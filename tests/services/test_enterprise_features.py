"""
Tests for Enterprise Features:
1. Dynamic GIS Evacuation Routing (A* / Dijkstra with Water Depth Constraint)
2. Cloud-Piercing Radar & Satellite Blind-Spot Fallback
3. Immutable Cryptographic Audit Logger (SHA-256 Hash Chain)
"""

import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app
from backend.services.evacuation_routing import dynamic_evacuation_router
from backend.services.satellite_fallback import satellite_fallback_controller
from backend.services.audit_logger import audit_logger


class TestDynamicEvacuationRouting:
    def test_evacuation_path_calculated_nominal(self):
        """Verifies shortest path to high-ground shelter when flood depth is nominal."""
        res = dynamic_evacuation_router.calculate_safest_evacuation_path(
            origin_node_id="UK_HUB_01",
            water_depth_m=0.2,
            district="Chamoli",
        )
        assert res.is_passable is True
        assert res.total_distance_km > 0
        assert res.destination_shelter != ""
        assert res.geojson_linestring["type"] == "Feature"
        assert res.geojson_linestring["geometry"]["type"] == "LineString"
        assert len(res.turn_by_turn_waypoints) >= 2

    def test_flooded_road_barrier_enforcement(self):
        """Verifies that road segments where water depth >= 0.3m are avoided."""
        # Deep water will flood lower segments and force alternative path
        res_deep = dynamic_evacuation_router.calculate_safest_evacuation_path(
            origin_node_id="UK_HUB_01",
            water_depth_m=1.8,
            district="Chamoli",
        )
        assert res_deep.flooded_segments_avoided > 0
        assert res_deep.is_passable is True


class TestSatelliteRadarFallback:
    def test_optical_blind_spot_triggers_sar_radar(self):
        """When cloud cover > 92%, optical is degraded and Sentinel-1 SAR is activated."""
        res = satellite_fallback_controller.evaluate_satellite_pipeline(
            cloud_cover_pct=96.0,
            is_satellite_blackout=False,
        )
        assert res.is_optical_blind_spot is True
        assert res.fallback_level_tier == "TIER_2_SAR_RADAR"
        assert "Sentinel-1 C-Band SAR" in res.active_inundation_sensor

    def test_total_satellite_blackout_triggers_1d_ground_hydro(self):
        """When all satellites drop, falls back to 1D hydrodynamic model."""
        res = satellite_fallback_controller.evaluate_satellite_pipeline(
            cloud_cover_pct=99.0,
            is_satellite_blackout=True,
        )
        assert res.fallback_level_tier == "TIER_3_HYDRODYNAMIC_GROUND"
        assert "1D Catchment Hydrodynamic Mesh" in res.active_inundation_sensor


class TestSecureAuditLogger:
    def test_hash_chain_integrity(self):
        """Verifies that the append-only SHA-256 hash chain remains unbroken."""
        is_valid, count = audit_logger.verify_integrity()
        assert is_valid is True
        assert count >= 4

    def test_tamper_detection(self):
        """Verifies that tampering with a historical log invalidates the hash chain."""
        # Log a test action
        rec = audit_logger.log_action(
            user_id="TEST_AUDITOR",
            role="ADMIN",
            action="TEST_LOG_ENTRY",
            details="Verifying cryptographic integrity.",
        )
        is_valid_before, _ = audit_logger.verify_integrity()
        assert is_valid_before is True

        # Simulate adversarial tamper on the record details
        original_details = rec.details
        rec.details = "TAMPERED DETAILS: Unauthorized modification"
        is_valid_after, bad_index = audit_logger.verify_integrity()
        assert is_valid_after is False

        # Restore original details
        rec.details = original_details
        is_valid_restored, _ = audit_logger.verify_integrity()
        assert is_valid_restored is True


class TestEnterpriseAPIRoutes:
    @pytest.mark.asyncio
    async def test_evacuation_routing_api(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.get("/api/v1/data/routing/evacuation?district=Chamoli&water_depth_m=1.2")
            assert res.status_code == 200
            data = res.json()
            assert "geojson_linestring" in data
            assert data["is_passable"] is True

    @pytest.mark.asyncio
    async def test_satellite_status_api(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.get("/api/v1/system/satellite-status?cloud_cover_pct=95.0")
            assert res.status_code == 200
            data = res.json()
            assert data["is_optical_blind_spot"] is True
            assert data["fallback_level_tier"] == "TIER_2_SAR_RADAR"

    @pytest.mark.asyncio
    async def test_audit_trail_api(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.get("/api/v1/system/audit-trail?limit=10")
            assert res.status_code == 200
            data = res.json()
            assert data["audit_integrity_status"] == "VERIFIED_TAMPER_PROOF"
            assert data["hash_chain_verified"] is True
            assert len(data["audit_logs"]) > 0
