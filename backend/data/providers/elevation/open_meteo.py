"""
Open-Meteo Elevation API Provider.

Fetches real SRTM & Copernicus 90m/30m Digital Elevation Model (DEM) data.
Real data source with zero fabricated values. Free for non-commercial use.
Source: https://open-meteo.com/en/docs/elevation-api
"""

from __future__ import annotations

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import httpx
import structlog

from backend.data.providers.base import (
    DataProvider,
    DataProvenance,
    Observation,
    ObservationBatch,
    ProviderStatus,
    QualityStatus,
)

logger = structlog.get_logger(__name__)

ELEVATION_URL = "https://api.open-meteo.com/v1/elevation"


class OpenMeteoElevationProvider(DataProvider):
    """Provider for real DEM elevations from Open-Meteo."""

    def __init__(self):
        self._client = httpx.AsyncClient(timeout=20.0)

    @property
    def name(self) -> str:
        return "Open-Meteo Elevation (SRTM/Copernicus DEM)"

    @property
    def source_url(self) -> str:
        return ELEVATION_URL

    @property
    def requires_api_key(self) -> bool:
        return False

    async def check_status(self) -> ProviderStatus:
        """Check if Open-Meteo Elevation API is reachable."""
        try:
            resp = await self._client.get(
                ELEVATION_URL,
                params={"latitude": 30.3165, "longitude": 78.0322},
            )
            if resp.status_code == 200:
                return ProviderStatus.AVAILABLE
            elif resp.status_code == 429:
                return ProviderStatus.RATE_LIMITED
            return ProviderStatus.ERROR
        except (httpx.ConnectError, httpx.TimeoutException):
            return ProviderStatus.OFFLINE
        except Exception as e:
            logger.error("elevation_status_check_failed", error=str(e))
            return ProviderStatus.ERROR

    async def fetch(
        self,
        latitude: float,
        longitude: float,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        **kwargs: Any,
    ) -> ObservationBatch:
        """Fetch elevation observation batch."""
        fetch_time = datetime.now(timezone.utc)
        elev = await self.get_elevation(latitude, longitude)
        obs: List[Observation] = []
        if elev is not None:
            obs.append(
                Observation(
                    variable="elevation",
                    value=float(elev),
                    unit="m",
                    latitude=latitude,
                    longitude=longitude,
                    observation_time=fetch_time,
                    provenance=DataProvenance(
                        source="Copernicus / SRTM DEM via Open-Meteo",
                        source_url=self.source_url,
                        provider=self.__class__.__name__,
                        dataset="srtm_copernicus_dem",
                        retrieved_at=fetch_time,
                        observation_time=fetch_time,
                        spatial_resolution="30m/90m",
                        temporal_resolution="static",
                        units="m",
                        quality_status=QualityStatus.VALID,
                    ),
                )
            )

        return ObservationBatch(
            provider_name=self.name,
            fetch_timestamp=fetch_time,
            status=ProviderStatus.AVAILABLE if elev is not None else ProviderStatus.ERROR,
            observations=obs,
        )

    async def validate(self, batch: ObservationBatch) -> ObservationBatch:
        """Validate elevation observations."""
        for obs in batch.observations:
            # Elevation in Uttarakhand ranges from ~200m (Haridwar) to ~7816m (Nanda Devi)
            if obs.value is not None and (obs.value < -100 or obs.value > 9000):
                obs.provenance.quality_status = QualityStatus.INVALID
        return batch

    def metadata(self) -> dict[str, Any]:
        """Provider metadata for transparency and documentation."""
        return {
            "name": self.name,
            "url": self.source_url,
            "license": "CC-BY 4.0 / Open Access",
            "requires_api_key": False,
            "coverage": "Global (90m SRTM / 30m Copernicus DEM)",
            "spatial_resolution": "30m/90m grid",
            "temporal_resolution": "Static digital elevation model",
            "update_frequency": "Periodic DEM reprocessing",
            "variables": ["elevation"],
            "limitations": [
                "Steep Himalayan gorges may have radar shadow artefacts in raw DEM",
                "Snowpack depth is not reflected in base rock DEM",
            ],
            "attribution": "NASA SRTM & Copernicus Digital Elevation Model via Open-Meteo",
        }

    async def get_elevation(self, latitude: float, longitude: float) -> Optional[float]:
        """Fetch real elevation in meters for a given coordinate."""
        try:
            resp = await self._client.get(
                ELEVATION_URL,
                params={"latitude": latitude, "longitude": longitude},
            )
            if resp.status_code == 200:
                data = resp.json()
                elevations = data.get("elevation")
                if isinstance(elevations, list) and len(elevations) > 0:
                    return float(elevations[0])
                elif isinstance(elevations, (int, float)):
                    return float(elevations)
            logger.warning("elevation_fetch_failed", status=resp.status_code, lat=latitude, lon=longitude)
            return None
        except Exception as e:
            logger.error("elevation_request_error", error=str(e), lat=latitude, lon=longitude)
            return None

    async def get_batch_elevations(self, coordinates: List[Dict[str, float]]) -> List[Optional[float]]:
        """Fetch real elevations for multiple coordinates in a single call."""
        if not coordinates:
            return []
        lats = ",".join(str(c["lat"]) for c in coordinates)
        lons = ",".join(str(c["lon"]) for c in coordinates)
        try:
            resp = await self._client.get(
                ELEVATION_URL,
                params={"latitude": lats, "longitude": lons},
            )
            if resp.status_code == 200:
                data = resp.json()
                elevations = data.get("elevation", [])
                return [float(e) if e is not None else None for e in elevations]
            return [None] * len(coordinates)
        except Exception as e:
            logger.error("batch_elevation_error", error=str(e))
            return [None] * len(coordinates)

    async def close(self):
        await self._client.aclose()


elevation_provider = OpenMeteoElevationProvider()
