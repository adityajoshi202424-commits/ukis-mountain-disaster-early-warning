"""
Unit & Integration Tests for SIH PS #192 Engine Router
Validates the 5 Core Requirements: Stations, Replay, Cascade, Evacuate, and CAP Broadcast
"""

import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app


@pytest.mark.asyncio
async def test_get_all_stations():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/stations")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "SUCCESS"
        assert "STN-001" in data["stations"]
        assert data["stations"]["STN-001"]["district"] == "Chamoli"


@pytest.mark.asyncio
async def test_process_chronologic_replay():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "station_id": "STN-001",
            "target_time": "2026-08-31T14:30:00Z",
        }
        res = await client.post("/api/v1/hydrometrics/replay", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["station_id"] == "STN-001"
        assert data["rate_of_rise_m_per_hr"] == 0.58
        assert data["alert_level"] == "RED"
        assert data["ndma_hex_color"] == "#EF4444"


@pytest.mark.asyncio
async def test_calculate_cascade_propagation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "upstream_district": "Chamoli",
            "initial_surge_cumecs": 4500.0,
            "elapsed_hours": 3.5,
        }
        res = await client.post("/api/v1/hydrometrics/cascade", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["upstream_district"] == "Chamoli"
        assert data["downstream_district"] == "Rudraprayag"
        assert data["transmitted_surge_cumecs"] < 4500.0
        assert data["attenuation_factor_score"] > 0.0


@pytest.mark.asyncio
async def test_get_profile_aware_route_citizen():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/routing/evacuate?profile=CITIZEN")
        assert res.status_code == 200
        data = res.json()
        assert data["profile"] == "CITIZEN"
        assert data["status"] in ["OPTIMAL_PATH_FOUND", "PATH_BLOCKED_ALL_CHANNELS_SUBMERGED_OR_FULL"]


@pytest.mark.asyncio
async def test_generate_cap_and_vernacular_feeds():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/alerts/broadcast?incident_id=INC-2026-009")
        assert res.status_code == 200
        data = res.json()
        assert "<identifier>INC-2026-009</identifier>" in data["cap_xml"]
        assert "Hindi" in data["vernacular_sms"]
        assert "Garhwali" in data["vernacular_sms"]
        assert "Kumaoni" in data["vernacular_sms"]
        assert "Jaunsari" in data["vernacular_sms"]
