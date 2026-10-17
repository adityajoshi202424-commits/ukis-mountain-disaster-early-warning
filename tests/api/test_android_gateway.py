"""
Unit & Integration Tests for Android SMS Gateway & Provider Registry
Validates:
- Android mobile device registration
- Emergency SMS queuing and pending pull
- Android SmsManager delivery receipt acknowledgment
- Queue telemetry status
- Provider registry including GloFAS and Elevation DEM
- Minimal alert sync without hardcoded mock records
"""

import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app
from backend.data.providers.registry import provider_registry


@pytest.mark.asyncio
async def test_android_device_registration_and_listing():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        reg_payload = {
            "device_id": "TEST-ANDROID-01",
            "device_model": "Samsung Galaxy XCover 6 Pro (Disaster Rugged)",
            "android_version": "Android 14 (API 34)",
            "sim_carrier": "BSNL Mobile UK",
            "sim_slot_count": 2,
            "battery_pct": 87,
            "signal_strength_bars": 4,
            "app_version": "1.0.0",
        }
        res = await client.post("/api/v1/telecom/android-gateway/register", json=reg_payload)
        assert res.status_code == 200
        data = res.json()
        assert data["device_id"] == "TEST-ANDROID-01"
        assert data["is_active"] is True
        assert data["sim_carrier"] == "BSNL Mobile UK"

        # List devices
        list_res = await client.get("/api/v1/telecom/android-gateway/devices")
        assert list_res.status_code == 200
        devices = list_res.json()
        assert any(d["device_id"] == "TEST-ANDROID-01" for d in devices)


@pytest.mark.asyncio
async def test_android_sms_dispatch_queue_and_acknowledgment():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Dispatch/enqueue an emergency alert
        dispatch_payload = {
            "recipient_phone": "+919876543210",
            "message": "EMERGENCY ALERT: Landslide risk detected near Joshimath. Evacuate immediately to high ground.",
            "target_community": "Chamoli_Joshimath_Sector",
            "hazard_tier": "CRITICAL",
            "safe_shelter": "Govt Inter College Elevated Campus",
            "route_direction": "N",
        }
        dispatch_res = await client.post("/api/v1/telecom/android-gateway/dispatch", json=dispatch_payload)
        assert dispatch_res.status_code == 200
        sms = dispatch_res.json()
        sms_id = sms["sms_id"]
        assert sms["status"] == "QUEUED"
        assert sms["recipient_phone"] == "+919876543210"

        # 2. Android device pulls pending tasks
        pull_res = await client.get(f"/api/v1/telecom/android-gateway/pending?device_id=TEST-ANDROID-01&limit=5")
        assert pull_res.status_code == 200
        tasks = pull_res.json()
        matching = [t for t in tasks if t["sms_id"] == sms_id]
        assert len(matching) == 1
        assert matching[0]["status"] == "IN_TRANSIT"
        assert matching[0]["device_id"] == "TEST-ANDROID-01"

        # 3. Android device reports delivery receipt
        ack_payload = {
            "sms_id": sms_id,
            "device_id": "TEST-ANDROID-01",
            "status": "DELIVERED",
            "carrier_message_ref": "CELL-BSNL-998877",
            "delivered_at": "2026-09-17T18:30:00Z",
        }
        ack_res = await client.post("/api/v1/telecom/android-gateway/ack", json=ack_payload)
        assert ack_res.status_code == 200
        ack_data = ack_res.json()
        assert ack_data["status"] == "SUCCESS"
        assert ack_data["delivery_status"] == "DELIVERED"

        # 4. Check queue telemetry
        queue_res = await client.get("/api/v1/telecom/android-gateway/queue")
        assert queue_res.status_code == 200
        q_data = queue_res.json()
        assert q_data["status"] == "ONLINE"
        assert q_data["metrics"]["delivered"] >= 1


@pytest.mark.asyncio
async def test_minimal_alert_sync_has_no_hardcoded_dummy_data():
    """Verify minimal alert sync returns empty list or authentic records, never fake ALT-CHAMOLI-01."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/sync/alerts/minimal")
        assert res.status_code == 200
        alerts = res.json()
        assert isinstance(alerts, list)
        # Ensure hardcoded fake alert from before is NOT injected
        if not alerts:
            assert alerts == []
        else:
            for item in alerts:
                # Should not have the old static seed
                assert item[0] != "ALT-CHAMOLI-01" or item[1] != "CRITICAL"


@pytest.mark.asyncio
async def test_real_provider_registry_initialization():
    """Verify ProviderRegistry initializes real public providers including GloFAS and Elevation."""
    await provider_registry.initialize()
    providers = provider_registry.list_providers()
    provider_names = [p["name"] for p in providers]

    assert "open_meteo" in provider_names
    assert "glofas_flood" in provider_names
    assert "open_meteo_elevation" in provider_names
    assert "usgs_earthquakes" in provider_names
    assert "osm" in provider_names
