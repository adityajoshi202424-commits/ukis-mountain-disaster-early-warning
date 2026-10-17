"""
UKIS Environmental Configuration Validator & Orchestration
Enforces strict runtime validation on application startup.
Crashes early if critical regional bounds, Indian government API endpoints,
or emergency helpline numbers are missing or violated.
"""

from __future__ import annotations

import os
import structlog
from pathlib import Path
from typing import List, Tuple, Optional, Dict
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv

logger = structlog.get_logger("env_validator")

# Auto-detect and load environmental file
app_env = os.getenv("APP_ENV", os.getenv("ENVIRONMENT", "local")).lower()
base_dir = Path(__file__).resolve().parent.parent.parent
env_file = base_dir / f".env.{app_env}"

if env_file.exists():
    load_dotenv(dotenv_path=env_file, override=False)
else:
    load_dotenv(dotenv_path=base_dir / ".env", override=False)


class EnvironmentValidationError(Exception):
    """Raised when critical production disaster settings are missing or malformed."""
    pass


class SpatialBoundaryViolationError(EnvironmentValidationError):
    """Raised when spatial coordinates or bounding envelope violate Uttarakhand state limits."""
    pass


class MissingCredentialError(EnvironmentValidationError):
    """Raised when a feed or gateway marked required: true is missing authentic credentials/endpoint."""
    pass


# Strict Uttarakhand Territorial Limits (Survey of India / ISRO Bhuvan)
UTTARAKHAND_BOUNDS = {
    "min_lat": 28.7161,
    "max_lat": 31.4558,
    "min_lon": 77.5757,
    "max_lon": 81.0475,
}
UTTARAKHAND_BBOX = UTTARAKHAND_BOUNDS


