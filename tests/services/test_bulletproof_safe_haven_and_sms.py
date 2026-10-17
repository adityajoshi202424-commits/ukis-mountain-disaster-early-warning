"""
Comprehensive Test Suite for UKIS Task 5:
Bulletproof Recovery, Nearest Safe Haven Query, Hazard Exclusion, and SMS Broadcast.

Sub-tasks tested:
1. 5.1 Safe Zone Schema & Querying (ST_Distance, ST_Azimuth, and Straight-Line Hazard Zone Exclusion)
2. 5.2 SMS Gateway Dispatcher Engine & Exact Variable Pattern Compliance
3. 5.3 Citizen SOS Inbound Webhook & Regex Extraction (SOS <village> <hazard>)
4. End-to-end Last-Mile Resilience Loop: Space Data -> Earth Logic -> Direct Human Guidance via SMS
"""

from __future__ import annotations

import os
import uuid
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.models import SafeHaven, CitizenPing
from backend.services.last_mile_resilience import (
    SafeHavenResult,
    SmsDispatchResult,
    build_evacuation_sms,
    compass_direction,
    calculate_geodesic_distance_m,
    calculate_azimuth_degrees,
    check_straight_line_hazard_intersection,
    select_nearest_safe_haven_with_exclusion,
    nearest_safe_haven,
    dispatch_sms,
    parse_sos,
    VERIFIED_UTTARAKHAND_VILLAGES,
    DEFAULT_SAFE_HAVENS,
)

client = TestClient(app)


# ===========================================================================
# 5.1 Safe Zone Schema & Model Validation
# ===========================================================================

def test_safe_havens_and_citizen_pings_models_exist():
    """Verify PostGIS tables and SQLAlchemy ORM models have all required columns."""
    # Check SafeHaven columns
    safe_haven_cols = {c.name for c in SafeHaven.__table__.columns}
    assert "id" in safe_haven_cols
    assert "name" in safe_haven_cols
    assert "facility_type" in safe_haven_cols
    assert "geom" in safe_haven_cols
    assert "capacity" in safe_haven_cols

    # Check CitizenPing columns
    ping_cols = {c.name for c in CitizenPing.__table__.columns}
    assert "id" in ping_cols
    assert "village_name" in ping_cols
    assert "reported_hazard" in ping_cols
    assert "geom" in ping_cols
    assert "verified" in ping_cols


# ===========================================================================
# 5.1 Geodesic Mathematics & Compass Azimuth Calculations
# ===========================================================================

def test_compass_direction_octants():
    """Verify conversion of azimuth degrees into 8 cardinal/intercardinal compass directions."""
    assert compass_direction(0.0) == "N"
    assert compass_direction(359.0) == "N"
    assert compass_direction(45.0) == "NE"
    assert compass_direction(90.0) == "E"
    assert compass_direction(135.0) == "SE"
    assert compass_direction(180.0) == "S"
    assert compass_direction(225.0) == "SW"
    assert compass_direction(270.0) == "W"
    assert compass_direction(315.0) == "NW"


def test_geodesic_distance_and_azimuth_accuracy():
    """Verify distance and azimuth calculation between known Himalayan points."""
    # Joshimath (30.5564, 79.5670) to Tapovan (30.4950, 79.6500)
    dist = calculate_geodesic_distance_m(30.5564, 79.5670, 30.4950, 79.6500)
    assert 10000.0 < dist < 14000.0  # Approx 10.4 km line-of-sight

    azimuth = calculate_azimuth_degrees(30.5564, 79.5670, 30.4950, 79.6500)
    assert 100.0 < azimuth < 160.0  # Heading South-East


# ===========================================================================
# 5.1 Straight-Line Hazard Zone Exclusion Function
# ===========================================================================

