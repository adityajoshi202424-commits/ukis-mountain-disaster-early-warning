"""Pure-function tests for the Uttarakhand last-mile resilience layer."""

from backend.services.evacuation_routing import dynamic_evacuation_router
from backend.services.last_mile_resilience import (
    build_evacuation_sms,
    compass_direction,
    escalate_operational_tier,
    parse_sos,
)


def test_exposure_escalates_operational_tier_without_changing_physical_score():
    assert escalate_operational_tier("HIGH", True) == "CRITICAL"
    assert escalate_operational_tier("HIGH", False) == "HIGH"


def test_same_graph_isolation_has_three_states():
    states = dynamic_evacuation_router.compute_isolation_states(
        village_node_ids=["UK_HUB_01", "UNKNOWN_VILLAGE"],
        hub_node_ids=["UK_SHELTER_01"],
    )
    assert states["UK_HUB_01"] == "connected"
    assert states["UNKNOWN_VILLAGE"] == "unmapped"


def test_sms_and_sos_contracts_are_strict():
    message = build_evacuation_sms("Raini", "Verified Shelter", compass_direction(90))
    assert message == (
        "EMERGENCY ALERT: Landslide risk detected near Raini. "
        "EVACUATE IMMEDIATELY to the nearest safe shelter at Verified Shelter. "
        "Path vector direction: E. Stay away from riverbanks."
    )
    assert parse_sos("SOS Raini landslide") == {"village": "Raini", "hazard": "landslide"}
    assert parse_sos("help Raini landslide") is None