class IndianRegionalEnvironment(BaseModel):
    # App Mode
    app_env: str = Field(default="local")
    app_debug: bool = Field(default=False)
    port: int = Field(default=8080)
    timezone: str = Field(default="Asia/Kolkata")

    # Regional Bounds (Uttarakhand Devbhoomi)
    default_country_code: str = Field(default="IN")
    default_state: str = Field(default="Uttarakhand")
    default_state_bounding_box: str = Field(
        default="77.5757,28.7161,81.0475,31.4558",
        description="min_lon,min_lat,max_lon,max_lat",
    )
    default_map_center_lat: float = Field(default=30.3165)
    default_map_center_lon: float = Field(default=78.0322)
    default_map_zoom: int = Field(default=8)

    # Spatial Coordinates Bounds (Uttarakhand Spatial Grid Boundaries)
    uttarakhand_min_lat: float = Field(default=28.7161)
    uttarakhand_max_lat: float = Field(default=31.4558)
    uttarakhand_min_lon: float = Field(default=77.5757)
    uttarakhand_max_lon: float = Field(default=81.0475)

    # Telemetry Feed Gateways (Gated on real institutional access)
    ndma_cap_feed_url: Optional[str] = Field(default=None)
    imd_uttarakhand_warn_url: Optional[str] = Field(default=None)
    cwc_river_gauge_stream: Optional[str] = Field(default=None)
    iitr_earthquake_ws: Optional[str] = Field(default=None)

    # Telemetry API Keys / Auth Tokens
    ndma_cap_api_key: Optional[str] = Field(default=None)
    cwc_gauge_api_key: Optional[str] = Field(default=None)
    iitr_eew_auth_token: Optional[str] = Field(default=None)

    # Legacy Aliases
    ndma_cap_gateway_url: Optional[str] = Field(default=None)
    imd_weather_alerts_endpoint: Optional[str] = Field(default=None)
    imd_mausam_warn_uri: Optional[str] = Field(default=None)
    cwc_hydrology_endpoint: Optional[str] = Field(default=None)
    cwc_hydrology_feed: Optional[str] = Field(default=None)
    ncs_seismic_feed_url: Optional[str] = Field(default=None)
    iitr_eew_seismic_ws: Optional[str] = Field(default=None)
    seoc_uttarakhand_feed: Optional[str] = Field(default=None)
    isro_bhuvan_geoportal_tile_uri: Optional[str] = Field(default=None)
    isro_bhuvan_wms_server: Optional[str] = Field(default=None)

    # Secondary Verified Public Telemetry Endpoints
    open_meteo_weather_api: Optional[str] = Field(default="https://api.open-meteo.com/v1/forecast")
    open_meteo_flood_api: Optional[str] = Field(default="https://flood-api.open-meteo.com/v1/flood")
    open_meteo_elevation_api: Optional[str] = Field(default="https://api.open-meteo.com/v1/elevation")
    usgs_seismic_feed_url: Optional[str] = Field(default="https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson")

    # Multi-Channel Alert Gateway Routes
    cdot_cell_broadcast_proxy: Optional[str] = Field(default=None)
    nic_sms_gateway_url: Optional[str] = Field(default=None)
    nic_sms_api_key: Optional[str] = Field(default=None)
    nic_sms_auth_token: Optional[str] = Field(default=None)
    nic_ivr_gateway_url: Optional[str] = Field(default=None)
    nic_ivr_api_key: Optional[str] = Field(default=None)
    whatsapp_business_api_url: Optional[str] = Field(default=None)
    whatsapp_business_api_key: Optional[str] = Field(default=None)
    fcm_server_key: Optional[str] = Field(default=None)
    ndma_sachet_feed_url: Optional[str] = Field(default=None)

    # Admin & Traffic Rate Limiting
    admin_dashboard_jwt_secret: Optional[str] = Field(default="DMMC_SECURE_JWT_SECRET_KEY_2026")
    public_api_rate_limit_per_min: int = Field(default=60)

    # Indian Emergency Telephony & Alert Protocols
    national_emergency_line: str = Field(default="112")
    state_disaster_helpline: str = Field(default="1070")
    district_disaster_helpline: str = Field(default="1077")
    ambulance_helpline: str = Field(default="108")
    cdac_cell_broadcast_receiver_id: str = Field(default="IN_CAP_001")

    # Cache, Resiliency & Active-Active Distributed Failover Settings
    cache_ttl_seconds: int = Field(default=300)
    emergency_cache_bypass: bool = Field(default=True)
    upstream_http_timeout_seconds: float = Field(default=15.0)
    max_retry_attempts: int = Field(default=3)
    failover_edge_enabled: bool = Field(default=True)
    failover_primary_region: str = Field(default="ap-south-1")
    failover_secondary_region: str = Field(default="ap-south-2")

    @field_validator("uttarakhand_min_lat", "uttarakhand_max_lat")
    @classmethod
    def validate_uttarakhand_latitudes(cls, v: float) -> float:
        # Check strict Uttarakhand latitude range (28.7161 to 31.4558)
        # Allow tiny epsilon for floating point representation
        if v < 28.70 or v > 31.50:
            raise SpatialBoundaryViolationError(
                f"Latitude {v:.4f}°N violates Uttarakhand state spatial envelope "
                f"[{UTTARAKHAND_BOUNDS['min_lat']}°N - {UTTARAKHAND_BOUNDS['max_lat']}°N]."
            )
        return v

    @field_validator("uttarakhand_min_lon", "uttarakhand_max_lon")
    @classmethod
    def validate_uttarakhand_longitudes(cls, v: float) -> float:
        # Check strict Uttarakhand longitude range (77.5757 to 81.0475)
        if v < 77.50 or v > 81.10:
            raise SpatialBoundaryViolationError(
                f"Longitude {v:.4f}°E violates Uttarakhand state spatial envelope "
                f"[{UTTARAKHAND_BOUNDS['min_lon']}°E - {UTTARAKHAND_BOUNDS['max_lon']}°E]."
            )
        return v

    @field_validator("default_state_bounding_box")
    @classmethod
    def validate_bounding_box(cls, v: str) -> str:
        parts = [p.strip() for p in v.split(",")]
        if len(parts) != 4:
            raise ValueError("Bounding box must contain exactly 4 comma-separated coordinates: min_lon,min_lat,max_lon,max_lat")
        try:
            min_lon, min_lat, max_lon, max_lat = map(float, parts)
            if min_lon >= max_lon or min_lat >= max_lat:
                raise ValueError("min_lon must be < max_lon and min_lat must be < max_lat.")
            if min_lat < 28.70 or max_lat > 31.50 or min_lon < 77.50 or max_lon > 81.10:
                raise SpatialBoundaryViolationError(
                    f"Bounding box [{v}] violates Uttarakhand territorial boundaries."
                )
        except ValueError as ex:
            raise ValueError(f"Invalid bounding box coordinate format: {ex}") from ex
        return v

    def get_bounding_box_coords(self) -> Tuple[float, float, float, float]:
        """Returns (min_lon, min_lat, max_lon, max_lat) as floats."""
        parts = [float(p.strip()) for p in self.default_state_bounding_box.split(",")]
        return parts[0], parts[1], parts[2], parts[3]

    def is_coordinate_in_state(self, lat: float, lon: float) -> bool:
        """Checks if a point falls within the Uttarakhand state bounding envelope."""
        min_lon, min_lat, max_lon, max_lat = self.get_bounding_box_coords()
        return (min_lat <= lat <= max_lat) and (min_lon <= lon <= max_lon)

    def validate_feed(self, feed_name: str, endpoint: Optional[str], api_key: Optional[str] = None, required: bool = False) -> bool:
        """
        Validates whether a feed is properly configured.
        If required=True and missing credentials/endpoint, raises MissingCredentialError.
        If required=False and missing, returns False (fails closed gracefully).
        """
        is_configured = bool(endpoint and endpoint.strip())
        if required and not is_configured:
            logger.error("Required telemetry feed missing credentials", feed=feed_name)
            raise MissingCredentialError(
                f"Startup validation failed: Telemetry feed '{feed_name}' is marked required: true "
                f"but is missing institutional endpoint or credentials."
            )
        return is_configured