def test_hazard_zone_straight_line_exclusion():
    """
    UKIS Task 5.1 Exclusion Function:
    If the straight-line vector between village and nearest safe haven intersects
    a calculated hazard polygon, drop that safe haven and automatically fetch
    the next closest valid safe haven point.
    """
    village_coords = (30.5500, 79.5600)  # Origin village

    # Candidate 1: Shelter A (Closer - 500m East)
    shelter_a = {
        "id": "shelter-a-closer",
        "name": "Shelter A (Direct East)",
        "facility_type": "Primary School",
        "latitude": 30.5500,
        "longitude": 79.5660,
    }

    # Candidate 2: Shelter B (Farther - 1200m North)
    shelter_b = {
        "id": "shelter-b-farther",
        "name": "Shelter B (Safe North Ridge)",
        "facility_type": "Community Centre",
        "latitude": 30.5610,
        "longitude": 79.5600,
    }

    # Scenario 1: No hazards - Shelter A (closer) must be chosen
    result_clean = select_nearest_safe_haven_with_exclusion(
        village_id="VIL_TEST_01",
        village_name="Test Village Alpha",
        village_lat=village_coords[0],
        village_lon=village_coords[1],
        candidates=[shelter_a, shelter_b],
        hazard_zones=[],
    )
    assert result_clean is not None
    assert result_clean.safe_haven_name == "Shelter A (Direct East)"
    assert result_clean.compass_direction == "E"

    # Scenario 2: Hazard zone placed directly between Village and Shelter A
    # Polygon covering longitude 79.5620 to 79.5640 across latitude 30.5480 to 30.5520
    blocking_hazard = {
        "hazard_type": "active_debris_flow",
        "polygon_coordinates": [
            [79.5620, 30.5480],
            [79.5640, 30.5480],
            [79.5640, 30.5520],
            [79.5620, 30.5520],
            [79.5620, 30.5480],
        ],
    }

    # Exclusion function must detect intersection with Shelter A and select Shelter B!
    result_excluded = select_nearest_safe_haven_with_exclusion(
        village_id="VIL_TEST_01",
        village_name="Test Village Alpha",
        village_lat=village_coords[0],
        village_lon=village_coords[1],
        candidates=[shelter_a, shelter_b],
        hazard_zones=[blocking_hazard],
    )
    assert result_excluded is not None
    assert result_excluded.safe_haven_name == "Shelter B (Safe North Ridge)"
    assert result_excluded.compass_direction == "N"

    # Scenario 3: Second hazard zone blocks Shelter B as well -> returns None
    second_hazard = {
        "hazard_type": "landslide_chasm",
        "polygon_coordinates": [
            [79.5580, 30.5540],
            [79.5620, 30.5540],
            [79.5620, 30.5580],
            [79.5580, 30.5580],
            [79.5580, 30.5540],
        ],
    }
    result_all_blocked = select_nearest_safe_haven_with_exclusion(
        village_id="VIL_TEST_01",
        village_name="Test Village Alpha",
        village_lat=village_coords[0],
        village_lon=village_coords[1],
        candidates=[shelter_a, shelter_b],
        hazard_zones=[blocking_hazard, second_hazard],
    )
    assert result_all_blocked is None


@pytest.mark.asyncio
async def test_nearest_safe_haven_service_fallback():
    """Verify nearest_safe_haven service method returns safe haven for verified villages."""
    haven_res = await nearest_safe_haven(session=None, village_id="joshimath")
    assert haven_res is not None
    assert "Joshimath" in haven_res.village_name
    assert haven_res.safe_haven_name is not None
    assert haven_res.distance_m > 0.0
    assert haven_res.compass_direction in ("N", "NE", "E", "SE", "S", "SW", "W", "NW")


# ===========================================================================
# 5.2 SMS Gateway Dispatcher & Variable Pattern Compliance
# ===========================================================================

def test_evacuation_sms_exact_variable_pattern():
    """
    UKIS Task 5.2 Strict string requirement:
    'EMERGENCY ALERT: Landslide risk detected near {village_name}. EVACUATE IMMEDIATELY to the nearest safe shelter at {safe_haven_name}. Path vector direction: {compass_direction}. Stay away from riverbanks.'
    """
    village = "Joshimath Central"
    shelter = "Joshimath Cantonment High-Ground Shelter"
    direction = "NE"

    generated_msg = build_evacuation_sms(
        village_name=village,
        safe_haven_name=shelter,
        compass_direction=direction,
    )

    expected_pattern = (
        f"EMERGENCY ALERT: Landslide risk detected near {village}. "
        f"EVACUATE IMMEDIATELY to the nearest safe shelter at {shelter}. "
        f"Path vector direction: {direction}. Stay away from riverbanks."
    )

    assert generated_msg == expected_pattern


