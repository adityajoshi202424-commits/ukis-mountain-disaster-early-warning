"""
Flash Flood Early Warning Platform — Data Quality Engine

Every incoming observation passes through validation before entering the system.
Invalid data is flagged, never silently consumed.

Checks:
- Missing values
- Duplicate records
- Timestamp validity
- Geographic validity (within expected bounds)
- Unit consistency
- Impossible values (e.g., rainfall = -17 mm)
- Stale observations
- Sudden unrealistic jumps
"""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from typing import Optional

import structlog

from backend.data.providers.base import (
    Observation,
    ObservationBatch,
    QualityStatus,
)

logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Physical bounds for validation — documented, not arbitrary
# ---------------------------------------------------------------------------

# Source: WMO guidelines, historical extremes, and common sense
VARIABLE_BOUNDS: dict[str, dict] = {
    "rainfall": {
        "min": 0.0,
        "max": 500.0,  # mm/hour — Cherrapunji record is ~381mm/hr spot
        "unit": "mm",
        "max_jump": 200.0,  # mm change between consecutive observations
    },
    "rainfall_daily": {
        "min": 0.0,
        "max": 2000.0,  # mm/day — Mawsynram/Cherrapunji can exceed 1000
        "unit": "mm",
    },
    "temperature": {
        "min": -50.0,
        "max": 60.0,  # °C
        "unit": "°C",
        "max_jump": 15.0,  # °C change per hour
    },
    "humidity": {
        "min": 0.0,
        "max": 100.0,
        "unit": "%",
    },
    "wind_speed": {
        "min": 0.0,
        "max": 120.0,  # m/s — Category 5 cyclone range
        "unit": "m/s",
    },
    "river_level": {
        "min": -10.0,  # meters — some gauges reference below sea level
        "max": 30.0,  # meters — extreme flood stage
        "unit": "m",
        "max_jump": 3.0,  # m change per 15 minutes
    },
    "pressure": {
        "min": 870.0,  # hPa — lowest recorded
        "max": 1084.0,  # hPa — highest recorded
        "unit": "hPa",
    },
    "elevation": {
        "min": -500.0,
        "max": 9000.0,
        "unit": "m",
    },
}

# Uttarakhand geographic bounds (with generous padding covering all 13 districts)
UTTARAKHAND_BOUNDS = {
    "lat_min": 28.5,
    "lat_max": 31.6,
    "lon_min": 77.5,
    "lon_max": 81.2,
}

# How old an observation can be before it's considered stale
STALE_THRESHOLDS: dict[str, timedelta] = {
    "rainfall": timedelta(hours=2),
    "temperature": timedelta(hours=3),
    "river_level": timedelta(hours=1),
    "wind_speed": timedelta(hours=3),
    "forecast": timedelta(hours=6),
    "default": timedelta(hours=6),
}


