"""
UKIS 2026 Problem Statement P-011: Differentiation Layer Automated Tests
Validates Tier 1, 2, and 3 capabilities:
- Automatic tiered SMS dispatch with anti-alert-fatigue constraint
- Dijkstra-embedded nearest safe shelter + escape route in SMS payload
- Alert calibration & track-record metrics (Anti-Cry-Wolf)
- Cascading upstream-to-downstream hydraulic wave model
- Physical siren / relay actuation trigger
- Edge-AI sensor node telemetry preprocessor
- Generative AI Commander Assistant (SOP-grounded)
- Bluetooth / offline store-and-forward relay packet generator
"""

import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app


@pytest.mark.asyncio
async def test_tiered_sms_dispatch_escalation_and_embedded_route():
    """Validates that a tier increase from Green to Orange triggers SMS with embedded route and shelter."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "station_id": "UK-CHAMOLI-01",
            "new_tier": "ORANGE",
            "trigger_reason": "Rainfall intensity 38mm/hr crossed IMD Orange threshold (30mm/hr)",
            "water_depth_m": 0.65,
            "blocked_road_name": "Valley Riparian Track",
            "mode": "HISTORICAL_REPLAY",
        }
        res = await client.post("/api/v1/mountain/alerts/tiered-dispatch", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "SUCCESS_DISPATCHED"
        assert data["tier"] == "ORANGE"
        assert "SMS" in data["channels_dispatched"]
        assert data["assigned_safe_shelter"] is not None
        assert data["embedded_safe_route"] is not None
        assert "Safe point:" in data["plain_text_sms_preview"]
        assert "Route: via" in data["plain_text_sms_preview"]


@pytest.mark.asyncio
async def test_tiered_sms_anti_fatigue_suppression():
    """Validates that repeating the same tier or decreasing tier does NOT re-trigger SMS (eliminates alert fatigue)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "station_id": "UK-CHAMOLI-01",
            "new_tier": "ORANGE",  # Already at ORANGE from previous test
            "trigger_reason": "Steady rain continuing",
            "mode": "HISTORICAL_REPLAY",
        }
        res = await client.post("/api/v1/mountain/alerts/tiered-dispatch", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ALERT_SUPPRESSED_NO_TIER_INCREASE_OR_LOW_SEVERITY"


@pytest.mark.asyncio
async def test_tiered_sms_critical_escalation_triggers_siren():
    """Validates that escalating from Orange to RED triggers the physical siren actuator."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "station_id": "UK-CHAMOLI-01",
            "new_tier": "RED",
            "trigger_reason": "Cloudburst surge detected: 112mm/hr with lake breach wave",
            "mode": "HISTORICAL_REPLAY",
        }
        res = await client.post("/api/v1/mountain/alerts/tiered-dispatch", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "SUCCESS_DISPATCHED"
        assert data["tier"] == "RED"
        assert data["siren_actuated"] is True
        assert "PHYSICAL_SIREN_120DB" in data["channels_dispatched"]


@pytest.mark.asyncio
async def test_alert_calibration_track_record():
    """Validates that calibration metrics surface precision, false alarms, and historical ground truth."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/mountain/alerts/calibration")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "SUCCESS"
        assert "precision_percentage" in data
        assert "false_alarm_ratio_percentage" in data
        assert data["total_alerts_issued"] >= 2
        assert len(data["recent_audit_log"]) >= 2


@pytest.mark.asyncio
async def test_cascading_hazard_propagation():
    """Validates upstream-to-downstream wave cascade computation for Chamoli valley."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/mountain/hazard/cascade?station_id=UK-CHAMOLI-01")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "SUCCESS"
        assert data["district"] == "Chamoli"
        assert "cumulative_downstream_impact_index" in data
        assert "projected_downstream_surge_arrival_mins" in data
        assert len(data["upstream_chain_nodes"]) > 0


@pytest.mark.asyncio
async def test_physical_siren_trigger_endpoints():
    """Validates both the router endpoint and root specification alias /alerts/critical/trigger-siren."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Route 1: Internal API
        res1 = await client.post("/api/v1/mountain/alerts/siren/trigger", json={"station_id": "UK-CHAMOLI-01", "alert_level": "CRITICAL"})
        assert res1.status_code == 200
        assert "station_id" in res1.json()

        # Route 2: Direct spec endpoint
        res2 = await client.post("/alerts/critical/trigger-siren", json={"station_id": "UK-CHAMOLI-01", "district": "Chamoli"})
        assert res2.status_code == 200
        assert "station_id" in res2.json()


@pytest.mark.asyncio
async def test_edge_ai_sensor_node_preprocessing():
    """Validates edge sensor compression and anomaly scoring."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "station_id": "UK-CHAMOLI-01",
            "vibration_rms_g": 0.095,
            "acoustic_db": 74.2,
            "pore_pressure_kpa": 165.0,
            "raw_sample_count": 1000,
        }
        res = await client.post("/api/v1/mountain/edge/process-telemetry", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["bandwidth_reduction_pct"] == 98.4
        assert "edge_anomaly_score" in data
        assert data["summary_packet_bytes"] == 64


@pytest.mark.asyncio
async def test_generative_ai_commander_assistant():
    """Validates SOP-grounded natural-language query resolution without hallucination."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "station_id": "UK-CHAMOLI-01",
            "query": "What is the safest evacuation route and shelter for Joshimath if the gorge road floods?",
        }
        res = await client.post("/api/v1/mountain/commander/query", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "SUCCESS"
        assert "COMMANDER DIRECTIVE" in data["grounded_response"]
        assert "verified_shelter" in data
        assert "verified_route" in data
        assert "USDMA Mountain Disaster Standard Operating Procedures" in data["grounded_sop_citation"]


@pytest.mark.asyncio
async def test_bluetooth_offline_relay_packet():
    """Validates Bluetooth one-hop store-and-forward packet generation."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "station_id": "UK-CHAMOLI-01",
            "message": "CRITICAL: Evacuate immediately to Joshimath Cantonment High-Ground Shelter.",
        }
        res = await client.post("/api/v1/mountain/offline-relay/packet", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["protocol"] == "BLE-HIMALAYAN-RELAY-v1"
        assert data["max_hops_ttl"] == 2
        assert "cryptographic_signature" in data
        assert "packet_id" in data
