"""
Test suite for UKIS Addendum v2: Precursor Detection Layer + System Limitations
Covers:
- Section 3.15: Sentinel-1 InSAR coherence precursor tracking on pilot slopes
- Section 3.16: Automated Glacial Lake (GLOF) 30-day rate-of-change and cloud fail-visibly
- Section 3.17: System limitations report schema, coverage matrix, and 24-feature tiering
- API endpoints integration in system.py and action_layer.py
"""

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.sar_coherence import sar_coherence_engine, SAR_PILOT_SLOPES
from backend.services.glof_sentinel import glof_sentinel_service
from backend.services.catchment_cascade import catchment_cascade_modeler
from backend.services.system_limitations import system_limitations_service

client = TestClient(app)


def test_sar_coherence_pilot_slope_detection():
    """Verify that coordinates within Helang-Joshimath slope detect slow creep."""
    eval_result = sar_coherence_engine.evaluate_slope_coherence(
        latitude=30.5420,
        longitude=79.5480,
    )
    assert eval_result.within_pilot_scope is True
    assert eval_result.coverage_status == "PILOT_COVERED"
    assert eval_result.slope_id == "SLOPE-JOSHIMATH-HELANG"
    assert eval_result.destabilization_state in ["SLOW_CREEP_DETECTED", "ACCELERATING_DEFORMATION"]
    assert eval_result.estimated_deformation_rate_mm_week > 0.0
    assert len(eval_result.recent_interferometric_pairs) == 3
    assert eval_result.coherence_loss_delta >= 0.28
    assert "PRECURSOR DETECTED" in eval_result.actionable_insight or "SLOW-CREEP" in eval_result.actionable_insight


def test_sar_coherence_out_of_bounds_fail_visibly():
    """Verify that coordinates outside pilot slopes fail visibly without fabricating numbers."""
    eval_result = sar_coherence_engine.evaluate_slope_coherence(
        latitude=29.1000,
        longitude=78.2000,
    )
    assert eval_result.within_pilot_scope is False
    assert eval_result.coverage_status == "OUTSIDE_PILOT_SCOPE"
    assert eval_result.destabilization_state == "NOT_MONITORED_IN_PROTOTYPE"
    assert eval_result.latest_coherence == 0.0
    assert eval_result.estimated_deformation_rate_mm_week == 0.0
    assert len(eval_result.recent_interferometric_pairs) == 0
    assert "OUTSIDE the Tier 3 SAR Coherence pilot prototype boundary" in eval_result.actionable_insight
    assert "Item 24" in eval_result.limitations_notice


def test_sar_coherence_pilot_sites_catalog():
    """Verify pilot slope catalog contains all 3 named slopes with required metadata."""
    pilot_sites = sar_coherence_engine.list_pilot_slopes()
    assert len(pilot_sites) == 3
    slope_ids = [s["slope_id"] for s in pilot_sites]
    assert "SLOPE-JOSHIMATH-HELANG" in slope_ids
    assert "SLOPE-KEDARNATH-MANDAKINI" in slope_ids
    assert "SLOPE-RAINI-RISHIGANGA" in slope_ids
    for s in pilot_sites:
        assert "sentinel1_track" in s
        assert "geology" in s
        assert "historical_relevance" in s


def test_glof_expansion_rate_30day():
    """Verify 30-day surface area rate of change and cascade multiplier calculation."""
    res = glof_sentinel_service.calculate_30day_expansion_rate(
        current_area_m2=142100.0,
        area_30d_ago_m2=124500.0,
        lake_name="Chorabari Lake (Gandhi Sarovar)",
        cloud_cover_pct=8.5,
        threshold_rate_pct=10.0,
    )
    assert res.observation_status == "VERIFIED_OBSERVATION"
    assert res.is_precursor_flagged is True
    assert res.rate_of_change_30d_pct == 14.14
    assert res.precursor_severity in ["PRECURSOR_WATCH", "CRITICAL_SURGE_RISK"]
    assert res.upstream_cascade_multiplier > 1.0
    assert len(res.historical_observations) == 3
    assert "GLOF PRECURSOR" in res.actionable_recommendation or "PRECURSOR DETECTED" in res.actionable_recommendation


def test_glof_cloud_cover_obscuration_fail_visibly():
    """Verify that optical cloud cover > 30% raises an explicit observation gap."""
    res = glof_sentinel_service.calculate_30day_expansion_rate(
        current_area_m2=142100.0,
        area_30d_ago_m2=124500.0,
        lake_name="Chorabari Lake (Gandhi Sarovar)",
        cloud_cover_pct=42.5,
    )
    assert res.observation_status == "NO_CLOUD_FREE_OBSERVATION"
    assert res.is_precursor_flagged is False
    assert res.precursor_severity == "NO_OBSERVATION_GAP"
    assert res.upstream_cascade_multiplier == 1.0
    assert "OBSERVATION GAP DETECTED" in res.actionable_recommendation
    assert "42.5% cloud cover" in res.actionable_recommendation


