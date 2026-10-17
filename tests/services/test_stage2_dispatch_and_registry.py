"""
Test Suite for Stage 2: DPDP Act 2023 Registry, Multilingual Language Resolution,
and Dual-Channel Alert Dispatch Pipeline.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app
from backend.cap_schema import (
    CapAlertItem,
    AlertSeverity,
    HimalayanHazardType,
    CapArea,
    LocalizedCapInfo,
    SupportedLocale,
)
from backend.services.dpdp_user_registry import user_registry
from backend.services.alert_dispatch_pipeline import alert_dispatch_pipeline


@pytest.fixture(autouse=True)
def clean_registry():
    """Ensure registry has clean state for tests."""
    user_registry._subscribers.clear()


def test_dpdp_user_registry_encryption_and_erasure():
    """Verify phone numbers are encrypted at rest and de-registration permanently erases data."""
    raw_phone = "+919876543210"
    sub = user_registry.register_or_update(
        phone=raw_phone,
        locale="gbm-IN",
        district="Chamoli",
        device_token="tok_test_456",
        lat=30.55,
        lon=79.56,
    )
    # 1. Verify encrypted at rest (not stored as plaintext)
    assert sub.encrypted_phone != raw_phone
    assert len(sub.encrypted_phone) > 20
    assert user_registry.decrypt_phone(sub.encrypted_phone) == raw_phone

    # 2. Verify purpose limitation
    assert sub.purpose == "EMERGENCY_DISASTER_NOTIFICATION_ONLY"

    # 3. Verify lookup
    matches = user_registry.find_subscribers_for_geofence(districts=["Chamoli"])
    assert len(matches) == 1
    assert matches[0].subscriber_id == sub.subscriber_id

    # 4. Verify right to erasure / de-registration
    erased = user_registry.deregister(phone=raw_phone)
    assert erased is True
    assert user_registry.count() == 0


def test_language_resolution_with_fallback_to_hindi():
    """Verify CAP language resolution picks user's language, or falls back to Hindi if missing."""
    mock_alert = CapAlertItem(
        identifier="TEST-CAP-001",
        sender="dmmc@uk.gov.in",
        senderName="DMMC State Control",
        sent="2026-09-17T12:00:00Z",
        hazardType=HimalayanHazardType.FLASH_FLOOD_GLOF,
        severity=AlertSeverity.CRITICAL,
        districts=["Chamoli"],
        area=CapArea(areaDesc="Alaknanda Basin", polygon=[[30.4, 79.4], [30.6, 79.4], [30.6, 79.6], [30.4, 79.6]]),
        effective="2026-09-17T12:00:00Z",
        expires="2026-09-17T18:00:00Z",
        sourceFeed="CWC_GAUGE",
        sourceLastUpdated="2026-09-17T12:00:00Z",
        localized={
            "en-IN": LocalizedCapInfo(
                language=SupportedLocale.EN_IN,
                headline="Flash Flood Watch in Chamoli",
                description="River levels rising.",
                instruction="Move to high ground immediately.",
                senderName="DMMC",
                event="Flash Flood",
            ),
            "hi-IN": LocalizedCapInfo(
                language=SupportedLocale.HI_IN,
                headline="चमोली में आकस्मिक बाढ़ की चेतावनी",
                description="अलकनंदा नदी का जलस्तर खतरे के निशान के करीब।",
                instruction="तुरंत ऊंचे स्थानों पर जाएं।",
                senderName="DMMC",
                event="आकस्मिक बाढ़",
            ),
            "gbm-IN": LocalizedCapInfo(
                language=SupportedLocale.GBM_IN,
                headline="चमोली मा बाढ़ी कु भारी संकट",
                description="अलकनंदा मा पाणी बढ़णू च।",
                instruction="जल्दी से डांडा मा चड़ि जावां।",
                senderName="DMMC",
                event="बाढ़",
            ),
        },
    )

    # User with Garhwali gets Garhwali
    gbm_res = alert_dispatch_pipeline.resolve_alert_text_for_user(mock_alert, "gbm-IN")
    assert "बाढ़ी कु भारी संकट" in gbm_res["title"]

    # User with Kumaoni (not present in localized dict) falls back to Hindi
    kfy_res = alert_dispatch_pipeline.resolve_alert_text_for_user(mock_alert, "kfy-IN")
    assert "चमोली में आकस्मिक बाढ़" in kfy_res["title"]

    # User with English gets English
    en_res = alert_dispatch_pipeline.resolve_alert_text_for_user(mock_alert, "en-IN")
    assert "Flash Flood Watch" in en_res["title"]


@pytest.mark.asyncio
async def test_end_to_end_alert_dispatch_against_mock_cap():
    """Verify dispatch pipeline filters subscribers by geofence, handles dual channels, and writes audit record."""
    # Register subscribers in Chamoli (affected) and Haridwar (not affected)
    user_registry.register_or_update("+919111111111", locale="hi-IN", district="Chamoli", device_token="fcm_tok_1")
    user_registry.register_or_update("+919222222222", locale="gbm-IN", district="Chamoli")
    user_registry.register_or_update("+919333333333", locale="en-IN", district="Haridwar")  # Should not be alerted

    mock_alert = CapAlertItem(
        identifier="IN-UK-CAP-MOCK-2026",
        sender="dmmc@uk.gov.in",
        senderName="DMMC State Control",
        sent="2026-09-17T12:00:00Z",
        hazardType=HimalayanHazardType.FLASH_FLOOD_GLOF,
        severity=AlertSeverity.CRITICAL,
        districts=["Chamoli"],
        area=CapArea(areaDesc="Alaknanda Basin"),
        effective="2026-09-17T12:00:00Z",
        expires="2026-09-17T18:00:00Z",
        sourceFeed="CWC_GAUGE",
        sourceLastUpdated="2026-09-17T12:00:00Z",
        localized={
            "hi-IN": LocalizedCapInfo(
                language=SupportedLocale.HI_IN,
                headline="चमोली में बाढ़ चेतावनी",
                description="desc",
                instruction="instruction",
                senderName="DMMC",
                event="बाढ़",
            ),
        },
    )

    audit = await alert_dispatch_pipeline.process_and_dispatch_cap_alert(mock_alert)
    assert audit["alert_id"] == "IN-UK-CAP-MOCK-2026"
    assert audit["matched_subscribers"] == 2  # Only the 2 Chamoli users, Haridwar excluded
    assert "gateway_statuses" in audit
    assert audit["latency_ms"] >= 0


@pytest.mark.asyncio
async def test_user_and_ops_endpoints():
    """Verify HTTP API endpoints for registration, deregistration, and ops audit view."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. Register user
        reg_res = await client.post(
            "/api/v1/user/register",
            json={"phone": "+919998887776", "locale": "gbm-IN", "district": "Uttarkashi"},
        )
        assert reg_res.status_code == 200
        data = reg_res.json()
        assert data["status"] == "REGISTERED"
        assert data["applied_locale"] == "gbm-IN"

        # 2. Check Ops Delivery Audit endpoint
        ops_res = await client.get("/api/v1/ops/delivery-audit")
        assert ops_res.status_code == 200
        ops_data = ops_res.json()
        assert "total_dispatches" in ops_data

        # 3. Deregister user
        dereg_res = await client.post(
            "/api/v1/user/deregister",
            json={"phone": "+919998887776"},
        )
        assert dereg_res.status_code == 200
        assert dereg_res.json()["status"] == "ERASED"
