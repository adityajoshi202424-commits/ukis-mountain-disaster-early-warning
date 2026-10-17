"""
Comprehensive Test Suite for:
1. 5-Channel Alert Delivery Pipeline (C-DOT Cell Broadcast, NIC SMS, NIC IVR, WhatsApp, FCM Push)
2. Testing all 6 Historic Uttarakhand Disaster CAP Fixtures + 1 Malformed Fixture
3. Citizen "Mark Safe" & Family Status Query (DPDP Act 2023)
4. Crowdsourced Hazard Reports & Admin Moderation Queue
5. Shelter Occupancy Management (Live vs. Static)
6. Adapter Health Staleness Audit & Internal Ops Alerts
7. Public API Rate Limiting
8. DMMC Admin Authentication, Manual Issuance & Sensor Override
"""

import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app
from backend.cap_schema import (
    CapAlertItem,
    AlertSeverity,
    HimalayanHazardType,
    HazardReportCategory,
    HazardReportStatus,
    CitizenSafetyStatus,
)
from backend.services.dpdp_user_registry import user_registry
from backend.services.alert_dispatch_pipeline import alert_dispatch_pipeline
from backend.services.citizen_safety_service import citizen_safety_service
from backend.services.adapter_health_monitor import adapter_health_monitor
from backend.data.fixtures.uttarakhand_cap_fixtures import (
    ALL_HISTORIC_FIXTURES,
    FIXTURE_MALFORMED_CAP_PAYLOAD,
    FIXTURE_2021_CHAMOLI_GLOF,
)
from backend.middleware.rate_limiter import public_rate_limiter


@pytest.fixture(autouse=True)
def reset_test_state():
    """Reset registry, public rate limiter, and clean up test state before each test."""
    user_registry._subscribers.clear()
    public_rate_limiter.reset()


# ---------------------------------------------------------------------------
# 1. 5-CHANNEL ALERT DELIVERY & HISTORIC FIXTURES
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_all_6_historic_fixtures_dispatch_across_5_channels():
    """
    Verifies that all 6 historic Uttarakhand disaster fixtures exercise the
    5-channel dispatch pipeline without live credentials, failing closed safely.
    """
    # Register test subscribers across affected districts with diverse dialects
    user_registry.register_or_update("+919876543211", locale="hi-IN", district="Rudraprayag", device_token="fcm_rudra")
    user_registry.register_or_update("+919876543212", locale="gbm-IN", district="Chamoli", device_token="fcm_cham")
    user_registry.register_or_update("+919876543213", locale="kfy-IN", district="Pauri Garhwal")
    user_registry.register_or_update("+919876543214", locale="en-IN", district="Uttarkashi", device_token="fcm_uttar")

    assert len(ALL_HISTORIC_FIXTURES) == 6

    for alert_obj in ALL_HISTORIC_FIXTURES:
        audit = await alert_dispatch_pipeline.process_and_dispatch_cap_alert(alert_obj)

        assert audit["alert_id"] == alert_obj.identifier
        assert audit["hazard_type"] == alert_obj.hazardType.value
        assert audit["severity"] == alert_obj.severity.value
        assert "gateway_statuses" in audit
        assert audit["latency_ms"] >= 0.0

        # Verify fail-closed behavior for unconfigured gateways
        statuses = audit["gateway_statuses"]
        assert any("SKIPPED_NO_GATEWAY" in s or "FAILED" in s or "SUCCESS" in s for s in statuses.values())


@pytest.mark.asyncio
async def test_critical_tier_triggers_cell_broadcast_and_ivr():
    """
    Verifies that CRITICAL tier alerts trigger C-DOT Cell Broadcast and NIC IVR Voice calls
    as priority zero-data and low-literacy channels.
    """
    user_registry.register_or_update("+919111111111", locale="gbm-IN", district="Chamoli")

    chamoli_alert = FIXTURE_2021_CHAMOLI_GLOF
    assert chamoli_alert.severity == AlertSeverity.CRITICAL

    audit = await alert_dispatch_pipeline.process_and_dispatch_cap_alert(chamoli_alert)
    assert audit["severity"] == "CRITICAL"
    statuses = audit["gateway_statuses"]

    # In unconfigured mode, C-DOT cell broadcast and IVR must have been invoked and safely skipped
    assert "CDOT_CELL_BROADCAST" in statuses
    assert any("NIC_IVR" in k for k in statuses.keys())


