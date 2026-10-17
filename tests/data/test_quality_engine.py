"""
Tests for the data quality engine.

Validates that the quality engine correctly identifies:
- Invalid values (negative rainfall, out-of-range temperature)
- Missing values
- Stale observations
- Future timestamps
- NaN/Inf values
- Geographic validity
"""

from datetime import datetime, timedelta, timezone

import pytest

from backend.data.providers.base import DataProvenance, Observation, QualityStatus
from backend.data.validation.quality import DataQualityEngine


@pytest.fixture
def engine():
    return DataQualityEngine()


def _make_observation(
    variable: str = "rainfall",
    value: float = 10.0,
    unit: str = "mm",
    lat: float = 30.5564,
    lon: float = 79.5670,
    obs_time: datetime = None,
) -> Observation:
    """Helper to create test observations with full provenance."""
    if obs_time is None:
        obs_time = datetime.now(timezone.utc) - timedelta(minutes=5)

    return Observation(
        variable=variable,
        value=value,
        unit=unit,
        latitude=lat,
        longitude=lon,
        observation_time=obs_time,
        provenance=DataProvenance(
            source="TestSource",
            source_url="https://test.example.com",
            provider="TestProvider",
            dataset="test-dataset",
            retrieved_at=datetime.now(timezone.utc),
            observation_time=obs_time,
            spatial_resolution="test",
            temporal_resolution="test",
            units=unit,
            quality_status=QualityStatus.VALID,
            processing_version="1.0.0",
        ),
    )


class TestPhysicalBounds:
    """Test that physically impossible values are caught."""

    def test_negative_rainfall_is_invalid(self, engine):
        """Rainfall = -17 mm must NOT silently enter the model."""
        obs = _make_observation(variable="rainfall", value=-17.0)
        from backend.data.providers.base import ObservationBatch
        from backend.data.providers.base import ProviderStatus

        batch = ObservationBatch(
            provider_name="test",
            fetch_timestamp=datetime.now(timezone.utc),
            status=ProviderStatus.AVAILABLE,
            observations=[obs],
        )
        result = engine.validate_batch(batch)
        assert result.observations[0].provenance.quality_status == QualityStatus.INVALID

    def test_extreme_rainfall_is_invalid(self, engine):
        """Rainfall = 600 mm/hr exceeds physical bounds."""
        obs = _make_observation(variable="rainfall", value=600.0)
        from backend.data.providers.base import ObservationBatch, ProviderStatus

        batch = ObservationBatch(
            provider_name="test",
            fetch_timestamp=datetime.now(timezone.utc),
            status=ProviderStatus.AVAILABLE,
            observations=[obs],
        )
        result = engine.validate_batch(batch)
        assert result.observations[0].provenance.quality_status == QualityStatus.INVALID

    def test_valid_rainfall_passes(self, engine):
        """Normal rainfall value should be VALID."""
        obs = _make_observation(variable="rainfall", value=42.3)
        from backend.data.providers.base import ObservationBatch, ProviderStatus

        batch = ObservationBatch(
            provider_name="test",
            fetch_timestamp=datetime.now(timezone.utc),
            status=ProviderStatus.AVAILABLE,
            observations=[obs],
        )
        result = engine.validate_batch(batch)
        assert result.observations[0].provenance.quality_status == QualityStatus.VALID

    def test_temperature_below_minus_50_is_invalid(self, engine):
        obs = _make_observation(variable="temperature", value=-55.0, unit="°C")
        from backend.data.providers.base import ObservationBatch, ProviderStatus

        batch = ObservationBatch(
            provider_name="test",
            fetch_timestamp=datetime.now(timezone.utc),
            status=ProviderStatus.AVAILABLE,
            observations=[obs],
        )
        result = engine.validate_batch(batch)
        assert result.observations[0].provenance.quality_status == QualityStatus.INVALID


class TestMissingValues:
    """Test that None values are correctly flagged as MISSING."""

    def test_none_value_is_missing(self, engine):
        obs = _make_observation(variable="rainfall", value=None)
        obs.value = None  # Explicitly set
        from backend.data.providers.base import ObservationBatch, ProviderStatus

        batch = ObservationBatch(
            provider_name="test",
            fetch_timestamp=datetime.now(timezone.utc),
            status=ProviderStatus.AVAILABLE,
            observations=[obs],
        )
        result = engine.validate_batch(batch)
        assert result.observations[0].provenance.quality_status == QualityStatus.MISSING


