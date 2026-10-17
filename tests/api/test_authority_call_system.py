"""
Automated Authority Call & Voice Escalation System Tests
Validates:
- Retrieval of official Uttarakhand nodal disaster authorities directory
- Automated voice call dispatch based on hazard analysis
- Twilio / IVR TwiML generation and bilingual briefing construction
- DTMF officer keypad acknowledgment recording
- Tiered auto-escalation integration when hazard reaches Critical/Red
"""

import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app
from backend.services.authority_call_dispatcher import authority_call_dispatcher, AuthorityCallRequest


@pytest.mark.asyncio
async def test_get_authorities_directory():
    """Verify retrieval of official emergency authorities directory."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/alerts/authorities/directory")
        assert res.status_code == 200
        data = res.json()
        assert len(data) >= 8
        agencies = {item["agency"] for item in data}
        assert "SDRF" in agencies
        assert "NDRF" in agencies
        assert "DDMA" in agencies
        assert "SEOC" in agencies


@pytest.mark.asyncio
async def test_get_district_filtered_authorities():
    """Verify district-specific filtering for Chamoli authorities."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/alerts/authorities/directory?district=Chamoli")
        assert res.status_code == 200
        data = res.json()
        assert len(data) >= 5
        for auth in data:
            assert auth["district"] in ("Chamoli", "Statewide")


@pytest.mark.asyncio
async def test_dispatch_authority_emergency_calls():
    """Verify that automated authority voice calls are initiated with bilingual transcripts."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "station_id": "UK-CHAMOLI-01",
            "district": "Chamoli",
            "hazard_type": "FLASH_FLOOD_GLOF",
            "severity": "CRITICAL",
            "rate_of_rise_m_hr": 1.75,
            "rainfall_velocity_mm_hr": 58.0,
            "lead_time_minutes": 25,
            "custom_directive": "Immediate riverbank evacuation and QRT mobilization.",
        }
        res = await client.post("/api/v1/alerts/call-authorities?mode=SIMULATION", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "AUTHORITY_CALLS_DISPATCHED"
        assert data["calls_initiated"] >= 1
        records = data["call_records"]
        assert len(records) >= 1
        rec = records[0]
        assert "PRIORITY EMERGENCY DISPATCH" in rec["spoken_transcript_en"]
        assert "उत्तराखंड आपदा" in rec["spoken_transcript_hi"]
        assert rec["call_status"] in ("SIMULATED_VOICE_CALL_DELIVERED", "LIVE_CALL_CONNECTED")


@pytest.mark.asyncio
async def test_get_authority_call_logs():
    """Verify retrieval of Call Detail Records (CDRs)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/alerts/authorities/call-logs")
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert "call_id" in data[0]
        assert "officer_name" in data[0]


@pytest.mark.asyncio
async def test_officer_call_acknowledgment_webhook():
    """Verify DTMF keypad acknowledgment recording via Twilio webhook."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        form_payload = {"Digits": "1", "CallSid": "CDR-AUTO-HIST-001"}
        res = await client.post(
            "/api/v1/alerts/authorities/call-gather",
            data=form_payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert res.status_code == 200
        assert "Acknowledgment recorded" in res.text
