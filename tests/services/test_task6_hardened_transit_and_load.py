"""
Comprehensive Test Suite for UKIS Task 6 (Hardened):
Transit Graph Network, Dynamic Transient Population Risk Layer, and Offline Mesh Sync.

Sub-tasks tested:
1. 6.1 Network Graph & Topological Reachability Engine (Single Graph, 3-State Fail-Visibly: connected, isolated, unmapped)
2. 6.2 Dynamic Transient Population Load Layer (Char Dham Yatra proxy, capped at MAX_LOAD_MULTIPLIER = 4.5)
3. 6.3 Compressed Offline State Synchronization (base64+gzip decompression, strict schema, clock drift check, conflict resolution)
4. REST API Endpoint Contracts (/api/v1/villages/isolated, /api/v1/analytics/dynamic-load, /api/v1/sync/mesh-packet, /api/v1/sync/mesh-reports)
"""

from __future__ import annotations

import base64
import gzip
import json
from datetime import datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.evacuation_routing import dynamic_evacuation_router
from backend.services.last_mile_resilience import build_evacuation_sms
from backend.services.dynamic_population_load import (
    MAX_LOAD_MULTIPLIER,
    compute_resource_requirement,
    dynamic_population_service,
)
from backend.services.mesh_sync import (
    mesh_sync_service,
    MeshPacketInput,
    CitizenStatusRecord,
    MAX_FUTURE_CLOCK_DRIFT_HOURS,
)

client = TestClient(app)


# ===========================================================================
# 6.1 Unified Network Graph & Topological Isolation Tests
# ===========================================================================

def test_unified_single_graph_service_exists():
    """Verify that only a single graph service exists and manages nodes & edges."""
    assert dynamic_evacuation_router is not None
    assert len(dynamic_evacuation_router.nodes) >= 5
    assert len(dynamic_evacuation_router.edges) >= 4


def test_topological_reachability_three_states():
    """
    UKIS Section 6.1: Reachability must classify settlements into 3 distinct states:
    1. 'connected' (path exists to at least one hub)
    2. 'isolated' (in graph, but all paths to hubs blocked)
    3. 'unmapped' (no edges mapped in OSM extract - fail-visibly, never assumed connected)
    """
    # Evaluate isolation with critical ingress roads blocked
    eval_result = dynamic_evacuation_router.evaluate_lifeline_isolation(
        blocked_road_names=["Mana-Joshimath Transit Link", "Raini-Tapovan Lifeline Bridge"]
    )

    assert eval_result["total_villages_evaluated"] >= 3
    assert "isolated_villages" in eval_result
    assert "connected_villages" in eval_result
    assert "unmapped_villages" in eval_result

    # Check unmapped village (fail-visibly rule)
    unmapped_list = eval_result["unmapped_villages"]
    assert len(unmapped_list) >= 1
    unmapped_ids = [v["village_node_id"] for v in unmapped_list]
    assert "UK_VIL_UNMAPPED_MALARI" in unmapped_ids

    unmapped_entry = next(v for v in unmapped_list if v["village_node_id"] == "UK_VIL_UNMAPPED_MALARI")
    assert unmapped_entry["connectivity_state"] == "unmapped"
    assert unmapped_entry["evacuation_status"] == "UNMAPPED_EDGE_DATA_GAP"
    assert "No road network edges mapped" in unmapped_entry["isolation_reason"]

    # Check isolated village
    isolated_list = eval_result["isolated_villages"]
    assert len(isolated_list) >= 1
    isolated_entry = isolated_list[0]
    assert isolated_entry["connectivity_state"] == "isolated"
    assert isolated_entry["is_isolated"] is True
    assert isolated_entry["needs_airlift"] is True
    assert "isolation_reason" in isolated_entry
    assert "isolation_last_checked" in isolated_entry


def test_isolated_village_alert_sms_text():
    """
    UKIS Section 6.1 Alert Payload requirement:
    When is_isolated = True, alert text must explicitly state:
    'ISOLATED — no ground route exists. Move to high ground immediately. Airborne rescue & pre-positioned relief alerted.'
    """
    sms_text = build_evacuation_sms(
        village_name="Mana Settlement",
        safe_haven_name="Govt Inter College Elevated Campus",
        direction="NE",
        is_isolated=True,
    )
    assert "ISOLATED — no ground route exists" in sms_text
    assert "Airborne rescue & pre-positioned relief alerted" in sms_text


def test_api_villages_isolated_three_states():
    """
    GET /api/v1/villages/isolated returns the full list of settlements with connectivity_state.
    """
    response = client.get("/api/v1/villages/isolated")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3

    states = {v["connectivity_state"] for v in data}
    assert "connected" in states
    assert "unmapped" in states
    # Verify all records have isolation timestamps and reasons
    assert all("isolation_last_checked" in v for v in data)
    assert all("connectivity_state" in v for v in data)


