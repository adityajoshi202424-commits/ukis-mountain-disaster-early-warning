"""NASA POWER hourly point observations.

NASA POWER is a real, keyless source for hourly precipitation and weather
history. Missing or unavailable values are returned as unavailable; this
adapter never estimates a replacement value.
"""

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

POWER_URL = "https://power.larc.nasa.gov/api/temporal/hourly/point"
POWER_VARIABLES = {
    "PRECTOTCORR": ("rainfall", "mm/hr"),
    "T2M": ("temperature", "°C"),
    "RH2M": ("humidity", "%"),
}


class NasaPowerProvider(DataProvider):
    """NASA POWER hourly point data, without an API key."""

    def __init__(self):
        self._client = httpx.AsyncClient(timeout=30.0)

    @property
    def name(self) -> str:
        return "NASA POWER"

    @property
    def source_url(self) -> str:
        return POWER_URL

    @property
    def requires_api_key(self) -> bool:
        return False

    async def check_status(self) -> ProviderStatus:
        try:
            response = await self._client.get(
                POWER_URL,
                params={
                    "parameters": "PRECTOTCORR",
                    "community": "AG",
                    "longitude": 78.0322,
                    "latitude": 30.3165,
                    "start": (datetime.now(timezone.utc) - timedelta(days=2)).strftime("%Y%m%d"),
                    "end": datetime.now(timezone.utc).strftime("%Y%m%d"),
                    "format": "JSON",
                    "time-standard": "UTC",
                },
            )
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
        start = start_time or fetched_at - timedelta(days=2)
        end = end_time or fetched_at
        try:
            response = await self._client.get(
                POWER_URL,
                params={
                    "parameters": ",".join(POWER_VARIABLES),
                    "community": "AG",
                    "longitude": longitude,
                    "latitude": latitude,
                    "start": start.strftime("%Y%m%d"),
                    "end": end.strftime("%Y%m%d"),
                    "format": "JSON",
                    "time-standard": "UTC",
                },
            )
            response.raise_for_status()
            observations = self._parse(response.json(), latitude, longitude, fetched_at)
            return ObservationBatch(
                provider_name=self.name,
                fetch_timestamp=fetched_at,
                status=ProviderStatus.AVAILABLE,
                observations=observations,
            )
        except httpx.TimeoutException:
            return self._unavailable(fetched_at, "NASA POWER request timed out")
        except httpx.ConnectError:
            return self._unavailable(fetched_at, "NASA POWER source is unreachable")
        except httpx.HTTPStatusError as error:
            return self._unavailable(fetched_at, f"NASA POWER returned HTTP {error.response.status_code}")
        except Exception as error:
            return ObservationBatch(
                provider_name=self.name,
                fetch_timestamp=fetched_at,
                status=ProviderStatus.ERROR,
                observations=[],
                error_message=f"NASA POWER provider error: {type(error).__name__}",
            )

    def _parse(self, data: dict, latitude: float, longitude: float, fetched_at: datetime) -> list[Observation]:
        parameters = data.get("properties", {}).get("parameter", {})
        observations: list[Observation] = []
        for source_variable, (variable, unit) in POWER_VARIABLES.items():
            for timestamp, raw_value in parameters.get(source_variable, {}).items():
                try:
                    observation_time = datetime.strptime(timestamp, "%Y%m%d%H").replace(tzinfo=timezone.utc)
                except ValueError:
                    continue
                value = None if raw_value in (-999, -999.0) else float(raw_value)
                observations.append(Observation(
                    variable=variable,
                    value=value,
                    unit=unit,
                    latitude=latitude,
                    longitude=longitude,
                    observation_time=observation_time,
                    provenance=DataProvenance(
                        source="NASA POWER",
                        source_url=POWER_URL,
                        provider="NasaPowerProvider",
                        dataset="POWER hourly point",
                        retrieved_at=fetched_at,
                        observation_time=observation_time,
                        spatial_resolution="point model grid",
                        temporal_resolution="hourly",
                        units=unit,
                        quality_status=QualityStatus.VALID if value is not None else QualityStatus.MISSING,
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
            if observation.value is not None and observation.variable == "rainfall" and observation.value < 0:
                observation.provenance.quality_status = QualityStatus.INVALID
        return batch

    def metadata(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "url": "https://power.larc.nasa.gov/",
            "license": "NASA public data terms",
            "requires_api_key": False,
            "coverage": "Global land points",
            "spatial_resolution": "model grid point",
            "temporal_resolution": "hourly",
            "update_frequency": "Near-real-time and historical archive",
            "limitations": ["Model/reanalysis product, not an in-situ gauge", "Point values represent a gridded estimate"],
        }

    async def close(self):
        await self._client.aclose()