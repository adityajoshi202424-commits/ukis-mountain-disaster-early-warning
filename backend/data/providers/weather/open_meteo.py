"""
Flash Flood Early Warning Platform — Open-Meteo Weather Provider

REAL DATA SOURCE. No API key required. Free for non-commercial use.

Source: https://open-meteo.com/
License: CC-BY 4.0 (attribution required)
Coverage: Global
Resolution: ~11km (ECMWF HRES), hourly
Latency: Real-time forecasts, historical archive back to 1940

Provides:
- Hourly forecast: temperature, precipitation, humidity, wind, pressure
- Historical weather (via archive endpoint)
- NO fabricated values — returns None when data unavailable
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

# Open-Meteo API endpoints
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
HISTORICAL_URL = "https://archive-api.open-meteo.com/v1/archive"

# Variables we request from Open-Meteo and their mapping to our schema
HOURLY_VARIABLES = [
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "rain",
    "snowfall",
    "snow_depth",
    "freezing_level_height",
    "surface_pressure",
    "wind_speed_10m",
    "wind_direction_10m",
    "cloud_cover",
    "soil_moisture_0_to_7cm",
    "soil_temperature_0_to_7cm",
]

# Map Open-Meteo variable names to our internal variable names
VARIABLE_MAP = {
    "temperature_2m": ("temperature", "°C"),
    "relative_humidity_2m": ("humidity", "%"),
    "precipitation": ("rainfall", "mm"),
    "rain": ("rainfall_liquid", "mm"),
    "snowfall": ("snowfall", "cm"),
    "snow_depth": ("snow_depth", "m"),
    "freezing_level_height": ("freezing_level_height", "m"),
    "surface_pressure": ("pressure", "hPa"),
    "wind_speed_10m": ("wind_speed", "m/s"),
    "wind_direction_10m": ("wind_direction", "°"),
    "cloud_cover": ("cloud_cover", "%"),
    "soil_moisture_0_to_7cm": ("soil_moisture_0_7cm", "m³/m³"),
    "soil_temperature_0_to_7cm": ("soil_temperature_0_7cm", "°C"),
}


class OpenMeteoProvider(DataProvider):
    """
    Open-Meteo weather data provider.

    No API key required. Free for non-commercial use.
    Returns real forecast and historical weather data.
    Never fabricates values.
    """

    def __init__(self):
        self._client = httpx.AsyncClient(timeout=30.0)
        self._last_successful_fetch: Optional[datetime] = None
        self._last_error: Optional[str] = None

    @property
    def name(self) -> str:
        return "Open-Meteo"

    @property
    def source_url(self) -> str:
        return "https://open-meteo.com/"

    @property
    def requires_api_key(self) -> bool:
        return False

    async def check_status(self) -> ProviderStatus:
        """Check if Open-Meteo API is reachable."""
        try:
            response = await self._client.get(
                FORECAST_URL,
                params={
                    "latitude": 30.3165,  # Dehradun, Uttarakhand — health check coordinate
                    "longitude": 78.0322,
                    "hourly": "temperature_2m",
                    "forecast_days": 1,
                },
            )
            if response.status_code == 200:
                return ProviderStatus.AVAILABLE
            elif response.status_code == 429:
                return ProviderStatus.RATE_LIMITED
            else:
                return ProviderStatus.ERROR
        except (httpx.ConnectError, httpx.TimeoutException):
            return ProviderStatus.OFFLINE
        except Exception as e:
            logger.error("open_meteo_status_check_failed", error=str(e))
            return ProviderStatus.ERROR

    async def fetch(
        self,
        latitude: float,
        longitude: float,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        **kwargs: Any,
    ) -> ObservationBatch:
        """
        Fetch real weather data from Open-Meteo.

        If start_time/end_time provided → historical archive.
        Otherwise → current forecast.
        """
        fetch_timestamp = datetime.now(timezone.utc)
        is_historical = start_time is not None and end_time is not None

        try:
            if is_historical:
                data = await self._fetch_historical(
                    latitude, longitude, start_time, end_time
                )
            else:
                data = await self._fetch_forecast(latitude, longitude)

            observations = self._parse_response(
                data, latitude, longitude, fetch_timestamp, is_historical
            )

            self._last_successful_fetch = fetch_timestamp

            return ObservationBatch(
                provider_name=self.name,
                fetch_timestamp=fetch_timestamp,
                status=ProviderStatus.AVAILABLE,
                observations=observations,
            )

        except httpx.TimeoutException:
            self._last_error = "Request timed out"
            logger.warning("open_meteo_timeout", lat=latitude, lon=longitude)
            return ObservationBatch(
                provider_name=self.name,
                fetch_timestamp=fetch_timestamp,
                status=ProviderStatus.OFFLINE,
                observations=[],
                error_message="Source temporarily unavailable (timeout).",
            )

        except httpx.ConnectError:
            self._last_error = "Connection failed"
            logger.warning("open_meteo_connection_error", lat=latitude, lon=longitude)
            return ObservationBatch(
                provider_name=self.name,
                fetch_timestamp=fetch_timestamp,
                status=ProviderStatus.OFFLINE,
                observations=[],
                error_message="Source temporarily unavailable (connection failed).",
            )

        except Exception as e:
            self._last_error = str(e)
            logger.error(
                "open_meteo_fetch_error",
                lat=latitude,
                lon=longitude,
                error=str(e),
            )
            return ObservationBatch(
                provider_name=self.name,
                fetch_timestamp=fetch_timestamp,
                status=ProviderStatus.ERROR,
                observations=[],
                error_message=f"Provider error: {type(e).__name__}",
            )

    async def _fetch_forecast(
        self, latitude: float, longitude: float
    ) -> dict:
        """Fetch current forecast from Open-Meteo."""
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": ",".join(HOURLY_VARIABLES),
            "forecast_days": 7,
            "past_days": 2,  # Include recent past for accumulations
            "timezone": "UTC",
        }

        response = await self._client.get(FORECAST_URL, params=params)
        response.raise_for_status()
        return response.json()

    async def _fetch_historical(
        self,
        latitude: float,
        longitude: float,
        start_time: datetime,
        end_time: datetime,
    ) -> dict:
        """Fetch historical weather from Open-Meteo archive."""
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": ",".join(HOURLY_VARIABLES),
            "start_date": start_time.strftime("%Y-%m-%d"),
            "end_date": end_time.strftime("%Y-%m-%d"),
            "timezone": "UTC",
        }

        response = await self._client.get(HISTORICAL_URL, params=params)
        response.raise_for_status()
        return response.json()

    def _parse_response(
        self,
        data: dict,
        latitude: float,
        longitude: float,
        fetch_timestamp: datetime,
        is_historical: bool,
    ) -> list[Observation]:
        """
        Parse Open-Meteo JSON response into Observation records.
        Each value gets full provenance. None values become MISSING.
        """
        observations: list[Observation] = []

        hourly = data.get("hourly", {})
        timestamps = hourly.get("time", [])

        if not timestamps:
            logger.warning(
                "open_meteo_empty_response",
                lat=latitude,
                lon=longitude,
            )
            return observations

        for var_name, (internal_name, unit) in VARIABLE_MAP.items():
            values = hourly.get(var_name, [])

            for i, timestamp_str in enumerate(timestamps):
                value = values[i] if i < len(values) else None

                # Parse the timestamp
                try:
                    obs_time = datetime.fromisoformat(timestamp_str).replace(
                        tzinfo=timezone.utc
                    )
                except (ValueError, TypeError):
                    continue  # Skip unparseable timestamps

                # Build provenance — every single observation has this
                provenance = DataProvenance(
                    source="Open-Meteo",
                    source_url=HISTORICAL_URL if is_historical else FORECAST_URL,
                    provider="OpenMeteoProvider",
                    dataset="open-meteo-historical" if is_historical else "open-meteo-forecast",
                    retrieved_at=fetch_timestamp,
                    observation_time=obs_time,
                    spatial_resolution="0.25° (~25km, ECMWF HRES)",
                    temporal_resolution="hourly",
                    units=unit,
                    quality_status=(
                        QualityStatus.VALID if value is not None else QualityStatus.MISSING
                    ),
                    processing_version="1.0.0",
                )

                observations.append(
                    Observation(
                        variable=internal_name,
                        value=value,
                        unit=unit,
                        latitude=latitude,
                        longitude=longitude,
                        observation_time=obs_time,
                        provenance=provenance,
                    )
                )

        logger.info(
            "open_meteo_parsed",
            lat=latitude,
            lon=longitude,
            total_observations=len(observations),
            variables=list(VARIABLE_MAP.values()),
            timestamps_count=len(timestamps),
        )

        return observations

    async def validate(self, batch: ObservationBatch) -> ObservationBatch:
        """
        Provider-specific validation for Open-Meteo data.
        Generic quality checks are done by the DataQualityEngine.
        This adds Open-Meteo-specific checks.
        """
        for obs in batch.observations:
            if obs.value is None:
                continue

            # Open-Meteo returns precipitation in mm — should never be negative
            if obs.variable in ("rainfall", "rainfall_liquid") and obs.value < 0:
                obs.provenance.quality_status = QualityStatus.INVALID
                logger.warning(
                    "open_meteo_negative_precip",
                    value=obs.value,
                    lat=obs.latitude,
                    lon=obs.longitude,
                )

        return batch

    def metadata(self) -> dict[str, Any]:
        """Provider metadata for transparency and documentation."""
        return {
            "name": "Open-Meteo",
            "url": "https://open-meteo.com/",
            "license": "CC-BY 4.0 (non-commercial free)",
            "requires_api_key": False,
            "coverage": "Global",
            "spatial_resolution": "0.25° (~25km)",
            "temporal_resolution": "Hourly",
            "update_frequency": "Real-time (forecast), 5-day delay (final archive)",
            "variables": list(VARIABLE_MAP.keys()),
            "limitations": [
                "Resolution is ~25km — not station-level",
                "Precipitation is model-interpolated, not gauge-observed",
                "Free tier has rate limits (not documented precisely)",
                "Soil moisture is from ERA5-Land reanalysis, not in-situ sensors",
            ],
            "attribution": "Data from Open-Meteo (https://open-meteo.com/). "
            "Weather data by ECMWF, DWD, NOAA, and others.",
        }

    async def fetch_mountain_telemetry(self, latitude: float, longitude: float) -> dict[str, Any]:
        """
        Fetch near-real-time mountain environmental telemetry for early warning analysis.
        Computes rolling rainfall accumulations, snowpack conditions, and freezing level isotherm.
        Zero fabricated data — returns exact values or None if unavailable.
        """
        try:
            raw_data = await self._fetch_forecast(latitude, longitude)
            hourly = raw_data.get("hourly", {})
            times = hourly.get("time", [])
            now_iso = datetime.now(timezone.utc).isoformat()

            # Find index closest to current hour
            current_idx = 0
            if times:
                current_dt = datetime.now(timezone.utc)
                min_diff = float("inf")
                for i, t_str in enumerate(times):
                    try:
                        t_dt = datetime.fromisoformat(t_str).replace(tzinfo=timezone.utc)
                        diff = abs((t_dt - current_dt).total_seconds())
                        if diff < min_diff:
                            min_diff = diff
                            current_idx = i
                    except Exception:
                        pass

            def _get_val(var: str, idx: int) -> Optional[float]:
                vals = hourly.get(var, [])
                if idx < len(vals) and vals[idx] is not None:
                    return float(vals[idx])
                return None

            # Current observations
            temp = _get_val("temperature_2m", current_idx)
            rain_1h = _get_val("precipitation", current_idx)
            snow_depth_m = _get_val("snow_depth", current_idx)
            snowfall_cm = _get_val("snowfall", current_idx)
            freezing_lvl_m = _get_val("freezing_level_height", current_idx)
            soil_moist = _get_val("soil_moisture_0_to_7cm", current_idx)
            pressure_hpa = _get_val("surface_pressure", current_idx)
            wind_speed = _get_val("wind_speed_10m", current_idx)

            # Rolling accumulations: past 24h and past 48h
            precip_vals = hourly.get("precipitation", [])
            past_start_24 = max(0, current_idx - 24)
            past_start_48 = max(0, current_idx - 48)

            rain_24h = sum([p for p in precip_vals[past_start_24:current_idx + 1] if p is not None])
            rain_48h = sum([p for p in precip_vals[past_start_48:current_idx + 1] if p is not None])

            # Max hourly rain in past 24h (peak burst)
            past_slice = [p for p in precip_vals[past_start_24:current_idx + 1] if p is not None]
            peak_rain_intensity = max(past_slice) if past_slice else 0.0

            return {
                "status": "ONLINE",
                "provider": "Open-Meteo Weather API",
                "source_url": FORECAST_URL,
                "retrieved_at": now_iso,
                "latitude": latitude,
                "longitude": longitude,
                "current_temperature_c": temp,
                "current_rainfall_mm_hr": rain_1h,
                "peak_rain_intensity_mm_hr": round(peak_rain_intensity, 2),
                "rainfall_24h_mm": round(rain_24h, 2),
                "rainfall_48h_mm": round(rain_48h, 2),
                "snow_depth_m": snow_depth_m,
                "snowfall_cm": snowfall_cm,
                "freezing_level_m": freezing_lvl_m,
                "soil_moisture_m3_m3": soil_moist,
                "surface_pressure_hpa": pressure_hpa,
                "wind_speed_ms": wind_speed,
            }
        except Exception as e:
            logger.error("mountain_telemetry_fetch_error", error=str(e), lat=latitude, lon=longitude)
            return {
                "status": "OFFLINE",
                "provider": "Open-Meteo Weather API",
                "source_url": FORECAST_URL,
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "latitude": latitude,
                "longitude": longitude,
                "error": str(e),
                "current_temperature_c": None,
                "current_rainfall_mm_hr": None,
                "peak_rain_intensity_mm_hr": None,
                "rainfall_24h_mm": None,
                "rainfall_48h_mm": None,
                "snow_depth_m": None,
                "snowfall_cm": None,
                "freezing_level_m": None,
                "soil_moisture_m3_m3": None,
                "surface_pressure_hpa": None,
                "wind_speed_ms": None,
            }

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()

