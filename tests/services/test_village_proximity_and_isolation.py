"""
Tests for UKIS Section 3.2b:
1. Village-Proximity Escalation:
   - Uninhabited ridge slip: retained at computed severity as operational-monitoring item (public alert suppressed).
   - Slip above/upstream of a village settlement: escalates alert tier to RED_ALERT (underlying physical risk score is NOT inflated).
2. Isolated-Village Lifeline Flagging:
   - Blocked road/bridge segment cutting off all ground routes: flags village as isolated (needs_airlift = True, AIRLIFT_PREPOSITIONED_SUPPLIES).
   - Blocked road with viable ground detour: flags village as connected (needs_airlift = False).
"""

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.geospatial_action import evaluate_proximity_escalation
from backend.services.evacuation_routing import dynamic_evacuation_router


client = TestClient(app)


# ---------------------------------------------------------------------------
# Section 3.2b Rule 1: Village-Proximity Escalation Tests
# ---------------------------------------------------------------------------

def test_uninhabited_ridge_slip_suppresses_public_alert_retains_score():
    """
    An uninhabited ridge slipping is a data point:
    Retained at its computed severity as an operational-monitoring item, not a public alert.
    """
    physical_score = 0.58
    physical_tier = "ORANGE"

    # High uninhabited ridge coordinates far from any settlement centroid
    result = evaluate_proximity_escalation(
        physical_risk_score=physical_score,
        physical_tier=physical_tier,
        hazard_lat=31.2500,
        hazard_lon=78.1500,
        hazard_elev_m=4600.0,
    )

    # Underlying physical score must be preserved without inflation
    assert result["physical_risk_score"] == physical_score
    assert result["physical_tier"] == "ORANGE"
    # Stays as operational monitoring item, NOT public alert
    assert result["is_public_alert"] is False
    assert result["alert_scope"] == "OPERATIONAL_MONITORING"
    assert result["operational_alert_tier"] == "ORANGE"
    assert result["escalation_triggered"] is False
    assert result["downslope_settlements_count"] == 0
    assert "Uninhabited terrain / ridge slip" in result["operational_summary"]


def test_hazard_above_village_escalates_to_red_alert_without_inflating_physical_score():
    """
    The same hazard flagged above or upstream of a village settlement escalates
    the alert tier to RED_ALERT, but does NOT alter the underlying physical risk score.
    """
    physical_score = 0.58
    physical_tier = "ORANGE"

    # Hazard centroid 475m directly above Joshimath village centroid
    result = evaluate_proximity_escalation(
        physical_risk_score=physical_score,
        physical_tier=physical_tier,
        hazard_lat=30.5630,
        hazard_lon=79.5660,
        hazard_elev_m=2350.0,  # Joshimath is at 1875m, so +475m upslope
    )

    # Critical check: physical score remains strictly uninflated
    assert result["physical_risk_score"] == physical_score
    assert result["physical_tier"] == "ORANGE"

    # Operational tier is escalated to RED_ALERT because of village downslope proximity
    assert result["operational_alert_tier"] == "RED_ALERT"
    assert result["is_public_alert"] is True
    assert result["alert_scope"] == "PUBLIC_EMERGENCY"
    assert result["escalation_triggered"] is True
    assert result["downslope_settlements_count"] >= 1

    settlement_names = [s["village_name"] for s in result["downslope_settlements"]]
    assert "Joshimath" in settlement_names
    assert "VILLAGE-PROXIMITY ESCALATION" in result["operational_summary"]


# ---------------------------------------------------------------------------
# Section 3.2b Rule 2: Isolated-Village Lifeline Flagging Tests
# ---------------------------------------------------------------------------