def test_api_villages_isolated_only_filter():
    """
    GET /api/v1/villages/isolated?isolated_only=true returns only isolated settlements.
    """
    response = client.get("/api/v1/villages/isolated?isolated_only=true")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for v in data:
        assert v["connectivity_state"] == "isolated"


# ===========================================================================
# 6.2 Dynamic Transient Population Load Layer Tests
# ===========================================================================

def test_compute_resource_requirement_scaling_and_caps():
    """
    UKIS Section 6.2: compute_resource_requirement
    - Non-zero static population enforced.
    - Never applies multiplier below 1.0 (dynamic load augments, never reduces).
    - Capped at MAX_LOAD_MULTIPLIER (4.5) to avoid absurd resource numbers.
    """
    base_kits = 50
    static_pop = 2500

    # 1. Reject zero static population
    with pytest.raises(ValueError, match="static_population must be a real, non-zero census figure"):
        compute_resource_requirement(base_kits, 0, 1000)

    # 2. Transient load less than census: multiplier never below 1.0
    result_low = compute_resource_requirement(base_kits, static_pop, 1200)
    assert result_low == 50.0

    # 3. Transient surge 2.0x
    result_surge = compute_resource_requirement(base_kits, static_pop, 5000)
    assert result_surge == 100.0

    # 4. Extreme surge 8.0x: must cap at MAX_LOAD_MULTIPLIER (4.5x)
    result_capped = compute_resource_requirement(base_kits, static_pop, 20000)
    assert result_capped == round(base_kits * MAX_LOAD_MULTIPLIER, 2)
    assert result_capped == 225.0


def test_dynamic_population_service_corridor_surges():
    """
    Verify DynamicPopulationLoadService calculates realistic Char Dham surges
    with required load_data_source and load_last_updated metadata.
    """
    village_load = dynamic_population_service.calculate_village_dynamic_load(
        village_id="UK_VIL_JOSHIMATH",
        village_name="Joshimath Cantonment",
        district="Chamoli",
        census_population=16709,
    )

    assert village_load.census_population == 16709
    assert village_load.current_estimated_load >= village_load.census_population
    assert village_load.load_multiplier >= 1.0
    assert village_load.load_data_source in ("yatra_registration_live", "yatra_season_multiplier_demo_mode")
    assert village_load.load_last_updated is not None
    assert village_load.is_demo_mode is True


def test_safe_haven_dynamic_provisioning_scaling():
    """
    Verify safe haven provisioning scales medical kits (1/50) and rations (0.002 tons/person)
    accurately with the dynamic load.
    """
    haven = dynamic_population_service.calculate_haven_provisioning(
        shelter_id="UK_SHELTER_TEST",
        shelter_name="Joshimath High-Ground Cantonment",
        district="Chamoli",
        catchment_static_population=5000,
        custom_load=15000,  # 3.0x load surge
    )

    assert haven.static_census_population == 5000
    assert haven.current_estimated_load == 15000
    assert haven.load_multiplier == 3.0
    assert haven.baseline_medical_kits == 100  # 5000 / 50
    assert haven.medical_kits_needed == 300   # 100 * 3.0
    assert haven.baseline_rations_tons == 10.0 # 5000 * 0.002
    assert haven.rations_tons == 30.0          # 10.0 * 3.0
    assert haven.load_data_source == "yatra_season_multiplier_demo_mode"


def test_api_dynamic_load_summary():
    """
    GET /api/v1/analytics/dynamic-load returns complete operational summary.
    """
    response = client.get("/api/v1/analytics/dynamic-load")
    assert response.status_code == 200
    data = response.json()

    assert "summary_title" in data
    assert "villages_load" in data
    assert "safe_havens_provisioning" in data
    assert data["max_load_multiplier_cap"] == MAX_LOAD_MULTIPLIER
    assert len(data["villages_load"]) >= 1
    assert len(data["safe_havens_provisioning"]) >= 1

    haven = data["safe_havens_provisioning"][0]
    assert "medical_kits_needed" in haven
    assert "rations_tons" in haven
    assert "load_data_source" in haven


# ===========================================================================
# 6.3 Compressed Offline State Synchronization Tests
# ===========================================================================

def test_decode_mesh_packet_decompression():
    """
    Verify decode_mesh_packet performs base64 decode and gzip decompression.
    """
    raw_records = [
        {"village_id": "UK_VIL_01", "status_code": "ROAD_BLOCKED", "timestamp": "2026-09-14T10:00:00Z"},
        {"village_id": "UK_VIL_02", "status_code": "MEDICAL_CRITICAL", "timestamp": "2026-09-14T10:05:00Z"},
    ]
    json_bytes = json.dumps(raw_records).encode("utf-8")
    compressed = gzip.compress(json_bytes)
    payload_b64 = base64.b64encode(compressed).decode("utf-8")

    decompressed = mesh_sync_service.decode_mesh_packet(payload_b64)
    assert decompressed == raw_records