def test_catchment_cascade_with_precursors():
    """Verify that lake expansion and SAR creep precursors elevate hydraulic cascade impact."""
    base_impact = catchment_cascade_modeler.compute_downstream_impact(
        district="Chamoli",
        local_rate_of_rise=1.45,
        elapsed_storm_hours=1.5,
        upstream_lake_expansion_multiplier=1.0,
        sar_coherence_creep_detected=False,
    )

    precursor_impact = catchment_cascade_modeler.compute_downstream_impact(
        district="Chamoli",
        local_rate_of_rise=1.45,
        elapsed_storm_hours=1.5,
        upstream_lake_expansion_multiplier=1.25,
        sar_coherence_creep_detected=True,
    )

    assert precursor_impact.cumulative_downstream_impact_index > base_impact.cumulative_downstream_impact_index
    assert precursor_impact.projected_downstream_surge_arrival_minutes == 60
    assert "Precursor Inputs" in precursor_impact.engineering_summary
    assert "InSAR Coherence Loss" in precursor_impact.engineering_summary
    assert "Glacial Lake Expansion" in precursor_impact.engineering_summary


def test_system_limitations_report_schema():
    """Verify comprehensive system limitations report contains 24 features and honest boundaries."""
    report = system_limitations_service.get_limitations_report()
    assert len(report.watershed_coverage_matrix) >= 5
    assert len(report.feature_maturity_tiers) == 24
    assert len(report.data_latency_matrix) >= 5
    assert len(report.what_this_system_does_not_claim) >= 5

    # Check Tier classification
    item17 = next(f for f in report.feature_maturity_tiers if f.item_number == 17)
    assert item17.tier == "TIER_3"
    assert item17.operational_maturity == "PROTOTYPE_SCOPE"

    item24 = next(f for f in report.feature_maturity_tiers if f.item_number == 24)
    assert item24.tier == "TIER_4"
    assert item24.operational_maturity == "ROADMAP_DESIGN_ONLY"

    assert "LEGAL & OPERATIONAL DISCLAIMER" in report.probabilistic_disclaimer
    assert "India Meteorological Department (IMD)" in report.probabilistic_disclaimer


def test_api_endpoints_integration():
    """Verify all new REST API endpoints respond with correct status codes and payloads."""
    # 1. System limitations endpoint
    resp_limitations = client.get("/api/v1/system/limitations")
    assert resp_limitations.status_code == 200
    data = resp_limitations.json()
    assert "watershed_coverage_matrix" in data
    assert len(data["feature_maturity_tiers"]) == 24

    # 2. SAR pilot sites endpoint
    resp_pilot = client.get("/api/v1/sar/coherence/pilot-sites")
    assert resp_pilot.status_code == 200
    sites = resp_pilot.json()
    assert len(sites) == 3

    # 3. SAR evaluation endpoint (inside pilot slope)
    resp_sar_eval = client.post(
        "/api/v1/sar/coherence/evaluate",
        json={"latitude": 30.5420, "longitude": 79.5480},
    )
    assert resp_sar_eval.status_code == 200
    sar_eval = resp_sar_eval.json()
    assert sar_eval["within_pilot_scope"] is True
    assert sar_eval["coverage_status"] == "PILOT_COVERED"

    # 4. SAR evaluation endpoint (outside pilot slope)
    resp_sar_out = client.post(
        "/api/v1/sar/coherence/evaluate",
        json={"latitude": 29.5000, "longitude": 78.5000},
    )
    assert resp_sar_out.status_code == 200
    sar_out = resp_sar_out.json()
    assert sar_out["within_pilot_scope"] is False
    assert sar_out["coverage_status"] == "OUTSIDE_PILOT_SCOPE"

    # 5. GLOF lake expansion rate endpoint
    resp_glof = client.post(
        "/api/v1/glof/lake-expansion/rate",
        json={
            "lake_name": "Chorabari Lake (Gandhi Sarovar)",
            "current_area_m2": 142100.0,
            "area_30d_ago_m2": 124500.0,
            "cloud_cover_pct": 8.5,
            "threshold_rate_pct": 10.0,
        },
    )
    assert resp_glof.status_code == 200
    glof_eval = resp_glof.json()
    assert glof_eval["observation_status"] == "VERIFIED_OBSERVATION"
    assert glof_eval["rate_of_change_30d_pct"] == 14.14
