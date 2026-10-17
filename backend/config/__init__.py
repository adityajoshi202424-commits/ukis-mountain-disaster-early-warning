"""
Flash Flood & Multi-Hazard Early Warning Platform — Configuration Package
All settings loaded dynamically from environment variables (.env files).
Zero hardcoded keys, coordinates, or tokens.
"""

from __future__ import annotations

import enum
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Export environment validator and hazard thresholds
from backend.config.env_validator import (
    indian_env,
    IndianRegionalEnvironment,
    IndianRegionalEnvironment as IndianEnvironmentConfig,
)
from backend.config.hazard_thresholds import MountainHazardConfig


class Environment(str, enum.Enum):
    LOCAL = "local"
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class DataMode(str, enum.Enum):
    """
    The operating modes — NEVER mixed.
    The UI must always display which mode is active.
    """

    LIVE = "LIVE"  # Real-time/recent external observations
    HISTORICAL = "HISTORICAL"  # Real historical observations
    REPLAY = "REPLAY"  # Historical data replayed chronologically
    SIMULATION = "SIMULATION"  # Synthetic values for dev/testing only


class Settings(BaseSettings):
    """Application settings. Loaded from .env file or environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Application ---
    app_env: Environment = Environment.DEVELOPMENT
    app_secret_key: str = Field(default="CHANGE_ME", description="Application secret key")
    app_debug: bool = False

    # --- Database ---
    db_host: str = "localhost"
    db_port: int = 25432
    db_name: str = "flashflood"
    db_user: str = "flashflood"
    db_password: str = "CHANGE_ME"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def database_url_sync(self) -> str:
        return (
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    # --- Redis ---
    redis_url: str = "redis://localhost:6379/0"

    # --- Data Provider API Keys ---
    nasa_earthdata_username: Optional[str] = None
    nasa_earthdata_password: Optional[str] = None
    imd_api_key: Optional[str] = None
    cwc_api_key: Optional[str] = None
    opentopography_api_key: Optional[str] = None

    # --- Alert Channels ---
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    alert_email_from: Optional[str] = None
    alert_webhook_url: Optional[str] = None

    # --- JWT ---
    jwt_secret_key: str = "CHANGE_ME"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    # --- Logging ---
    log_level: str = "INFO"
    log_format: str = "json"

    # --- Paths ---
    data_cache_dir: Path = Path("data_cache")
    ml_artifacts_dir: Path = Path("ml_artifacts")

    def provider_has_credentials(self, provider: str) -> bool:
        """Check if a specific provider has its required credentials configured."""
        checks = {
            "nasa_gpm": bool(self.nasa_earthdata_username and self.nasa_earthdata_password),
            "imd": bool(self.imd_api_key),
            "cwc": bool(self.cwc_api_key),
            "opentopography": bool(self.opentopography_api_key),
            "open_meteo": True,
            "nasa_power": True,
            "osm": True,
            "usgs_earthquakes": True,
        }
        return checks.get(provider, False)


# Singleton — import this everywhere
settings = Settings()

__all__ = [
    "Environment",
    "DataMode",
    "Settings",
    "settings",
    "indian_env",
    "IndianEnvironmentConfig",
    "MountainHazardConfig",
]