@pytest.mark.asyncio
async def test_dispatch_sms_with_dlt_structure():
    """
    Verify dispatch_sms supports Indian DLT template parameters and Twilio REST structure.
    In test environment without API keys, safely returns SOURCE_UNAVAILABLE without crash.
    """
    msg = "EMERGENCY ALERT: Landslide risk detected near Raini. EVACUATE IMMEDIATELY to the nearest safe shelter at Tapovan Disaster Shelter. Path vector direction: SE. Stay away from riverbanks."
    result = await dispatch_sms(
        recipient="+919812345678",
        message=msg,
        dlt_template_id="1107161829304859",
        sender_id="UKSDMA",
    )
    assert isinstance(result, SmsDispatchResult)
    assert result.status in ("SENT", "SOURCE_UNAVAILABLE", "GATEWAY_ERROR")


# ===========================================================================
# 5.3 Citizen SOS Inbound Webhook & Regex Extraction
# ===========================================================================

def test_parse_sos_regex():
    """
    UKIS Task 5.3: Regex parsing:
    SOS (?P<village>[\\w\\s]+) (?P<hazard>landslide|flood|cloudburst)
    """
    # 1. Valid cases
    r1 = parse_sos("SOS Raini landslide")
    assert r1 == {"village": "Raini", "hazard": "landslide"}

    r2 = parse_sos("SOS Joshimath Central flood")
    assert r2 == {"village": "Joshimath Central", "hazard": "flood"}

    r3 = parse_sos("SOS Mana Settlement cloudburst")
    assert r3 == {"village": "Mana Settlement", "hazard": "cloudburst"}

    # Case insensitivity
    r4 = parse_sos("sos bhatwari valley LANDSLIDE")
    assert r4 == {"village": "bhatwari valley", "hazard": "landslide"}

    # 2. Invalid hazard category
    assert parse_sos("SOS Raini earthquake") is None
    assert parse_sos("SOS Raini fire") is None

    # 3. Invalid command prefix
    assert parse_sos("HELP Raini landslide") is None
    assert parse_sos("EMERGENCY Joshimath flood") is None
    assert parse_sos("SOS") is None


def test_api_citizen_sms_webhook():
    """
    POST /api/v1/telecom/sms-webhook:
    Valid SOS message inserts citizen ping, resolves village coordinates,
    and returns sound_trigger = True.
    """
    # Valid SOS for known Uttarakhand village
    response = client.post(
        "/api/v1/telecom/sms-webhook",
        json={"body": "SOS Raini landslide"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "RECEIVED_UNVERIFIED"
    assert data["village_name"] == "Raini Gorge Village"
    assert data["reported_hazard"] == "landslide"
    assert data["sound_trigger"] is True
    assert "ping_id" in data
    assert "coordinates" in data
    assert data["coordinates"]["latitude"] > 0.0

    # Malformed message -> 422
    err_res = client.post(
        "/api/v1/telecom/sms-webhook",
        json={"body": "HELP me quick"},
    )
    assert err_res.status_code == 422

    # Unknown village -> 404
    unmapped_res = client.post(
        "/api/v1/telecom/sms-webhook",
        json={"body": "SOS NonExistentVillageXYZ landslide"},
    )
    assert unmapped_res.status_code == 404


def test_api_safe_haven_and_sms_dispatch_endpoint():
    """
    GET /api/v1/villages/{village_id}/safe-haven and
    POST /api/v1/telecom/sms-dispatch.
    """
    # 1. Query nearest safe haven for Joshimath
    haven_res = client.get("/api/v1/villages/joshimath/safe-haven")
    assert haven_res.status_code == 200
    haven_data = haven_res.json()
    assert "safe_haven_name" in haven_data
    assert "compass_direction" in haven_data
    assert haven_data["distance_m"] > 0

    # 2. Trigger SMS dispatch for village
    dispatch_res = client.post(
        "/api/v1/telecom/sms-dispatch",
        json={
            "village_id": "joshimath",
            "recipient": "+919812345678",
            "isolated": False,
        },
    )
    assert dispatch_res.status_code == 200
    dispatch_data = dispatch_res.json()
    assert "EMERGENCY ALERT: Landslide risk detected" in dispatch_data["message"]
    assert "Path vector direction:" in dispatch_data["message"]
    assert "dispatch" in dispatch_data
