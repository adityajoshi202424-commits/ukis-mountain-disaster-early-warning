"""
Tests for Vernacular Localization, Infrastructure Exposure Analytics, and Citizen Telemetry
"""

import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app
from backend.utils.localization_engine import localization_engine
from backend.services.exposure_analytics import exposure_analytics_service


class TestVernacularLocalization:
    def test_generate_localized_alerts_all_languages(self):
        """Verifies that localization engine outputs valid strings for English, Hindi, Garhwali, Kumaoni, and Sanskrit."""
        alerts = localization_engine.generate_localized_alert(
            district="Chamoli",
            river_surge_m_hr=1.45,
            rain_velocity_mm_hr=35.0,
            risk_level="HIGH",
            horizon_minutes=45,
        )
        assert "en" in alerts
        assert "hi" in alerts
        assert "gar" in alerts
        assert "kum" in alerts
        assert "Chamoli" in alerts["en"]
        assert "बाढ़" in alerts["hi"] or "चेतावनी" in alerts["hi"]
        assert "गाड़" in alerts["gar"] or "चेतावनी" in alerts["gar"]
        assert "गाड़" in alerts["kum"] or "चेतावनी" in alerts["kum"]

    def test_district_primary_vernacular_mapping(self):
        assert localization_engine.get_primary_vernacular_for_district("Chamoli") == "gar"
        assert localization_engine.get_primary_vernacular_for_district("Pithoragarh") == "kum"


class TestInfrastructureExposureAnalytics:
    def test_calculate_exposure_chamoli(self):
        """Verifies spatial intersection calculations for flooded roads, substations, and hospitals in Chamoli."""
        res = exposure_analytics_service.calculate_exposure(
            latitude=30.5564,
            longitude=79.5670,
            radius_km=15.0,
            flood_depth_m=1.5,
            district="Chamoli",
        )
        assert res.flooded_roads_km > 0
        assert res.submerged_power_substations_count >= 1
        assert res.vulnerable_hospitals_count >= 1
        assert res.estimated_exposed_population > 0
        assert res.evacuation_priority_index >= 5.0
        assert len(res.critical_assets_list) > 0


class TestCitizenGroundTruthTelemetry:
    @pytest.mark.asyncio
    async def test_citizen_report_submission_and_priority_bump(self):
        """Verifies that an acute field report escalates priority in the operator validation queue."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            payload = {
                "latitude": 30.5564,
                "longitude": 79.5670,
                "district": "Chamoli",
                "hazard_type": "Flash flood debris surge",
                "field_notes": "Rishiganga tributary surge observed near Tapovan tunnel.",
                "reporter_phone": "+919864011223",
                "has_photo_evidence": True,
            }
            res = await client.post("/api/v1/telemetry/citizen-report", json=payload)
            assert res.status_code == 200
            data = res.json()
            assert data["status"] == "ACCEPTED"
            assert data["priority_escalated"] is True

            # Verify report shows in reports list
            list_res = await client.get("/api/v1/telemetry/citizen-reports")
            assert list_res.status_code == 200
            reports = list_res.json()
            assert any(r["hazard_type"] == "Flash flood debris surge" for r in reports)