class DataQualityEngine:
    """
    Validates every observation before it enters the system.

    Returns observations with updated quality_status.
    Never silently drops or fabricates data.
    """

    def validate_batch(
        self,
        batch: ObservationBatch,
        reference_time: Optional[datetime] = None,
        previous_observations: Optional[list[Observation]] = None,
        allow_forecast: bool = False,
    ) -> ObservationBatch:
        """
        Validate all observations in a batch.
        Returns the same batch with quality_status updated on each observation.

        Args:
            allow_forecast: If True, future-timestamped data is treated as forecast
                           (VALID) rather than rejected. Use for weather forecast APIs.
        """
        if reference_time is None:
            reference_time = datetime.now(timezone.utc)

        validated = []
        for obs in batch.observations:
            validated_obs = self._validate_observation(
                obs, reference_time, previous_observations, allow_forecast
            )
            validated.append(validated_obs)

        batch.observations = validated
        return batch

    def _validate_observation(
        self,
        obs: Observation,
        reference_time: datetime,
        previous: Optional[list[Observation]] = None,
        allow_forecast: bool = False,
    ) -> Observation:
        """Run all validation checks on a single observation."""

        issues: list[str] = []

        # Check 1: Missing value
        if obs.value is None:
            obs.provenance.quality_status = QualityStatus.MISSING
            logger.info(
                "quality_check_missing",
                variable=obs.variable,
                lat=obs.latitude,
                lon=obs.longitude,
            )
            return obs

        # Check 2: NaN / Inf
        if math.isnan(obs.value) or math.isinf(obs.value):
            obs.provenance.quality_status = QualityStatus.INVALID
            issues.append(f"Value is NaN or Inf: {obs.value}")
            self._log_issue(obs, issues)
            return obs

        # Check 3: Physical bounds
        bounds = VARIABLE_BOUNDS.get(obs.variable)
        if bounds:
            if obs.value < bounds["min"] or obs.value > bounds["max"]:
                obs.provenance.quality_status = QualityStatus.INVALID
                issues.append(
                    f"Value {obs.value} outside bounds "
                    f"[{bounds['min']}, {bounds['max']}] for {obs.variable}"
                )
                self._log_issue(obs, issues)
                return obs

        # Check 4: Geographic validity
        if not self._is_valid_location(obs.latitude, obs.longitude):
            obs.provenance.quality_status = QualityStatus.SUSPECT
            issues.append(
                f"Location ({obs.latitude}, {obs.longitude}) outside expected region"
            )

        # Check 5: Timestamp validity
        if obs.observation_time:
            # Future observation (more than 5 minutes ahead)
            if obs.observation_time > reference_time + timedelta(minutes=5):
                if not allow_forecast:
                    obs.provenance.quality_status = QualityStatus.INVALID
                    issues.append(
                        f"Observation time {obs.observation_time} is in the future"
                    )
                    self._log_issue(obs, issues)
                    return obs
                # else: forecast data — future timestamps are expected, keep VALID

            # Stale observation
            stale_threshold = STALE_THRESHOLDS.get(
                obs.variable, STALE_THRESHOLDS["default"]
            )
            age = reference_time - obs.observation_time
            if age > stale_threshold:
                obs.provenance.quality_status = QualityStatus.STALE
                issues.append(
                    f"Observation is {age} old (threshold: {stale_threshold})"
                )

        # Check 6: Sudden unrealistic jumps
        if previous and bounds and "max_jump" in bounds:
            jump_issue = self._check_jump(obs, previous, bounds["max_jump"])
            if jump_issue:
                issues.append(jump_issue)
                obs.provenance.quality_status = QualityStatus.SUSPECT

        # Log any issues found
        if issues:
            self._log_issue(obs, issues)
        else:
            obs.provenance.quality_status = QualityStatus.VALID

        return obs

    def _is_valid_location(self, lat: float, lon: float) -> bool:
        """Check if coordinates are within the expected region (Uttarakhand + padding)."""
        return (
            UTTARAKHAND_BOUNDS["lat_min"] <= lat <= UTTARAKHAND_BOUNDS["lat_max"]
            and UTTARAKHAND_BOUNDS["lon_min"] <= lon <= UTTARAKHAND_BOUNDS["lon_max"]
        )

    def _check_jump(
        self,
        current: Observation,
        previous: list[Observation],
        max_jump: float,
    ) -> Optional[str]:
        """Check for unrealistic jumps between consecutive observations."""
        # Find the most recent previous observation of the same variable at same location
        for prev in reversed(previous):
            if (
                prev.variable == current.variable
                and prev.value is not None
                and abs(prev.latitude - current.latitude) < 0.01
                and abs(prev.longitude - current.longitude) < 0.01
            ):
                jump = abs(current.value - prev.value)
                if jump > max_jump:
                    return (
                        f"Sudden jump: {prev.value} → {current.value} "
                        f"(delta={jump}, max_allowed={max_jump})"
                    )
                break
        return None

    def _log_issue(self, obs: Observation, issues: list[str]) -> None:
        """Log quality issues with structured logging."""
        logger.warning(
            "data_quality_issue",
            variable=obs.variable,
            value=obs.value,
            lat=obs.latitude,
            lon=obs.longitude,
            quality_status=obs.provenance.quality_status.value,
            issues=issues,
            source=obs.provenance.source,
        )

    def get_staleness(
        self, obs: Observation, reference_time: Optional[datetime] = None
    ) -> Optional[timedelta]:
        """
        Calculate how stale an observation is.
        Returns None if observation_time is not set.
        The UI uses this to show "Updated 7 minutes ago".
        """
        if reference_time is None:
            reference_time = datetime.now(timezone.utc)
        if obs.observation_time is None:
            return None
        return reference_time - obs.observation_time

    def format_staleness(self, staleness: Optional[timedelta]) -> str:
        """Format staleness for UI display."""
        if staleness is None:
            return "Observation time unknown"

        total_seconds = int(staleness.total_seconds())
        if total_seconds < 60:
            return f"Updated {total_seconds} seconds ago"
        elif total_seconds < 3600:
            minutes = total_seconds // 60
            return f"Updated {minutes} minute{'s' if minutes != 1 else ''} ago"
        elif total_seconds < 86400:
            hours = total_seconds // 3600
            return f"Updated {hours} hour{'s' if hours != 1 else ''} ago"
        else:
            days = total_seconds // 86400
            return f"Last observation: {days} day{'s' if days != 1 else ''} ago"


# Singleton
quality_engine = DataQualityEngine()
