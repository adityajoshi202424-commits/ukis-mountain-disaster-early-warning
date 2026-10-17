"""
Tests for Live Data API Routes (/api/v1/data/*)
Validates Live Hydrology with Redis Buffer & Failover, and Active Alerts with CAP XML
"""

import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app


@pytest.mark.asyncio
async def test_get_current_hydrology_nominal():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/data/hydrology/current?station_id=CWC_GAUGE_JOSHIMATH_01")
        assert response.status_code == 200
        data = response.json()
        assert data["station_id"] == "CWC_GAUGE_JOSHIMATH_01"
        assert data["data_quality"] == "SOURCE_UNAVAILABLE"
        assert data["hydrology"] is None


@pytest.mark.asyncio
async def test_get_current_hydrology_outage_failover():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/data/hydrology/current?station_id=CWC_GAUGE_JOSHIMATH_01&is_cwc_failed=true")
        assert response.status_code == 200
        data = response.json()
        assert data["data_quality"] == "SOURCE_UNAVAILABLE"
        assert data["active_source"] is None
        assert data["hydrology"] is None
        assert len(data["missing_inputs"]) > 0


@pytest.mark.asyncio
async def test_get_active_alerts_json():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/data/alerts/active?mode=HISTORICAL_REPLAY")
        assert response.status_code == 200
        data = response.json()
        assert data["is_sandbox"] is True
        assert "[SIH EVALUATION SANDBOX - DO NOT BROADCAST]" in data["sandbox_notice"]


@pytest.mark.asyncio
async def test_get_active_alerts_cap_xml():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/data/alerts/active?mode=HISTORICAL_REPLAY&format=cap_xml")
        assert response.status_code == 200
        assert "application/xml" in response.headers.get("content-type", "")
        assert "<?xml" in response.text


@pytest.mark.asyncio
async def test_get_live_hydrology_prediction():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/data/hydrology/live-prediction?district=Chamoli&lat=30.5564&lon=79.5670")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "LIVE_OBSERVATION"
        assert data["district"] == "Chamoli"
        assert "live_weather" in data
        assert "live_hydrology" in data
        assert "prediction" in data
        assert "risk_level" in data["prediction"]
        assert "localized_alerts" in data
        assert "en" in data["localized_alerts"]


@pytest.mark.asyncio
async def test_get_nasa_power_rainfall():
    from backend.data.providers.registry import provider_registry
    await provider_registry.initialize()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/data/rainfall/nasa-power?lat=30.3165&lon=78.0322")
        # Either returns 200 with live observations or 200 with OFFLINE status if remote API times out
        assert response.status_code == 200
        data = response.json()
        assert data["provider"] == "NASA POWER"
        assert "observations" in data

