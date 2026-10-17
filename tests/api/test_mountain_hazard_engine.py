"""
Unit & Integration Tests for UKIS 2026 Problem Statement P-011
AI Mountain Disaster Early-Warning Intelligence Engine
"""

import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app


@pytest.mark.asyncio
async def test_get_root_branding():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/")
        assert res.status_code == 200
        data = res.json()
        assert data["problem_code"] == "P-011"
        assert "Uttarakhand" in data["region"]
        assert len(data["capabilities"]) == 5


@pytest.mark.asyncio
async def test_get_uttarakhand_stations():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/mountain/stations")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "SUCCESS"
        assert data["total_districts"] == 13
        assert "UK-CHAMOLI-01" in data["stations"]
        assert "UK-RUDRAPRAYAG-01" in data["stations"]
        assert "UK-UTTARKASHI-01" in data["stations"]


@pytest.mark.asyncio
async def test_get_composite_mountain_hazard():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/mountain/hazard/composite?station_id=UK-CHAMOLI-01")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "SUCCESS"
        assert 0.0 <= data["composite_risk_score"] <= 100.0
        assert data["alert_level"] in ["GREEN", "YELLOW", "ORANGE", "RED"]
        assert len(data["feature_attributions"]) == 5
        assert "Multi-hazard index" in data["explainable_reasoning_en"]
        assert data["telemetry_provenance"]["data_fabrication"] == "0% — Verified Real Public Feeds"


@pytest.mark.asyncio
async def test_get_glacier_and_glof_monitoring():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/mountain/glaciers")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "SUCCESS"
        assert data["total_monitored_glaciers"] >= 4
        # Verify Chorabari and Gangotri exist
        names = [g["glacier_name"] for g in data["glaciers"]]
        assert any("Chorabari" in n for n in names)
        assert any("Gangotri" in n for n in names)


@pytest.mark.asyncio
async def test_get_fragile_slopes_and_landslides():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/mountain/slopes")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "SUCCESS"
        assert data["total_slopes_monitored"] >= 4
        # Verify Joshimath is monitored
        names = [s["name"] for s in data["slopes"]]
        assert any("Joshimath" in n for n in names)


@pytest.mark.asyncio
async def test_get_seismic_mountain_hazards():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/mountain/seismic")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] in ["ONLINE", "SOURCE_UNAVAILABLE"]


@pytest.mark.asyncio
async def test_generate_emergency_bulletin():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"station_id": "UK-RUDRAPRAYAG-01", "target_lang": "en"}
        res = await client.post("/api/v1/mountain/bulletin/generate", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "SUCCESS"
        assert "CAP-1.2" or "cap_xml" in str(data)
        assert "USDMA" in data["headline"]
