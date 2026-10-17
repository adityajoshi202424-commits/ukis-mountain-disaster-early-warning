"""
Flash Flood Early Warning Platform — Provider Registry

Central registry of all data providers.
Manages lifecycle, health checks, and credential validation.
Never fabricates data from unregistered or unavailable providers.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

import structlog

from backend.config import settings
from backend.data.providers.base import (
    DataProvider,
    ObservationBatch,
    ProviderHealth,
    ProviderStatus,
)
from backend.data.providers.weather.open_meteo import OpenMeteoProvider
from backend.data.providers.infrastructure.osm import OSMInfrastructureProvider
from backend.data.providers.weather.nasa_power import NasaPowerProvider
from backend.data.providers.seismic.usgs import UsgsEarthquakeProvider
from backend.data.providers.hydrology.glofas import GloFASRiverDischargeProvider
from backend.data.providers.elevation.open_meteo import OpenMeteoElevationProvider

logger = structlog.get_logger(__name__)


class ProviderRegistry:
    """
    Central registry for all data providers.

    Responsibilities:
    - Initialize providers with credentials
    - Track health status
    - Route data requests to appropriate providers
    - Report unavailable providers honestly
    """

    def __init__(self):
        self._providers: dict[str, DataProvider] = {}
        self._health_cache: dict[str, ProviderHealth] = {}
        self._initialized = False

    async def initialize(self):
        """
        Register all providers. Check credentials.
        Providers without credentials are registered but marked API_KEY_REQUIRED.
        """
        if self._initialized:
            return

        # --- Tier 1: No API key required (real live public APIs) ---
        self._providers["open_meteo"] = OpenMeteoProvider()
        self._providers["nasa_power"] = NasaPowerProvider()
        self._providers["osm"] = OSMInfrastructureProvider()
        self._providers["usgs_earthquakes"] = UsgsEarthquakeProvider()
        self._providers["glofas_flood"] = GloFASRiverDischargeProvider()
        self._providers["open_meteo_elevation"] = OpenMeteoElevationProvider()

        # --- Tier 2: API key required ---
        # These are registered but will report API_KEY_REQUIRED if unconfigured.
        # Actual provider classes will be created in later phases.
        # For now, we honestly report their status.

        self._initialized = True

        logger.info(
            "provider_registry_initialized",
            registered_providers=list(self._providers.keys()),
            total=len(self._providers),
        )

    def get_provider(self, name: str) -> Optional[DataProvider]:
        """Get a registered provider by name. Returns None if not registered."""
        return self._providers.get(name)

    async def check_all_health(self) -> dict[str, ProviderHealth]:
        """Check health of all registered providers."""
        results: dict[str, ProviderHealth] = {}
        for name, provider in self._providers.items():
            try:
                health = await provider.health()
                results[name] = health
                self._health_cache[name] = health
            except Exception as e:
                logger.error("health_check_failed", provider=name, error=str(e))
                results[name] = ProviderHealth(
                    provider_name=name,
                    status=ProviderStatus.ERROR,
                    last_error=str(e),
                    last_error_time=datetime.now(timezone.utc),
                )
        return results

    async def get_health(self, provider_name: str) -> Optional[ProviderHealth]:
        """Get cached health for a specific provider."""
        if provider_name in self._health_cache:
            return self._health_cache[provider_name]
        provider = self.get_provider(provider_name)
        if provider:
            health = await provider.health()
            self._health_cache[provider_name] = health
            return health
        return None

    def list_providers(self) -> list[dict]:
        """List all registered providers with their metadata."""
        result = []
        for name, provider in self._providers.items():
            result.append({
                "name": name,
                "display_name": provider.name,
                "source_url": provider.source_url,
                "requires_api_key": provider.requires_api_key,
                "credentials_configured": settings.provider_has_credentials(name),
                "metadata": provider.metadata(),
            })
        return result

    def get_unavailable_providers(self) -> list[dict]:
        """
        List providers that need credentials but don't have them.
        Displayed in the UI as API_KEY_REQUIRED.
        """
        unavailable = []

        # Providers we know about but haven't implemented yet
        planned_providers = {
            "nasa_gpm": {
                "name": "NASA GPM IMERG",
                "purpose": "Satellite-observed rainfall",
                "credential": "NASA Earthdata Login (free)",
                "url": "https://urs.earthdata.nasa.gov/",
            },
            "imd": {
                "name": "India Meteorological Department",
                "purpose": "Official Indian weather observations",
                "credential": "IMD API key",
                "url": "https://api.imd.gov.in/",
            },
            "cwc": {
                "name": "Central Water Commission",
                "purpose": "Himalayan river discharge & stage observations (Alaknanda, Bhagirathi, Mandakini)",
                "credential": "CWC/NWDP access",
                "url": "https://nwdp.nwic.gov.in/",
            },
            "opentopography": {
                "name": "OpenTopography (SRTM)",
                "purpose": "Elevation/DEM data",
                "credential": "OpenTopography API key (free)",
                "url": "https://opentopography.org/",
            },
        }

        for provider_id, info in planned_providers.items():
            if not settings.provider_has_credentials(provider_id):
                unavailable.append({
                    "provider_id": provider_id,
                    **info,
                    "status": "API_KEY_REQUIRED",
                    "effect": f"{info['purpose']} will be unavailable until credentials are configured.",
                    "required_configuration": info["credential"],
                })

        return unavailable

    async def shutdown(self):
        """Gracefully close all provider connections."""
        for name, provider in self._providers.items():
            if hasattr(provider, "close"):
                await provider.close()
        logger.info("provider_registry_shutdown")


# Singleton
provider_registry = ProviderRegistry()
