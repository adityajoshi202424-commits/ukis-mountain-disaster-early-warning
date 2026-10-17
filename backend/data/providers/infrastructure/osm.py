"""
Flash Flood Early Warning Platform — OpenStreetMap Infrastructure Provider

REAL DATA SOURCE. No API key required.

Source: https://www.openstreetmap.org/
Access: Overpass API (https://overpass-api.de/)
License: ODbL (Open Database License)
Coverage: Global (community-contributed)

Provides:
- Roads, bridges, hospitals, schools, rivers for impact assessment
- Real geographic coordinates and geometries
- NO fabricated infrastructure — returns actual OSM data
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

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

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Overpass QL queries for infrastructure types relevant to flood impact assessment
INFRASTRUCTURE_QUERIES = {
    "hospitals": '[out:json];(node["amenity"="hospital"]({bbox});way["amenity"="hospital"]({bbox}););out center;',
    "schools": '[out:json];(node["amenity"="school"]({bbox});way["amenity"="school"]({bbox}););out center;',
    "bridges": '[out:json];(way["bridge"="yes"]({bbox}););out center;',
    "roads_primary": '[out:json];(way["highway"~"primary|secondary|trunk|motorway"]({bbox}););out center;',
    "rivers": '[out:json];(way["waterway"~"river|stream"]({bbox});relation["waterway"="river"]({bbox}););out center;',
    "villages": '[out:json];(node["place"~"village|hamlet|town"]({bbox}););out center;',
    "police_stations": '[out:json];(node["amenity"="police"]({bbox});way["amenity"="police"]({bbox}););out center;',
    "fire_stations": '[out:json];(node["amenity"="fire_station"]({bbox});way["amenity"="fire_station"]({bbox}););out center;',
}


class OSMInfrastructureProvider(DataProvider):
    """
    OpenStreetMap infrastructure data provider via Overpass API.

    No API key required. Returns real geographic features.
    Used for impact assessment: which infrastructure is in a risk zone.
    """

    def __init__(self):
        self._client = httpx.AsyncClient(timeout=60.0)  # Overpass can be slow
        self._last_successful_fetch: Optional[datetime] = None

    @property
    def name(self) -> str:
        return "OpenStreetMap"

    @property
    def source_url(self) -> str:
        return "https://overpass-api.de/api/interpreter"

    @property
    def requires_api_key(self) -> bool:
        return False

    async def check_status(self) -> ProviderStatus:
        """Check if Overpass API is reachable."""
        try:
            # Simple status check query
            response = await self._client.get(
                "https://overpass-api.de/api/status"
            )
            if response.status_code == 200:
                # Check if rate limited
                text = response.text
                if "rate_limited" in text.lower() or "slot available after" in text.lower():
                    return ProviderStatus.RATE_LIMITED
                return ProviderStatus.AVAILABLE
            return ProviderStatus.ERROR
        except (httpx.ConnectError, httpx.TimeoutException):
            return ProviderStatus.OFFLINE
        except Exception:
            return ProviderStatus.ERROR

    async def fetch(
        self,
        latitude: float,
        longitude: float,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        radius_km: float = 25.0,
        infrastructure_type: str = "hospitals",
        **kwargs: Any,
    ) -> ObservationBatch:
        """
        Fetch real infrastructure features from OSM within a bounding box.

        Parameters:
            latitude, longitude: Center point
            radius_km: Search radius in kilometers
            infrastructure_type: One of INFRASTRUCTURE_QUERIES keys
        """
        fetch_timestamp = datetime.now(timezone.utc)

        if infrastructure_type not in INFRASTRUCTURE_QUERIES:
            return ObservationBatch(
                provider_name=self.name,
                fetch_timestamp=fetch_timestamp,
                status=ProviderStatus.ERROR,
                observations=[],
                error_message=f"Unknown infrastructure type: {infrastructure_type}. "
                f"Valid types: {list(INFRASTRUCTURE_QUERIES.keys())}",
            )

        # Calculate bounding box from center + radius
        # ~0.009° per km at Uttarakhand latitudes (~30°N)
        delta_lat = radius_km * 0.009
        delta_lon = radius_km * 0.0104  # Adjusted for Uttarakhand latitude (~30°N)
        bbox = f"{latitude - delta_lat},{longitude - delta_lon},{latitude + delta_lat},{longitude + delta_lon}"

        query = INFRASTRUCTURE_QUERIES[infrastructure_type].format(bbox=bbox)

        try:
            response = await self._client.post(
                OVERPASS_URL,
                data={"data": query},
            )
            response.raise_for_status()
            data = response.json()

            observations = self._parse_elements(
                data.get("elements", []),
                infrastructure_type,
                fetch_timestamp,
            )

            self._last_successful_fetch = fetch_timestamp

            logger.info(
                "osm_fetch_complete",
                infrastructure_type=infrastructure_type,
                center_lat=latitude,
                center_lon=longitude,
                radius_km=radius_km,
                features_found=len(observations),
            )

            return ObservationBatch(
                provider_name=self.name,
                fetch_timestamp=fetch_timestamp,
                status=ProviderStatus.AVAILABLE,
                observations=observations,
            )

        except httpx.TimeoutException:
            logger.warning("osm_timeout", infrastructure_type=infrastructure_type)
            return ObservationBatch(
                provider_name=self.name,
                fetch_timestamp=fetch_timestamp,
                status=ProviderStatus.OFFLINE,
                observations=[],
                error_message="Overpass API timed out. Try a smaller area.",
            )

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                return ObservationBatch(
                    provider_name=self.name,
                    fetch_timestamp=fetch_timestamp,
                    status=ProviderStatus.RATE_LIMITED,
                    observations=[],
                    error_message="Overpass API rate limit reached. Retry later.",
                )
            return ObservationBatch(
                provider_name=self.name,
                fetch_timestamp=fetch_timestamp,
                status=ProviderStatus.ERROR,
                observations=[],
                error_message=f"Overpass API error: HTTP {e.response.status_code}",
            )

        except Exception as e:
            logger.error("osm_fetch_error", error=str(e))
            return ObservationBatch(
                provider_name=self.name,
                fetch_timestamp=fetch_timestamp,
                status=ProviderStatus.ERROR,
                observations=[],
                error_message=f"Provider error: {type(e).__name__}",
            )

    def _parse_elements(
        self,
        elements: list[dict],
        infrastructure_type: str,
        fetch_timestamp: datetime,
    ) -> list[Observation]:
        """Parse Overpass API elements into Observations with provenance."""
        observations: list[Observation] = []

        for element in elements:
            # Get coordinates — nodes have lat/lon, ways/relations have center
            lat = element.get("lat") or element.get("center", {}).get("lat")
            lon = element.get("lon") or element.get("center", {}).get("lon")

            if lat is None or lon is None:
                continue

            tags = element.get("tags", {})
            name = tags.get("name", tags.get("name:en", "Unnamed"))

            provenance = DataProvenance(
                source="OpenStreetMap",
                source_url=f"https://www.openstreetmap.org/{element.get('type', 'node')}/{element.get('id', '')}",
                provider="OSMInfrastructureProvider",
                dataset=f"osm-{infrastructure_type}",
                retrieved_at=fetch_timestamp,
                observation_time=fetch_timestamp,  # OSM is current state
                spatial_resolution="vector (exact geometry)",
                temporal_resolution="static (community-updated)",
                units=None,
                quality_status=QualityStatus.VALID,
                processing_version="1.0.0",
            )

            observations.append(
                Observation(
                    variable=f"infrastructure_{infrastructure_type}",
                    value=1.0,  # Presence indicator
                    unit="count",
                    latitude=float(lat),
                    longitude=float(lon),
                    observation_time=fetch_timestamp,
                    provenance=provenance,
                )
            )

        return observations

    async def fetch_all_infrastructure(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 25.0,
    ) -> dict[str, ObservationBatch]:
        """
        Fetch all infrastructure types for a location.
        Returns a dict of infrastructure_type → ObservationBatch.
        """
        results: dict[str, ObservationBatch] = {}
        for infra_type in INFRASTRUCTURE_QUERIES:
            results[infra_type] = await self.fetch(
                latitude=latitude,
                longitude=longitude,
                radius_km=radius_km,
                infrastructure_type=infra_type,
            )
        return results

    async def validate(self, batch: ObservationBatch) -> ObservationBatch:
        """OSM-specific validation. Coordinates from OSM are generally reliable."""
        for obs in batch.observations:
            # Sanity check coordinates
            if not (-90 <= obs.latitude <= 90) or not (-180 <= obs.longitude <= 180):
                obs.provenance.quality_status = QualityStatus.INVALID
        return batch

    def metadata(self) -> dict[str, Any]:
        return {
            "name": "OpenStreetMap",
            "url": "https://www.openstreetmap.org/",
            "api": "Overpass API (https://overpass-api.de/)",
            "license": "ODbL (Open Database License)",
            "requires_api_key": False,
            "coverage": "Global (community-contributed)",
            "spatial_resolution": "Vector (exact positions/geometries)",
            "update_frequency": "Continuous (community edits)",
            "infrastructure_types": list(INFRASTRUCTURE_QUERIES.keys()),
            "limitations": [
                "Coverage depends on community contributions — may be incomplete in rural areas",
                "Overpass API has rate limits (no explicit quota, but throttled under load)",
                "Data quality varies by region — Uttarakhand urban areas well-mapped, remote high-altitude trails less so",
                "No official validation — community-contributed data",
            ],
            "attribution": "© OpenStreetMap contributors. Data available under ODbL.",
        }

    async def close(self):
        await self._client.aclose()