def test_blocked_lifeline_bridge_triggers_isolated_airlift_flag():
    """
    When a road or bridge segment is marked blocked/washed out and NO ground route remains,
    the village is explicitly flagged as isolated, requiring airlift / pre-positioned supplies.
    """
    # Block the solitary lifeline bridge connecting Raini Village across the gorge
    eval_result = dynamic_evacuation_router.evaluate_lifeline_isolation(
        blocked_road_names=["Raini-Tapovan Lifeline Bridge"]
    )

    assert eval_result["isolated_count"] >= 1
    assert eval_result["airlift_required"] is True

    isolated_names = [v["village_name"] for v in eval_result["isolated_villages"]]
    assert "Raini Village (Rishiganga)" in isolated_names

    raini_record = next(v for v in eval_result["isolated_villages"] if "Raini" in v["village_name"])
    assert raini_record["is_isolated"] is True
    assert raini_record["needs_airlift"] is True
    assert raini_record["response_protocol"] == "AIRLIFT_PREPOSITIONED_SUPPLIES"
    assert raini_record["evacuation_status"] == "CUT_OFF_NO_GROUND_ROUTE"
    assert "Airborne supply drop required" in raini_record["isolation_reason"]


def test_blocked_road_with_ground_detour_is_not_flagged_isolated():
    """
    If a road is blocked but an alternative ground route exists, the village is
    NOT isolated (needs_airlift = False), distinguishing harder to reach from cut-off.
    """
    # Block one secondary road (Valley Riparian Track), but Auli Ascent Road remains open
    eval_result = dynamic_evacuation_router.evaluate_lifeline_isolation(
        blocked_road_names=["Valley Riparian Track"],
        target_village_ids=["UK_HUB_01"],
    )

    assert eval_result["isolated_count"] == 0
    assert len(eval_result["connected_villages"]) == 1

    hub_record = eval_result["connected_villages"][0]
    assert hub_record["is_isolated"] is False
    assert hub_record["needs_airlift"] is False
    assert hub_record["response_protocol"] == "GROUND_EVACUATION"
    assert hub_record["evacuation_status"] == "CONNECTED_PASSABLE"


# ---------------------------------------------------------------------------
# REST API Endpoint Validation Tests
# ---------------------------------------------------------------------------

def test_api_proximity_escalation_endpoint_uninhabited():
    """POST /api/v1/hazards/proximity-escalation endpoint for uninhabited ridge."""
    payload = {
        "physical_risk_score": 0.62,
        "physical_tier": "ORANGE",
        "hazard_latitude": 31.3000,
        "hazard_longitude": 78.1000,
        "hazard_elevation_m": 4500.0,
    }
    response = client.post("/api/v1/hazards/proximity-escalation", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["physical_risk_score"] == 0.62
    assert data["operational_alert_tier"] == "ORANGE"
    assert data["is_public_alert"] is False
    assert data["alert_scope"] == "OPERATIONAL_MONITORING"


def test_api_proximity_escalation_endpoint_village_upslope():
    """POST /api/v1/hazards/proximity-escalation endpoint for hazard above village."""
    payload = {
        "physical_risk_score": 0.62,
        "physical_tier": "ORANGE",
        "hazard_latitude": 30.5630,
        "hazard_longitude": 79.5660,
        "hazard_elevation_m": 2350.0,
    }
    response = client.post("/api/v1/hazards/proximity-escalation", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Physical score untouched
    assert data["physical_risk_score"] == 0.62
    # Alert tier escalated
    assert data["operational_alert_tier"] == "RED_ALERT"
    assert data["is_public_alert"] is True
    assert data["alert_scope"] == "PUBLIC_EMERGENCY"


def test_api_lifelines_evaluate_isolation_endpoint():
    """POST /api/v1/lifelines/evaluate-isolation endpoint."""
    payload = {
        "blocked_roads": ["Raini-Tapovan Lifeline Bridge"],
    }
    response = client.post("/api/v1/lifelines/evaluate-isolation", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["airlift_required"] is True
    assert data["isolated_count"] >= 1
    assert any("Raini" in v["village_name"] for v in data["isolated_villages"])


def test_api_villages_isolated_dashboard_endpoint():
    """GET /api/v1/villages/isolated returns dashboard village states."""
    response = client.get("/api/v1/villages/isolated")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    # Check that connectivity_state is provided
    assert all("connectivity_state" in v for v in data)