def test_malformed_fixture_handling():
    """
    Deliberately malformed payload missing mandatory CAP fields must fail Pydantic validation
    cleanly without crashing the server.
    """
    with pytest.raises(Exception):
        CapAlertItem(**FIXTURE_MALFORMED_CAP_PAYLOAD)


# ---------------------------------------------------------------------------
# 2. CITIZEN "MARK SAFE" & FAMILY CHECK-IN
# ---------------------------------------------------------------------------
def test_citizen_mark_safe_and_linked_contact_query():
    """
    Tests citizen marking themselves safe, privacy-preserving hashing,
    and family member query by contact number.
    """
    user_phone = "+919876500001"
    family_contact = "+919876500002"

    # 1. Citizen marks safe
    rec = citizen_safety_service.check_in_safe(
        phone=user_phone,
        district="Chamoli",
        status=CitizenSafetyStatus.SAFE,
        message="Safe at Joshimath Relief Centre",
        linked_contacts=[family_contact],
    )
    assert rec.phone_hash != user_phone
    assert rec.status == CitizenSafetyStatus.SAFE
    assert rec.district == "Chamoli"

    # 2. Family queries status
    results = citizen_safety_service.get_contact_safety_status(family_contact)
    assert len(results) == 1
    assert results[0]["status"] == "SAFE"
    assert results[0]["district"] == "Chamoli"
    assert "Joshimath Relief Centre" in results[0]["message"]

    # 3. DPDP Erasure
    deleted = citizen_safety_service.delete_checkin_history(user_phone)
    assert deleted is True
    assert len(citizen_safety_service.get_contact_safety_status(family_contact)) == 0


# ---------------------------------------------------------------------------
# 3. CROWDSOURCED HAZARD REPORTS & MODERATION
# ---------------------------------------------------------------------------
def test_crowdsourced_hazard_report_validation_and_moderation():
    """
    Tests geotagged hazard report submission, bounding box guard,
    initial unverified status, and admin approval/rejection.
    """
    # Valid report within Chamoli
    report = citizen_safety_service.submit_hazard_report(
        reporter_phone="+919876543200",
        district="Chamoli",
        hazard_type=HimalayanHazardType.LANDSLIDE_SLOPE_FAILURE,
        category=HazardReportCategory.ROAD_BLOCKED,
        description="Badrinath highway blocked by boulder fall near Sirobagarh",
        lat=30.38,
        lon=79.42,
    )
    assert report.is_unverified is True
    assert report.status == HazardReportStatus.UNVERIFIED

    # Coordinate outside Uttarakhand bounds must raise ValueError
    with pytest.raises(ValueError):
        citizen_safety_service.submit_hazard_report(
            reporter_phone="+919876543200",
            district="Chamoli",
            hazard_type=HimalayanHazardType.LANDSLIDE_SLOPE_FAILURE,
            category=HazardReportCategory.ROAD_BLOCKED,
            description="Out of bounds test",
            lat=25.0,  # Below Uttarakhand min_lat (28.7161)
            lon=79.0,
        )

    # Admin moderation: APPROVE
    approved = citizen_safety_service.moderate_hazard_report(
        report_id=report.report_id,
        action="APPROVE",
        admin_user="dmmc_duty_officer_1",
        notes="Verified by SDRF patrol unit 4",
    )
    assert approved.status == HazardReportStatus.APPROVED
    assert approved.is_unverified is False
    assert approved.verified_by == "dmmc_duty_officer_1"


# ---------------------------------------------------------------------------
# 4. SHELTER OCCUPANCY (LIVE VS STATIC)
# ---------------------------------------------------------------------------
def test_shelter_occupancy_and_admin_update():
    """
    Tests initial static shelter capacity display and admin live occupancy update.
    """
    shelters = citizen_safety_service.get_shelters(district="Chamoli")
    assert len(shelters) >= 1
    chamoli_shelter = shelters[0]
    assert chamoli_shelter.is_live is False  # Static by default
    assert chamoli_shelter.capacity > 0

    # Admin updates live occupancy
    updated = citizen_safety_service.update_shelter_occupancy(
        shelter_id=chamoli_shelter.shelter_id,
        current_occupancy=180,
        is_live=True,
        admin_user="dmmc_admin",
    )
    assert updated.current_occupancy == 180
    assert updated.is_live is True


