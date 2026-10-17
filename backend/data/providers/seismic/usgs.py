"""USGS Earthquake GeoJSON provider for Himalayan seismic context."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import httpx

from backend.data.providers.base import (
    DataProvider,
    DataProvenance,
    Observation,
    ObservationBatch,
    ProviderStatus,
    QualityStatus,
)

USGS_QUERY_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"


class UsgsEarthquakeProvider(DataProvider):
    """Real-time global USGS earthquake events filtered to a local region."""

    def __init__(self):
        self._client = httpx.AsyncClient(timeout=30.0)

    @property
    def name(self) -> str:
        return "USGS Earthquake Hazards Program"

    @property
    def source_url(self) -> str:
        return USGS_QUERY_URL

    @property
    def requires_api_key(self) -> bool:
        return False

    async def check_status(self) -> ProviderStatus:
        try:
            response = await self._client.get(USGS_QUERY_URL, params={"format": "geojson", "limit": 1})
            return ProviderStatus.AVAILABLE if response.status_code == 200 else ProviderStatus.ERROR
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
        **kwargs: Any,
    ) -> ObservationBatch:
        fetched_at = datetime.now(timezone.utc)
        days_back = float(kwargs.get("days_back", 30))
        radius_degrees = float(kwargs.get("radius_degrees", 3.0))
        start = start_time or fetched_at - timedelta(days=days_back)
        end = end_time or fetched_at
        params = {
            "format": "geojson",
            "starttime": start.isoformat(),
            "endtime": end.isoformat(),
            "minmagnitude": float(kwargs.get("min_magnitude", 2.0)),
            "minlatitude": max(-90.0, latitude - radius_degrees),
            "maxlatitude": min(90.0, latitude + radius_degrees),
            "minlongitude": max(-180.0, longitude - radius_degrees),
            "maxlongitude": min(180.0, longitude + radius_degrees),
            "orderby": "time",
        }
        try:
            response = await self._client.get(USGS_QUERY_URL, params=params)
            response.raise_for_status()
            return ObservationBatch(
                provider_name=self.name,
                fetch_timestamp=fetched_at,
                status=ProviderStatus.AVAILABLE,
                observations=self._parse(response.json(), fetched_at),
            )
        except httpx.TimeoutException:
            return self._unavailable(fetched_at, "USGS earthquake feed timed out")
        except httpx.ConnectError:
            return self._unavailable(fetched_at, "USGS earthquake feed is unreachable")
        except httpx.HTTPStatusError as error:
            return self._unavailable(fetched_at, f"USGS returned HTTP {error.response.status_code}")
        except Exception as error:
            return ObservationBatch(
                provider_name=self.name,
                fetch_timestamp=fetched_at,
                status=ProviderStatus.ERROR,
                observations=[],
                error_message=f"USGS provider error: {type(error).__name__}",
            )

    def _parse(self, data: dict, fetched_at: datetime) -> list[Observation]:
        observations: list[Observation] = []
        for feature in data.get("features", []):
            geometry = feature.get("geometry", {})
            coordinates = geometry.get("coordinates", [])
            properties = feature.get("properties", {})
            if len(coordinates) < 2 or properties.get("mag") is None:
                continue
            observation_time = datetime.fromtimestamp(properties["time"] / 1000, tz=timezone.utc)
            observations.append(Observation(
                variable="earthquake_magnitude",
                value=float(properties["mag"]),
                unit="magnitude",
                latitude=float(coordinates[1]),
                longitude=float(coordinates[0]),
                observation_time=observation_time,
                provenance=DataProvenance(
                    source="USGS Earthquake Hazards Program",
                    source_url=properties.get("url", USGS_QUERY_URL),
                    provider="UsgsEarthquakeProvider",
                    dataset="USGS earthquake GeoJSON feed",
                    retrieved_at=fetched_at,
                    observation_time=observation_time,
                    spatial_resolution="event epicenter",
                    temporal_resolution="event-driven",
                    units="magnitude",
                    quality_status=QualityStatus.VALID,
                ),
            ))
        return observations

    def _unavailable(self, fetched_at: datetime, message: str) -> ObservationBatch:
        return ObservationBatch(
            provider_name=self.name,
            fetch_timestamp=fetched_at,
            status=ProviderStatus.OFFLINE,
            observations=[],
            error_message=message,
        )

    async def validate(self, batch: ObservationBatch) -> ObservationBatch:
        for observation in batch.observations:
            if observation.value is None or observation.value < -1 or observation.value > 10:
                observation.provenance.quality_status = QualityStatus.INVALID
        return batch

    def metadata(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "url": "https://earthquake.usgs.gov/",
            "license": "USGS public domain data",
            "requires_api_key": False,
            "coverage": "Global, filtered to requested Uttarakhand/Himalayan bounds",
            "spatial_resolution": "event epicenter",
            "temporal_resolution": "event-driven",
            "update_frequency": "Continuous feed",
            "limitations": ["USGS is a fallback live seismic feed, not India's authoritative NCS feed", "Magnitude and location are revised by USGS"],
        }

    async def close(self):
        await self._client.aclose()
# Legacy API-compatible USGS provider retained for existing hazard endpoints.

from typing import Optional, Dict, Any, List
from datetime import datetime, timezone, timedelta
import httpx
import structlog

logger = structlog.get_logger(__name__)

USGS_FEED_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"


class USGSEarthquakeProvider:
    """Provider for real-time seismic telemetry across Uttarakhand and the Central Himalayas."""

    @property
    def name(self) -> str:
        return "USGS Real-Time Earthquake Hazards Feed"

    @property
    def source_url(self) -> str:
        return USGS_FEED_URL

    async def get_recent_earthquakes(
        self,
        min_magnitude: float = 2.0,
        days_back: int = 30,
        lat_min: float = 28.5,
        lat_max: float = 31.5,
        lon_min: float = 77.5,
        lon_max: float = 81.5,
    ) -> Dict[str, Any]:
        """
        Query real earthquake events within the Uttarakhand bounding box.
        """
        start_time = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime("%Y-%m-%d")
        try:
            async with httpx.AsyncClient(timeout=25.0) as client:
                resp = await client.get(
                    USGS_FEED_URL,
                    params={
                        "format": "geojson",
                        "starttime": start_time,
                        "minmagnitude": min_magnitude,
                        "minlatitude": lat_min,
                        "maxlatitude": lat_max,
                        "minlongitude": lon_min,
                        "maxlongitude": lon_max,
                    },
                )
            if resp.status_code == 200:
                data = resp.json()
                features = data.get("features", [])
                events = []
                for f in features:
                    props = f.get("properties", {})
                    geom = f.get("geometry", {})
                    coords = geom.get("coordinates", [0, 0, 0])
                    time_ms = props.get("time")
                    event_dt = (
                        datetime.fromtimestamp(time_ms / 1000.0, tz=timezone.utc).isoformat()
                        if time_ms
                        else None
                    )
                    mag = props.get("mag")
                    events.append({
                        "event_id": f.get("id"),
                        "place": props.get("place"),
                        "magnitude": mag,
                        "time": event_dt,
                        "longitude": coords[0],
                        "latitude": coords[1],
                        "depth_km": coords[2],
                        "url": props.get("url"),
                        "significance": props.get("sig"),
                    })

                # Calculate regional Peak Ground Acceleration (PGA) hazard indicator
                max_mag = max([e["magnitude"] for e in events if e["magnitude"] is not None], default=0.0)
                seismic_status = "NORMAL"
                if max_mag >= 5.0:
                    seismic_status = "HIGH_SEISMIC_SLOPE_INSTABILITY"
                elif max_mag >= 4.0:
                    seismic_status = "MODERATE_SHAKING_ALERT"
                elif max_mag >= 3.0:
                    seismic_status = "MINOR_BACKGROUND_TREMOR"

                return {
                    "status": "ONLINE",
                    "provider": self.name,
                    "source_url": self.source_url,
                    "fetch_timestamp": datetime.now(timezone.utc).isoformat(),
                    "bounding_box": {
                        "lat_min": lat_min,
                        "lat_max": lat_max,
                        "lon_min": lon_min,
                        "lon_max": lon_max,
                    },
                    "count": len(events),
                    "seismic_status": seismic_status,
                    "max_magnitude": max_mag,
                    "events": events,
                }
            logger.warning("usgs_fetch_failed", status=resp.status_code)
            return {
                "status": "SOURCE_UNAVAILABLE",
                "provider": self.name,
                "error": f"Upstream API returned status code {resp.status_code}",
                "events": [],
            }
        except Exception as e:
            logger.error("usgs_request_error", error=str(e))
            return {
                "status": "OFFLINE",
                "provider": self.name,
                "error": str(e),
                "events": [],
            }

    async def close(self):
        await self._client.aclose()


usgs_seismic_provider = USGSEarthquakeProvider()
