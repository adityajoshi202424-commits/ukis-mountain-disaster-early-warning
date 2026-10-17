"""
Open-Meteo Flood / GloFAS River Discharge API Provider.

Fetches real Copernicus Global Flood Awareness System (GloFAS v4) river discharge data.
Real data source with zero fabricated values. Free for non-commercial use.
Source: https://open-meteo.com/en/docs/flood-api
License: CC-BY 4.0 / Copernicus Open Access
"""

from __future__ import annotations

from typing import Optional, Dict, Any, List
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

FLOOD_API_URL = "https://flood-api.open-meteo.com/v1/flood"


class GloFASRiverDischargeProvider(DataProvider):
    """Provider for real river discharge observations from GloFAS via Open-Meteo."""

    def __init__(self):
        self._client = httpx.AsyncClient(timeout=25.0)

    @property
    def name(self) -> str:
        return "Copernicus GloFAS v4 (via Open-Meteo Flood API)"

    @property
    def source_url(self) -> str:
        return FLOOD_API_URL

    @property
    def requires_api_key(self) -> bool:
        return False

    async def check_status(self) -> ProviderStatus:
        """Check if GloFAS Flood API is reachable."""
        try:
            resp = await self._client.get(
                FLOOD_API_URL,
                params={
                    "latitude": 30.5526,
                    "longitude": 79.5632,
                    "daily": "river_discharge",
                    "forecast_days": 1,
                },
            )
            if resp.status_code == 200:
                return ProviderStatus.AVAILABLE
            elif resp.status_code == 429:
                return ProviderStatus.RATE_LIMITED
            return ProviderStatus.ERROR
        except (httpx.ConnectError, httpx.TimeoutException):
            return ProviderStatus.OFFLINE
        except Exception as e:
            logger.error("glofas_status_check_failed", error=str(e))
            return ProviderStatus.ERROR

    async def fetch(
        self,
        latitude: float,
        longitude: float,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        **kwargs: Any,
    ) -> ObservationBatch:
        """Fetch river discharge observation batch."""
        fetch_time = datetime.now(timezone.utc)
        result = await self.get_discharge(latitude, longitude, forecast_days=kwargs.get("forecast_days", 7))
        if result.get("status") in ("OFFLINE", "SOURCE_UNAVAILABLE"):
            return ObservationBatch(
                provider_name=self.name,
                fetch_timestamp=fetch_time,
                status=ProviderStatus.ERROR,
                observations=[],
                error_message=result.get("error", "Upstream GloFAS error"),
            )

        current_val = result.get("current_discharge_cumecs")
        obs: List[Observation] = []
        if current_val is not None:
            obs.append(
                Observation(
                    variable="river_discharge",
                    value=float(current_val),
                    unit="m³/s",
                    latitude=latitude,
                    longitude=longitude,
                    observation_time=fetch_time,
                    provenance=DataProvenance(
                        source="Copernicus GloFAS",
                        source_url=self.source_url,
                        provider=self.__class__.__name__,
                        dataset="glofas_v4_daily",
                        retrieved_at=fetch_time,
                        observation_time=fetch_time,
                        spatial_resolution="0.05°",
                        temporal_resolution="daily",
                        units="m³/s",
                        quality_status=QualityStatus.VALID,
                    ),
                )
            )

        return ObservationBatch(
            provider_name=self.name,
            fetch_timestamp=fetch_time,
            status=ProviderStatus.AVAILABLE,
            observations=obs,
        )

    async def validate(self, batch: ObservationBatch) -> ObservationBatch:
        """Validate streamflow discharge observations."""
        for obs in batch.observations:
            if obs.value is not None and obs.value < 0:
                obs.provenance.quality_status = QualityStatus.INVALID
        return batch

    def metadata(self) -> dict[str, Any]:
        """Provider metadata for transparency and documentation."""
        return {
            "name": self.name,
            "url": self.source_url,
            "license": "CC-BY 4.0 / Copernicus Open Access",
            "requires_api_key": False,
            "coverage": "Global river basins (including Ganga, Alaknanda, Bhagirathi)",
            "spatial_resolution": "0.05° (~5km gridded river network)",
            "temporal_resolution": "Daily river discharge",
            "update_frequency": "Daily model runs (ECMWF GloFAS v4.0)",
            "variables": ["river_discharge", "river_discharge_mean", "river_discharge_max"],
            "limitations": [
                "Simulated gridded hydrology routed over DEM stream network",
                "Upstream gauge assimilation may have reporting delay",
            ],
            "attribution": "Copernicus Emergency Management Service — Global Flood Awareness System (GloFAS)",
        }

    async def get_discharge(
        self,
        latitude: float,
        longitude: float,
        forecast_days: int = 7,
    ) -> Dict[str, Any]:
        """
        Fetch real daily river discharge (m³/s) for a given coordinate.
        Returns actual GloFAS hydrological model output with full provenance.
        """
        try:
            resp = await self._client.get(
                FLOOD_API_URL,
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "daily": "river_discharge,river_discharge_mean,river_discharge_median,river_discharge_max,river_discharge_min",
                    "forecast_days": forecast_days,
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                daily = data.get("daily", {})
                times = daily.get("time", [])
                discharge = daily.get("river_discharge", [])
                discharge_max = daily.get("river_discharge_max", [])

                series = []
                for i in range(len(times)):
                    val = discharge[i] if i < len(discharge) else None
                    val_max = discharge_max[i] if i < len(discharge_max) else None
                    series.append({
                        "date": times[i],
                        "river_discharge_cumecs": val,
                        "river_discharge_max_cumecs": val_max,
                    })

                current_discharge = series[0]["river_discharge_cumecs"] if series else None
                peak_forecast = max(
                    [s["river_discharge_cumecs"] for s in series if s["river_discharge_cumecs"] is not None],
                    default=None,
                )

                return {
                    "status": "ONLINE",
                    "provider": self.name,
                    "source_url": self.source_url,
                    "fetch_timestamp": datetime.now(timezone.utc).isoformat(),
                    "latitude": latitude,
                    "longitude": longitude,
                    "current_discharge_cumecs": current_discharge,
                    "peak_forecast_cumecs": peak_forecast,
                    "daily_forecast": series,
                }
            logger.warning("glofas_fetch_failed", status=resp.status_code, lat=latitude, lon=longitude)
            return {
                "status": "SOURCE_UNAVAILABLE",
                "provider": self.name,
                "error": f"Upstream API returned status code {resp.status_code}",
                "latitude": latitude,
                "longitude": longitude,
                "current_discharge_cumecs": None,
                "daily_forecast": [],
            }
        except Exception as e:
            logger.error("glofas_request_error", error=str(e), lat=latitude, lon=longitude)
            return {
                "status": "OFFLINE",
                "provider": self.name,
                "error": str(e),
                "latitude": latitude,
                "longitude": longitude,
                "current_discharge_cumecs": None,
                "daily_forecast": [],
            }

    async def close(self):
        await self._client.aclose()


glofas_provider = GloFASRiverDischargeProvider()
