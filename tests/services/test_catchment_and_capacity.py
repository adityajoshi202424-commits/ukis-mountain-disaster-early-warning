"""
Unit & Integration Tests for:
1. Hydraulic Catchment Cascade & Wavefront Attenuation Modeler
2. High-Resolution Edge-Sensor Health Analytics (Battery & Ping Latency)
3. Capacity-Constrained Evacuation Graph Pathfinder
"""

import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.catchment_cascade import catchment_cascade_modeler
from backend.services.evacuation_routing import dynamic_evacuation_router
from backend.sih.replay_engine import sih_replay_engine
from backend.sih.models import TelemetryFeatureRow

client = TestClient(app)


class TestCatchmentCascadeModeler:
    def test_exponential_time_lag_attenuation(self):
        result = catchment_cascade_modeler.compute_downstream_impact(
            district="Chamoli",
            local_rate_of_rise=1.45,
            elapsed_storm_hours=1.5,
        )
        assert result.target_district == "Chamoli"
        assert result.cumulative_downstream_impact_index > 0.0
        assert len(result.upstream_catchment_nodes) == 3
        # Check node attenuation math
        for node in result.upstream_catchment_nodes:
            assert node.time_lag_hours > 0.0
            assert node.weight_coefficient > 0.0
            assert node.rate_of_rise_m_hr > 0.0

    def test_downstream_surge_imminent_flag(self):
        high_surge = catchment_cascade_modeler.compute_downstream_impact(
            district="Chamoli",
            local_rate_of_rise=2.10,
            elapsed_storm_hours=2.0,
        )
        assert high_surge.is_downstream_surge_imminent is True
        assert high_surge.projected_downstream_surge_arrival_minutes == 75

        low_surge = catchment_cascade_modeler.compute_downstream_impact(
            district="Chamoli",
            local_rate_of_rise=0.15,
            elapsed_storm_hours=0.5,
        )
        assert low_surge.cumulative_downstream_impact_index < 0.8


class TestEdgeSensorHealthAnalytics:
    def test_battery_under_11_2v_triggers_degraded(self):
        t_curr = datetime(2024, 7, 14, 10, 0, tzinfo=timezone.utc)
        record1 = TelemetryFeatureRow(
            event_id="test",
            timestamp=datetime(2024, 7, 14, 9, 45, tzinfo=timezone.utc),
            rainfall_mm=10.0,
            rainfall_intensity_mm_hr=12.0,
            river_level_meters=26.5,
            river_surge_m_hr=0.2,
            soil_moisture_percentage=75.0,
            soil_saturation_index=0.75,
            battery_voltage_v=12.4,
            network_latency_ms=120,
        )
        record2 = TelemetryFeatureRow(
            event_id="test",
            timestamp=t_curr,
            rainfall_mm=14.0,
            rainfall_intensity_mm_hr=16.0,
            river_level_meters=26.8,
            river_surge_m_hr=0.3,
            soil_moisture_percentage=78.0,
            soil_saturation_index=0.78,
            battery_voltage_v=10.8,  # Under 11.2V
            network_latency_ms=120,
        )

        window_data = sih_replay_engine.extract_gated_window_features(
            all_records=[record1, record2],
            T_curr=t_curr,
        )
        assert window_data["data_quality"] == "DEGRADED"
        assert any("battery critical" in msg for msg in window_data["missing_inputs"])

    def test_latency_over_4500ms_triggers_degraded(self):
        t_curr = datetime(2024, 7, 14, 10, 0, tzinfo=timezone.utc)
        record1 = TelemetryFeatureRow(
            event_id="test",
            timestamp=datetime(2024, 7, 14, 9, 45, tzinfo=timezone.utc),
            rainfall_mm=10.0,
            rainfall_intensity_mm_hr=12.0,
            river_level_meters=26.5,
            river_surge_m_hr=0.2,
            soil_moisture_percentage=75.0,
            soil_saturation_index=0.75,
            battery_voltage_v=12.4,
            network_latency_ms=120,
        )
        record2 = TelemetryFeatureRow(
            event_id="test",
            timestamp=t_curr,
            rainfall_mm=14.0,
            rainfall_intensity_mm_hr=16.0,
            river_level_meters=26.8,
            river_surge_m_hr=0.3,
            soil_moisture_percentage=78.0,
            soil_saturation_index=0.78,
            battery_voltage_v=12.4,
            network_latency_ms=4950,  # Over 4500ms
        )

        window_data = sih_replay_engine.extract_gated_window_features(
            all_records=[record1, record2],
            T_curr=t_curr,
        )
        assert window_data["data_quality"] == "DEGRADED"
        assert any("latency exceeded" in msg for msg in window_data["missing_inputs"])


class TestShelterCapacityConstrainedRouting:
    def test_shelter_capacity_routing_nominal(self):
        # Under max capacity
        route = dynamic_evacuation_router.calculate_safest_evacuation_path(
            origin_node_id="UK_HUB_01",
            water_depth_m=0.2,
            district="Chamoli",
            shelter_headcount_overrides={"UK_SHELTER_01": 482, "UK_SHELTER_02": 140},
        )
        assert route.is_passable is True
        assert route.destination_shelter == "Joshimath Cantonment High-Ground Shelter"
        assert route.shelter_capacity_status.is_exhausted is False
        assert route.shelter_capacity_status.utilization_pct == 96.4

    def test_shelter_exhaustion_forces_overflow_reroute(self):
        # Joshimath Cantonment at 500/500 (100% capacity) -> Inbound edge blocked (weight = Infinity)
        route = dynamic_evacuation_router.calculate_safest_evacuation_path(
            origin_node_id="UK_HUB_01",
            water_depth_m=0.2,
            district="Chamoli",
            shelter_headcount_overrides={"UK_SHELTER_01": 500, "UK_SHELTER_02": 140},
        )
        assert route.is_passable is True
        # Dijkstra must route to secondary shelter: Govt Inter College Joshimath Elevated Campus
        assert "Govt Inter College Joshimath Elevated Campus" in route.destination_shelter
        assert route.overflow_redirected is True
        assert route.shelter_capacity_status.shelter_id == "UK_SHELTER_02"


class TestCatchmentAndCapacityAPIRoutes:
    def test_catchment_cascade_api(self):
        response = client.get("/api/v1/data/hydrology/cascade?district=Chamoli&local_rate_of_rise=1.45")
        assert response.status_code == 200
        data = response.json()
        assert data["target_district"] == "Chamoli"
        assert data["cumulative_downstream_impact_index"] > 0
        assert len(data["upstream_catchment_nodes"]) >= 2

    def test_stations_health_api(self):
        response = client.get("/api/v1/data/stations/health")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 4
        # Verify battery and latency presence
        for st in data:
            assert "battery_voltage_v" in st
            assert "network_latency_ms" in st
            assert "data_quality" in st

    def test_shelter_capacity_update_api(self):
        response = client.post(
            "/api/v1/data/routing/shelter-capacity",
            json={"shelter_id": "UK_SHELTER_01", "current_headcount": 490},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["new_headcount"] == 490