def validate_runtime_environment() -> IndianRegionalEnvironment:
    """
    Validates environment settings at startup.
    Raises EnvironmentValidationError if critical settings are missing or violated.
    """
    try:
        raw_min_lat = float(os.getenv("UTTARAKHAND_MIN_LAT", "28.7161"))
        raw_max_lat = float(os.getenv("UTTARAKHAND_MAX_LAT", "31.4558"))
        raw_min_lon = float(os.getenv("UTTARAKHAND_MIN_LON", "77.5757"))
        raw_max_lon = float(os.getenv("UTTARAKHAND_MAX_LON", "81.0475"))

        env = IndianRegionalEnvironment(
            app_env=os.getenv("APP_ENV", os.getenv("ENVIRONMENT", "local")),
            app_debug=os.getenv("APP_DEBUG", "false").lower() == "true",
            port=int(os.getenv("PORT", "8080")),
            timezone=os.getenv("TIMEZONE", "Asia/Kolkata"),
            default_country_code=os.getenv("DEFAULT_COUNTRY_CODE", "IN"),
            default_state=os.getenv("DEFAULT_STATE", "Uttarakhand"),
            default_state_bounding_box=os.getenv("DEFAULT_STATE_BOUNDING_BOX", "77.5757,28.7161,81.0475,31.4558"),
            default_map_center_lat=float(os.getenv("DEFAULT_MAP_CENTER_LAT", "30.3165")),
            default_map_center_lon=float(os.getenv("DEFAULT_MAP_CENTER_LON", "78.0322")),
            default_map_zoom=int(os.getenv("DEFAULT_MAP_ZOOM", "8")),
            uttarakhand_min_lat=raw_min_lat,
            uttarakhand_max_lat=raw_max_lat,
            uttarakhand_min_lon=raw_min_lon,
            uttarakhand_max_lon=raw_max_lon,
            ndma_cap_feed_url=os.getenv("NDMA_CAP_FEED_URL") or os.getenv("NDMA_CAP_GATEWAY_URL") or None,
            imd_uttarakhand_warn_url=os.getenv("IMD_UTTARAKHAND_WARN_URL") or os.getenv("IMD_WEATHER_ALERTS_ENDPOINT") or None,
            cwc_river_gauge_stream=os.getenv("CWC_RIVER_GAUGE_STREAM") or os.getenv("CWC_HYDROLOGY_FEED") or None,
            iitr_earthquake_ws=os.getenv("IITR_EARTHQUAKE_WS") or os.getenv("IITR_EEW_SEISMIC_WS") or None,
            ndma_cap_api_key=os.getenv("NDMA_CAP_API_KEY") or None,
            cwc_gauge_api_key=os.getenv("CWC_GAUGE_API_KEY") or None,
            iitr_eew_auth_token=os.getenv("IITR_EEW_AUTH_TOKEN") or None,
            cdot_cell_broadcast_proxy=os.getenv("CDOT_CELL_BROADCAST_PROXY") or None,
            nic_sms_gateway_url=os.getenv("NIC_SMS_GATEWAY_URL") or None,
            nic_sms_api_key=os.getenv("NIC_SMS_API_KEY") or None,
            nic_sms_auth_token=os.getenv("NIC_SMS_AUTH_TOKEN") or None,
            nic_ivr_gateway_url=os.getenv("NIC_IVR_GATEWAY_URL") or None,
            nic_ivr_api_key=os.getenv("NIC_IVR_API_KEY") or None,
            whatsapp_business_api_url=os.getenv("WHATSAPP_BUSINESS_API_URL") or None,
            whatsapp_business_api_key=os.getenv("WHATSAPP_BUSINESS_API_KEY") or None,
            fcm_server_key=os.getenv("FCM_SERVER_KEY") or None,
            ndma_sachet_feed_url=os.getenv("NDMA_SACHET_FEED_URL") or None,
            admin_dashboard_jwt_secret=os.getenv("ADMIN_DASHBOARD_JWT_SECRET", "DMMC_SECURE_JWT_SECRET_KEY_2026"),
            public_api_rate_limit_per_min=int(os.getenv("PUBLIC_API_RATE_LIMIT_PER_MIN", "60")),
            national_emergency_line=os.getenv("NATIONAL_EMERGENCY_LINE", "112"),
            state_disaster_helpline=os.getenv("STATE_DISASTER_HELPLINE", "1070"),
            district_disaster_helpline=os.getenv("DISTRICT_DISASTER_HELPLINE", "1077"),
            ambulance_helpline=os.getenv("AMBULANCE_HELPLINE", "108"),
            cdac_cell_broadcast_receiver_id=os.getenv("CDAC_CELL_BROADCAST_RECEIVER_ID", "IN_CAP_001"),
            cache_ttl_seconds=int(os.getenv("CACHE_TTL_SECONDS", "300")),
            emergency_cache_bypass=os.getenv("EMERGENCY_CACHE_BYPASS", "true").lower() == "true",
            upstream_http_timeout_seconds=float(os.getenv("UPSTREAM_HTTP_TIMEOUT_SECONDS", "15.0")),
            max_retry_attempts=int(os.getenv("MAX_RETRY_ATTEMPTS", "3")),
            failover_edge_enabled=os.getenv("FAILOVER_EDGE_ENABLED", "true").lower() == "true",
            failover_primary_region=os.getenv("FAILOVER_PRIMARY_REGION", "ap-south-1"),
            failover_secondary_region=os.getenv("FAILOVER_SECONDARY_REGION", "ap-south-2"),
        )
        return env
    except (SpatialBoundaryViolationError, MissingCredentialError):
        raise
    except Exception as ex:
        raise EnvironmentValidationError(f"CRITICAL: Failed to validate Indian Regional Environment: {ex}") from ex


# Global validated configuration singleton
indian_env = validate_runtime_environment()