class TestNaNInf:
    """Test that NaN and Inf are caught."""

    def test_nan_is_invalid(self, engine):
        obs = _make_observation(value=float("nan"))
        from backend.data.providers.base import ObservationBatch, ProviderStatus

        batch = ObservationBatch(
            provider_name="test",
            fetch_timestamp=datetime.now(timezone.utc),
            status=ProviderStatus.AVAILABLE,
            observations=[obs],
        )
        result = engine.validate_batch(batch)
        assert result.observations[0].provenance.quality_status == QualityStatus.INVALID

    def test_inf_is_invalid(self, engine):
        obs = _make_observation(value=float("inf"))
        from backend.data.providers.base import ObservationBatch, ProviderStatus

        batch = ObservationBatch(
            provider_name="test",
            fetch_timestamp=datetime.now(timezone.utc),
            status=ProviderStatus.AVAILABLE,
            observations=[obs],
        )
        result = engine.validate_batch(batch)
        assert result.observations[0].provenance.quality_status == QualityStatus.INVALID


class TestStaleness:
    """Test stale observation detection."""

    def test_stale_rainfall_detected(self, engine):
        """Rainfall observation 3 hours old should be STALE (threshold: 2h)."""
        old_time = datetime.now(timezone.utc) - timedelta(hours=3)
        obs = _make_observation(variable="rainfall", obs_time=old_time)
        from backend.data.providers.base import ObservationBatch, ProviderStatus

        batch = ObservationBatch(
            provider_name="test",
            fetch_timestamp=datetime.now(timezone.utc),
            status=ProviderStatus.AVAILABLE,
            observations=[obs],
        )
        result = engine.validate_batch(batch)
        assert result.observations[0].provenance.quality_status == QualityStatus.STALE

    def test_fresh_rainfall_is_valid(self, engine):
        """Rainfall observation 30 minutes old should be VALID."""
        recent_time = datetime.now(timezone.utc) - timedelta(minutes=30)
        obs = _make_observation(variable="rainfall", obs_time=recent_time)
        from backend.data.providers.base import ObservationBatch, ProviderStatus

        batch = ObservationBatch(
            provider_name="test",
            fetch_timestamp=datetime.now(timezone.utc),
            status=ProviderStatus.AVAILABLE,
            observations=[obs],
        )
        result = engine.validate_batch(batch)
        assert result.observations[0].provenance.quality_status == QualityStatus.VALID


class TestFutureTimestamp:
    """Test that future observations are rejected."""

    def test_future_observation_is_invalid(self, engine):
        future_time = datetime.now(timezone.utc) + timedelta(hours=1)
        obs = _make_observation(obs_time=future_time)
        from backend.data.providers.base import ObservationBatch, ProviderStatus

        batch = ObservationBatch(
            provider_name="test",
            fetch_timestamp=datetime.now(timezone.utc),
            status=ProviderStatus.AVAILABLE,
            observations=[obs],
        )
        result = engine.validate_batch(batch)
        assert result.observations[0].provenance.quality_status == QualityStatus.INVALID


class TestGeographicValidity:
    """Test that coordinates outside expected region are flagged."""

    def test_outside_uttarakhand_is_suspect(self, engine):
        """Coordinates far outside Uttarakhand should be SUSPECT."""
        obs = _make_observation(lat=10.0, lon=76.0)  # Kerala, not Uttarakhand
        from backend.data.providers.base import ObservationBatch, ProviderStatus

        batch = ObservationBatch(
            provider_name="test",
            fetch_timestamp=datetime.now(timezone.utc),
            status=ProviderStatus.AVAILABLE,
            observations=[obs],
        )
        result = engine.validate_batch(batch)
        assert result.observations[0].provenance.quality_status == QualityStatus.SUSPECT


class TestStalenessFormatting:
    """Test UI-facing staleness display."""

    def test_format_seconds(self, engine):
        result = engine.format_staleness(timedelta(seconds=30))
        assert "30 seconds ago" in result

    def test_format_minutes(self, engine):
        result = engine.format_staleness(timedelta(minutes=7))
        assert "7 minutes ago" in result

    def test_format_hours(self, engine):
        result = engine.format_staleness(timedelta(hours=2))
        assert "2 hours ago" in result

    def test_format_days(self, engine):
        result = engine.format_staleness(timedelta(days=3))
        assert "3 days ago" in result

    def test_format_none(self, engine):
        result = engine.format_staleness(None)
        assert "unknown" in result.lower()
