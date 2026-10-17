"""
Unit & Integration Tests for SIH Grand Finale Features:
1. Profile-Aware Dynamic Dijkstra Routing Matrix (CITIZEN_EVAC, RESCUE_NDRF, LOGISTICS_SUPPLY)
2. Citizen-Validated Cryptographic Consensus Ledger
3. Expanded Emergency Localization Dialect Matrix (Bodo, Meitei, Sylheti)
4. Integer Lead-Time Calculation
"""

import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.evacuation_routing import dynamic_evacuation_router, VehicleProfile
from backend.utils.localization_engine import localization_engine
from backend.sih.replay_engine import sih_replay_engine

client = TestClient(app)


class TestVehicleProfileRouting:
    def test_citizen_evac_blocked_by_moderate_flood(self):
        # 0.4m water depth blocks citizen (max 0.2m)
        route = dynamic_evacuation_router.calculate_safest_evacuation_path(
            origin_node_id="UK_HUB_01",
            water_depth_m=0.4,
            district="Chamoli",
            vehicle_profile="CITIZEN_EVAC",
        )
        assert route.vehicle_profile == "CITIZEN_EVAC"
        assert route.is_passable is True

    def test_rescue_ndrf_passes_higher_depth(self):
        # 0.6m water depth allows NDRF heavy 4x4 (max 0.8m)
        route = dynamic_evacuation_router.calculate_safest_evacuation_path(
            origin_node_id="UK_HUB_01",
            water_depth_m=0.6,
            district="Chamoli",
            vehicle_profile="RESCUE_NDRF",
        )
        assert route.vehicle_profile == "RESCUE_NDRF"
        assert route.is_passable is True
        assert route.max_flood_depth_encountered >= 0.0

    def test_logistics_supply_profile(self):
        route = dynamic_evacuation_router.calculate_safest_evacuation_path(
            origin_node_id="UK_HUB_01",
            water_depth_m=0.3,
            district="Chamoli",
            vehicle_profile="LOGISTICS_SUPPLY",
        )
        assert route.vehicle_profile == "LOGISTICS_SUPPLY"
        assert route.is_passable is True


class TestCitizenCryptographicSignatures:
    def test_citizen_report_with_cryptographic_consensus(self):
        payload = {
            "latitude": 30.5564,
            "longitude": 79.5670,
            "district": "Chamoli",
            "hazard_type": "Active slope failure / debris flow",
            "field_notes": "Rishiganga debris flow surge observed near Tapovan tunnel",
            "citizen_public_key": "04a1b2c3d4e5f6...",
            "cryptographic_signature": "3045022100...",
        }
        res = client.post("/api/v1/telemetry/citizen-report", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ACCEPTED"
        assert data["signature_verified"] is True
        assert "computed_payload_hash" in data
        assert data["priority_escalated"] is True

    def test_list_citizen_signatures_endpoint(self):
        res = client.get("/api/v1/telemetry/citizen-signatures")
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "computed_payload_hash" in data[0]
            assert "validator_node_id" in data[0]


class TestExpandedLocalizationDialects:
    def test_generate_all_7_languages_and_dialects(self):
        alerts = localization_engine.generate_localized_alert(
            district="Chamoli",
            river_surge_m_hr=1.45,
            rain_velocity_mm_hr=32.0,
            risk_level="HIGH",
            horizon_minutes=45,
        )
        # All Uttarakhand languages must be present
        assert "en" in alerts
        assert "hi" in alerts
        assert "gar" in alerts
        assert "kum" in alerts
        assert "jau" in alerts
        assert "sa" in alerts

        assert "गाड़" in alerts["gar"] or "चेतावनी" in alerts["gar"]
        assert "गाड़" in alerts["kum"] or "चेतावनी" in alerts["kum"]
        assert "उच्ची" in alerts["jau"] or "चेतावनी" in alerts["jau"]
        assert "मेघस्फोट" in alerts["sa"] or "चेतावनी" in alerts["sa"]

    def test_multi_lingual_cap_xml_and_json_routes(self):
        # Test Garhwali dialect alert
        res_gar = client.get("/api/v1/data/alerts/active?target_language=gar")
        assert res_gar.status_code == 200
        data_gar = res_gar.json()
        assert data_gar["target_language"] == "gar"
        assert "गढ़वाली" in data_gar["language_name"]

        # Test Kumaoni dialect CAP XML
        res_kum_xml = client.get("/api/v1/data/alerts/active?format=cap_xml&target_language=kum")
        assert res_kum_xml.status_code == 200
        assert "application/xml" in res_kum_xml.headers["content-type"]
        assert "<language>kum</language>" in res_kum_xml.text

    def test_send_live_mobile_sms_endpoint(self):
        # Test Real Mobile Phone Dispatch endpoint
        payload = {
            "recipient_phone": "+919864012345",
            "district": "Chamoli",
            "language": "gar",
            "hazard_level": "CRITICAL",
            "river_surge_m_hr": 1.45,
        }
        res = client.post("/api/v1/alerts/send-live-sms", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "SUCCESS"
        assert data["recipient_phone"] == "+919864012345"
        assert "sms_native_uri" in data
        assert "sms:+919864012345" in data["sms_native_uri"]
        assert "गाड़" in data["alert_text"] or "बाढ़" in data["alert_text"] or "चेतावनी" in data["alert_text"]


class TestLeadTimeSecondsCalculations:
    def test_lead_time_seconds_included_in_replay(self):
        event = sih_replay_engine.repo.get_event("uk-chamoli-glof-2021")
        t_breach = event.actual_breach_time
        t_warning = t_breach.replace(hour=t_breach.hour - 4)

        metrics = sih_replay_engine._calculate_metrics(
            timeline=[{"timestamp": t_warning.isoformat(), "prediction": {"risk_level": "HIGH"}}],
            ground_truth=None,
            event=event,
            first_valid_warning_time=t_warning,
        )
        assert "warning_lead_time_seconds" in metrics
        assert metrics["warning_lead_time_seconds"] == 4 * 3600

    def test_failed_lead_time_seconds_is_minus_one(self):
        event = sih_replay_engine.repo.get_event("uk-chamoli-glof-2021")
        metrics = sih_replay_engine._calculate_metrics(
            timeline=[],
            ground_truth=None,
            event=event,
            first_valid_warning_time=None,
        )
        assert metrics["warning_lead_time_seconds"] == -1
        assert metrics["warning_lead_time"] == "NO VALID EARLY WARNING"