def test_decode_mesh_packet_rejects_corrupt_data():
    """Verify invalid payloads fail visibly with explicit ValueError."""
    # Bad Base64
    with pytest.raises(ValueError, match="Invalid Base64"):
        mesh_sync_service.decode_mesh_packet("not-valid-base-64!!!")

    # Valid Base64 but not gzip
    not_gzip_b64 = base64.b64encode(b"hello raw text").decode("utf-8")
    with pytest.raises(ValueError, match="Failed to decompress gzip"):
        mesh_sync_service.decode_mesh_packet(not_gzip_b64)


def test_mesh_packet_conflict_resolution():
    """
    UKIS Section 6.3: Conflict Resolution
    Incoming report overwrites existing record only when incoming report_timestamp > existing.
    Stale incoming report (timestamp <= existing) is discarded.
    """
    now = datetime.now(timezone.utc)
    t_older = (now - timedelta(hours=2)).isoformat()
    t_newer = (now - timedelta(minutes=15)).isoformat()

    # Ingest newer report first
    packet_newer = mesh_sync_service.create_sample_mesh_packet(
        device_id="SDRF-RELAY-A",
        records=[{
            "village_id": "UK_VIL_CONFLICT_TEST",
            "status_code": "EVACUATION_COMPLETE",
            "status_code_category": "CIVILIAN_SAFETY",
            "timestamp": t_newer,
            "field_notes": "All 120 residents moved to shelter.",
        }],
    )
    res_newer = mesh_sync_service.process_mesh_packet(packet_newer)
    assert res_newer.status == "SUCCESS"
    assert res_newer.successfully_synced_count == 1

    # Attempt to ingest older report for the same category
    packet_older = mesh_sync_service.create_sample_mesh_packet(
        device_id="SDRF-RELAY-B",
        records=[{
            "village_id": "UK_VIL_CONFLICT_TEST",
            "status_code": "EVACUATION_IN_PROGRESS",
            "status_code_category": "CIVILIAN_SAFETY",
            "timestamp": t_older,
            "field_notes": "Older stale report from earlier in the morning.",
        }],
    )
    res_older = mesh_sync_service.process_mesh_packet(packet_older)
    # Stale record should be discarded without error
    assert res_older.successfully_synced_count == 0

    # Verify current state in memory retained the newer status code
    recent = mesh_sync_service.list_recent_synced_reports()
    report = next(r for r in recent if r.village_id == "UK_VIL_CONFLICT_TEST")
    assert report.status_code == "EVACUATION_COMPLETE"
    assert report.report_timestamp == t_newer


def test_mesh_packet_clock_drift_anomaly_detection():
    """
    UKIS Section 6.3 Clock Drift Caveat:
    Packet timestamps > 2 hours in the future are flagged as CLOCK_DRIFT_SUSPECT.
    """
    drifted_future_time = (datetime.now(timezone.utc) + timedelta(hours=5)).isoformat()

    packet = mesh_sync_service.create_sample_mesh_packet(
        device_id="SDRF-DRIFTED-DEVICE-99",
        records=[{
            "village_id": "UK_VIL_DRIFT_TEST",
            "status_code": "WATER_POTABLE_OK",
            "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat(),
        }],
        packet_timestamp_iso=drifted_future_time,
    )
    result = mesh_sync_service.process_mesh_packet(packet)
    assert result.is_clock_drift_detected is True
    assert result.synced_reports[0].is_clock_drift_suspect is True


def test_api_mesh_sync_and_reports_endpoint():
    """
    POST /api/v1/sync/mesh-packet and GET /api/v1/sync/mesh-reports.
    """
    packet = mesh_sync_service.create_sample_mesh_packet(
        device_id="SDRF-API-TEST-DEVICE",
        records=[{
            "village_id": "UK_VIL_API_TEST",
            "status_code": "BRIDGE_DAMAGED",
            "status_code_category": "INFRASTRUCTURE",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "field_notes": "SDRF team on site.",
        }],
    )

    # POST packet
    post_res = client.post("/api/v1/sync/mesh-packet", json=packet.model_dump())
    assert post_res.status_code == 200
    res_data = post_res.json()
    assert res_data["status"] == "SUCCESS"
    assert res_data["successfully_synced_count"] == 1

    # GET reports feed
    get_res = client.get("/api/v1/sync/mesh-reports")
    assert get_res.status_code == 200
    feed = get_res.json()
    assert isinstance(feed, list)
    assert len(feed) >= 1

    matching = next(r for r in feed if r["village_id"] == "UK_VIL_API_TEST")
    assert matching["device_id"] == "SDRF-API-TEST-DEVICE"
    assert matching["is_offline_origin"] is True
    assert "report_timestamp" in matching
    assert "synced_at" in matching
    assert "sync_lag_seconds" in matching
