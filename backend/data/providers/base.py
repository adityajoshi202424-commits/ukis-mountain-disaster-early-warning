"""
Flash Flood Early Warning Platform — Data Provider Interface

Every data source MUST implement this interface.
Every observation MUST carry full provenance.
No fabricated data. No mock endpoints disguised as production.
"""

from __future__ import annotations

import enum
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Provider Status — what the UI shows
# ---------------------------------------------------------------------------


class ProviderStatus(str, enum.Enum):
    """Status of a data provider. Displayed in UI and API responses."""

    AVAILABLE = "AVAILABLE"
    API_KEY_REQUIRED = "API_KEY_REQUIRED"
    OFFLINE = "OFFLINE"
    RATE_LIMITED = "RATE_LIMITED"
    ERROR = "ERROR"
    STALE = "STALE"  # Last observation is older than acceptable threshold


class QualityStatus(str, enum.Enum):
    """Quality status of an individual observation."""

    VALID = "VALID"
    SUSPECT = "SUSPECT"  # Passed basic checks but flagged
    INVALID = "INVALID"  # Failed validation — must NOT enter model
    MISSING = "MISSING"  # No observation available
    STALE = "STALE"  # Observation is too old


# ---------------------------------------------------------------------------
# Data Provenance — EVERY observation must carry this
# ---------------------------------------------------------------------------


class DataProvenance(BaseModel):
    """
    Complete provenance record for any externally sourced observation.
    Required by specification: source, source_url, provider, dataset,
    retrieved_at, observation_time, spatial_resolution, temporal_resolution,
    units, quality_status, processing_version.
    """

    source: str = Field(description="Authoritative source name (e.g., 'Open-Meteo')")
    source_url: str = Field(description="URL from which data was retrieved")
    provider: str = Field(description="Provider implementation class name")
    dataset: str = Field(description="Specific dataset identifier")
    retrieved_at: datetime = Field(description="When the data was fetched from the source")
    observation_time: Optional[datetime] = Field(
        default=None, description="When the phenomenon was observed/measured"
    )
    spatial_resolution: Optional[str] = Field(
        default=None, description="e.g., '0.25°', '30m', 'station-level'"
    )
    temporal_resolution: Optional[str] = Field(
        default=None, description="e.g., 'hourly', '3-hourly', 'daily'"
    )
    units: Optional[str] = Field(default=None, description="e.g., 'mm', '°C', 'm'")
    quality_status: QualityStatus = QualityStatus.VALID
    processing_version: str = Field(
        default="1.0.0", description="Version of the processing pipeline"
    )


# ---------------------------------------------------------------------------
# Observation — the standard record
# ---------------------------------------------------------------------------


class Observation(BaseModel):
    """A single validated observation with full provenance."""

    variable: str = Field(description="What is being measured (e.g., 'rainfall', 'temperature')")
    value: Optional[float] = Field(
        default=None, description="Numeric value. None if DATA UNAVAILABLE."
    )
    unit: Optional[str] = Field(default=None)
    latitude: float
    longitude: float
    observation_time: Optional[datetime] = None
    provenance: DataProvenance

    @property
    def is_available(self) -> bool:
        return self.value is not None and self.provenance.quality_status == QualityStatus.VALID


class ObservationBatch(BaseModel):
    """A batch of observations from a single provider fetch."""

    provider_name: str
    fetch_timestamp: datetime
    status: ProviderStatus
    observations: list[Observation] = Field(default_factory=list)
    error_message: Optional[str] = None

    @property
    def valid_count(self) -> int:
        return sum(1 for o in self.observations if o.is_available)


# ---------------------------------------------------------------------------
# Provider Health — for monitoring dashboard
# ---------------------------------------------------------------------------


class ProviderHealth(BaseModel):
    """Health status for a data provider — shown in admin/monitoring UI."""

    provider_name: str
    status: ProviderStatus
    last_successful_fetch: Optional[datetime] = None
    last_error: Optional[str] = None
    last_error_time: Optional[datetime] = None
    observations_fetched: int = 0
    average_latency_ms: Optional[float] = None
    credentials_configured: bool = False


# ---------------------------------------------------------------------------
# Data Provider Interface — EVERY provider must implement this
# ---------------------------------------------------------------------------


class DataProvider(ABC):
    """
    Abstract interface for all data providers.

    Provider lifecycle:
        Provider interface
            ↓
        Real provider implementation
            ↓
        Authentication
            ↓
        Request
            ↓
        Validation
            ↓
        Normalization
            ↓
        Storage

    If unavailable, degrade gracefully. Never fabricate.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable provider name."""
        ...

    @property
    @abstractmethod
    def source_url(self) -> str:
        """Base URL of the data source."""
        ...

    @property
    @abstractmethod
    def requires_api_key(self) -> bool:
        """Whether this provider needs credentials."""
        ...

    @abstractmethod
    async def check_status(self) -> ProviderStatus:
        """
        Check if the provider is currently available.
        Returns API_KEY_REQUIRED if credentials are missing.
        Returns OFFLINE if the endpoint is unreachable.
        """
        ...

    @abstractmethod
    async def fetch(
        self,
        latitude: float,
        longitude: float,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        **kwargs: Any,
    ) -> ObservationBatch:
        """
        Fetch observations from the real source.

        MUST:
        - Attach full DataProvenance to every observation
        - Return ProviderStatus.OFFLINE if unreachable
        - Return ProviderStatus.API_KEY_REQUIRED if credentials missing
        - NEVER fabricate values
        - NEVER return random/placeholder data

        If the source cannot provide a value, the observation.value MUST be None
        and quality_status MUST be MISSING.
        """
        ...

    @abstractmethod
    async def validate(self, batch: ObservationBatch) -> ObservationBatch:
        """
        Validate observations using provider-specific rules.
        Mark invalid observations with QualityStatus.INVALID.
        """
        ...

    @abstractmethod
    def metadata(self) -> dict[str, Any]:
        """
        Return provider metadata for documentation and transparency.
        Must include: license, update_frequency, coverage, limitations.
        """
        ...

    async def health(self) -> ProviderHealth:
        """Get current health status of this provider."""
        status = await self.check_status()
        return ProviderHealth(
            provider_name=self.name,
            status=status,
            credentials_configured=not self.requires_api_key or status != ProviderStatus.API_KEY_REQUIRED,
        )
