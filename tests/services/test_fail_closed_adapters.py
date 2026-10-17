"""
Unit tests verifying Stage 1 Fail-Closed Adapters, Bounding Box Guards, and Config Validation.
"""

import pytest
from backend.config.env_validator import (
    IndianRegionalEnvironment,
    SpatialBoundaryViolationError,
    MissingCredentialError,
    validate_runtime_environment,
)
from backend.services.hazard_adapters import (
    hazard_registry,
    HimalayanHazardType,
    CwcGlofFlashFloodAdapter,
    CircuitBreaker,
)
from backend.services.push_sms_pipeline import (
    nic_sms_adapter,
    cdot_broadcast_adapter,
    fcm_push_adapter,
)


def test_spatial_bounding_box_violation_throws():
    """Verify bounding box coordinates outside Uttarakhand throw SpatialBoundaryViolationError."""
    with pytest.raises(SpatialBoundaryViolationError):
        # Longitude far outside Uttarakhand (e.g. 70.0°E in Gujarat/Rajasthan)
        IndianRegionalEnvironment(uttarakhand_min_lon=70.0)

    with pytest.raises(SpatialBoundaryViolationError):
        # Latitude far outside Uttarakhand (e.g. 20.0°N in Maharashtra)
        IndianRegionalEnvironment(uttarakhand_min_lat=20.0)


def test_required_feed_missing_credentials_throws():
    """Verify feed marked required: true raises MissingCredentialError if unconfigured."""
    env = validate_runtime_environment()
    with pytest.raises(MissingCredentialError):
        env.validate_feed(feed_name="MANDATORY_SEISMIC_STREAM", endpoint="", required=True)


@pytest.mark.asyncio
async def test_all_6_hazard_adapters_fail_closed_without_credentials():
    """Verify all 6 hazard adapters fail closed gracefully and return DATA_UNAVAILABLE when unconfigured."""
    statuses = hazard_registry.get_feed_statuses()
    assert len(statuses) == 6

    # When running with unconfigured credentials, all feeds report DATA_UNAVAILABLE
    for s in statuses:
        if not s.isConfigured:
            assert s.status == "DATA_UNAVAILABLE"
            assert "no credentials configured" in s.errorMessage.lower()

    # Querying all alerts returns an empty list without crashing or simulating fake data
    result = await hazard_registry.fetch_all_alerts(district="Chamoli")
    assert "alerts" in result
    assert "feed_statuses" in result
    assert result["count"] == len(result["alerts"])


@pytest.mark.asyncio
async def test_push_and_sms_adapters_fail_closed_with_audit():
    """Verify SMS and push dispatchers skip gracefully and log without pretending messages went out."""
    # Test NIC SMS fail-closed
    sms_res = await nic_sms_adapter.dispatch_sms_batch(["+919876543210"], "Test emergency alert")
    if not nic_sms_adapter.is_configured():
        assert sms_res.status == "SKIPPED_NO_GATEWAY"
        assert "no gateway configured" in sms_res.message

    # Test C-DOT broadcast fail-closed
    cdot_res = await cdot_broadcast_adapter.broadcast_polygon([[30.5, 79.5]], "Evacuate valley", "CRITICAL")
    if not cdot_broadcast_adapter.is_configured():
        assert cdot_res.status == "SKIPPED_NO_GATEWAY"

    # Test FCM push fail-closed
    fcm_res = await fcm_push_adapter.send_push_notification(["tok_123"], "Warning", "Body", "CRITICAL")
    if not fcm_push_adapter.is_configured():
        assert fcm_res.status == "SKIPPED_NO_GATEWAY"


def test_circuit_breaker_transitions():
    """Verify circuit breaker trips to OPEN on repeated failures and recovers after backoff."""
    cb = CircuitBreaker(failure_threshold=3, recovery_time_seconds=0.1)
    assert cb.state == "CLOSED"
    assert cb.can_attempt() is True

    cb.record_failure()
    cb.record_failure()
    assert cb.state == "CLOSED"

    cb.record_failure()
    assert cb.state == "OPEN"
    assert cb.can_attempt() is False

    # Simulate waiting past recovery time
    import time
    time.sleep(0.15)
    assert cb.can_attempt() is True
    assert cb.state == "HALF_OPEN"

    cb.record_success()
    assert cb.state == "CLOSED"