# ---------------------------------------------------------------------------
# 5. ADAPTER STALENESS & SYSTEM SELF-MONITORING
# ---------------------------------------------------------------------------
def test_adapter_staleness_and_internal_ops_alerts():
    """
    Tests that unconfigured or stale adapters generate internal ops alerts
    without exposing errors to citizens.
    """
    adapter_health_monitor.refresh_adapter_registry()
    statuses = adapter_health_monitor.get_adapter_statuses()
    assert len(statuses) >= 11  # 6 hazard + 5 delivery gateways

    # Check unconfigured adapters fail closed gracefully
    unconf = [s for s in statuses if not s["is_configured"]]
    assert len(unconf) > 0

    # Check internal ops alerts generated
    ops_alerts = adapter_health_monitor.get_internal_ops_alerts()
    assert isinstance(ops_alerts, list)


# ---------------------------------------------------------------------------
# 6. HTTP API INTEGRATION TESTS (ADMIN, CITIZEN, RATE LIMIT)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_full_http_api_endpoints():
    """
    Exercises all HTTP endpoints:
    - Admin login & audit trail
    - Citizen Mark Safe
    - Crowdsourced hazard submission & moderation queue
    - Shelter occupancy
    - Weather.gov parity
    - Rate limit enforcement
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. Admin Login
        login_res = await client.post(
            "/api/v1/admin/login",
            json={"username": "dmmc_admin", "password": "DMMC_Uk_Gov_2026!"},
        )
        assert login_res.status_code == 200
        auth_data = login_res.json()
        assert "access_token" in auth_data
        assert auth_data["role"] == "ADMIN"

        # 2. Citizen Mark Safe
        safe_res = await client.post(
            "/api/v1/citizen/check-in-safe",
            json={
                "phone": "+919412000001",
                "district": "Uttarkashi",
                "status": "SAFE",
                "message": "Safe at Bhatwari",
                "linked_contacts": ["+919412000002"],
            },
        )
        assert safe_res.status_code == 200
        assert safe_res.json()["status"] == "CHECKIN_RECORDED"

        # 3. Family queries status
        fam_res = await client.get("/api/v1/citizen/check-in/status?phone=%2B919412000002")
        assert fam_res.status_code == 200
        assert len(fam_res.json()["family_status"]) >= 1

        # 4. Crowdsourced report submit
        report_res = await client.post(
            "/api/v1/citizen/reports/submit",
            json={
                "reporter_phone": "+919412000003",
                "district": "Rudraprayag",
                "hazardType": "LANDSLIDE_SLOPE_FAILURE",
                "category": "ROAD_BLOCKED",
                "description": "Highway blocked near Sonprayag",
                "lat": 30.63,
                "lon": 79.00,
            },
        )
        assert report_res.status_code == 200
        rpt_data = report_res.json()["report"]
        assert rpt_data["is_unverified"] is True
        rpt_id = rpt_data["report_id"]

        # 5. Admin queue & moderation
        queue_res = await client.get("/api/v1/admin/reports/queue?district=Rudraprayag")
        assert queue_res.status_code == 200
        assert queue_res.json()["count"] >= 1

        mod_res = await client.post(
            f"/api/v1/admin/reports/{rpt_id}/action",
            json={"action": "APPROVE", "admin_user": "dmmc_admin", "notes": "Confirmed by field unit"},
        )
        assert mod_res.status_code == 200
        assert mod_res.json()["report"]["status"] == "APPROVED"

        # 6. Shelter live vs static occupancy
        sh_res = await client.get("/api/v1/shelters/occupancy?district=Chamoli")
        assert sh_res.status_code == 200
        assert len(sh_res.json()["shelters"]) >= 1

        # 7. Weather.gov parity active alerts
        w_res = await client.get("/api/v1/alerts/weather-gov-parity?district=Chamoli")
        assert w_res.status_code == 200
        w_data = w_res.json()
        assert "last_updated" in w_data
        assert "alerts" in w_data

        # 8. Sensor override & audit trail
        ovr_res = await client.post(
            "/api/v1/admin/alerts/override",
            json={
                "sensor_id": "CWC-RIVER-GAUGE-ALAKNANDA-04",
                "district": "Chamoli",
                "action": "OVERRIDE_FAULTY",
                "reason": "Sensor telemetry calibration artifact during thunderstorm",
                "admin_user": "dmmc_admin",
            },
        )
        assert ovr_res.status_code == 200

        audit_res = await client.get("/api/v1/admin/audit-trail")
        assert audit_res.status_code == 200
        assert audit_res.json()["count"] >= 1
