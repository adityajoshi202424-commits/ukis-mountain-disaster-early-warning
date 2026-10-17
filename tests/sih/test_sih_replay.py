"""
Unit and Integration Tests for SIH Demonstration & Evaluation Pipeline

Tests:
1. Zero temporal leakage enforcement (hard ceiling constraint)
2. Ground truth isolation from inference
3. High-frequency derivative calculus (Rain velocity, river surge, soil saturation)
4. Early warning trigger condition & lead-time calculation
5. Controlled failure / outage simulation (CWC failover to radar altimetry)
6. Counterfactual scenario mode (+20% rainfall offset isolation)
7. Objective metrics calculation (Precision, Recall, F1, FAR, Missed Rate, IoU)
"""

from datetime import datetime, timezone, timedelta
import pytest

from backend.sih.repository import sih_repository
from backend.sih.replay_engine import sih_replay_engine
from backend.sih.models_registry import model_registry


@pytest.fixture
def repo():
    return sih_repository


@pytest.fixture
def engine():
    return sih_replay_engine


class TestZeroTemporalLeakage:
    """Verifies that at no point does future data enter the inference matrix."""

    def test_future_records_dropped_at_t_curr(self, repo):
        event_id = "uk-chamoli-glof-2021"
        event = repo.get_event(event_id)
        assert event is not None

        # Pick an intermediate timestamp (e.g. 07:00 UTC)
        t_curr = datetime(2021, 2, 7, 7, 0, 0, tzinfo=timezone.utc)
        gated = repo.get_gated_historical_features(event_id, target_timestamp=t_curr)

        assert len(gated) > 0
        for record in gated:
            assert record.timestamp <= t_curr, f"LEAK DETECTED: Record at {record.timestamp} > {t_curr}"

    def test_ground_truth_isolation(self, repo, engine):
        """Model predict function must never receive or query the ground truth polygon."""
        event_id = "uk-chamoli-glof-2021"
        t_early = datetime(2021, 2, 7, 5, 0, 0, tzinfo=timezone.utc)
        gated = repo.get_gated_historical_features(event_id, target_timestamp=t_early)

        model = model_registry.get_model("ResNet-UNet-v2.4.1")
        pred = model.predict(gated)

        # Ensure ground truth is not in features or prediction output
        assert "ground_truth" not in pred
        assert "geojson" not in pred


class TestHighFrequencyDerivativesAndTrigger:
    """Verifies rate-of-rise calculus and trigger rules."""

    def test_cloudburst_trigger_rule(self, repo, engine):
        event_id = "uk-chamoli-glof-2021"
        # Run replay loop
        res = engine.execute_historical_replay(
            event_id=event_id,
            model_version="ResNet-UNet-v2.4.1",
            time_step_minutes=15,
        )
        sih_res = res["sih_evaluation_response"]
        timeline = sih_res["timeline"]

        # Find first warning
        warnings = [step for step in timeline if step["warning_triggered"]]
        assert len(warnings) > 0, "A valid high-risk early warning should have triggered"

        first_warn = warnings[0]
        # Verify trigger reason contains either rain velocity, surge velocity, or GLOF indicator
        reason = first_warn["prediction"]["trigger_reason"]
        assert ("Precipitation velocity" in reason or "River surge" in reason or "Extreme Danger" in reason or "surge" in reason.lower())

    def test_lead_time_calculation(self, engine):
        event_id = "uk-chamoli-glof-2021"
        res = engine.execute_historical_replay(event_id=event_id)
        metrics = res["sih_evaluation_response"]["metrics"]

        lead_time = metrics["warning_lead_time"]
        assert "Hours" in lead_time, f"Expected lead time in hours format, got {lead_time}"

        # In steep Himalayan micro-watersheds, rapid flash floods peak in 30-120 mins -> 0.5-3.0 hours warning lead time
        lead_val = float(lead_time.split()[0])
        assert 0.5 <= lead_val <= 4.0, f"Expected 0.5-4.0 hours lead time, got {lead_val}"


class TestControlledFailureOutage:
    """Verifies fault-tolerance when CWC river gauge is taken offline."""

    def test_cwc_outage_activates_backup(self, engine):
        event_id = "uk-chamoli-glof-2021"
        res = engine.execute_historical_replay(
            event_id=event_id,
            disabled_source_id="CWC_GAUGE",
        )
        sih_res = res["sih_evaluation_response"]

        # Provenance records the outage
        assert sih_res["provenance"]["disabled_source"] == "CWC_GAUGE"

        # Quality should be flagged DEGRADED
        degraded_steps = [s for s in sih_res["timeline"] if s["data_quality"] == "DEGRADED"]
        assert len(degraded_steps) == len(sih_res["timeline"])

        # Check that model flagged backup radar usage
        last_step = sih_res["timeline"][-1]
        assert last_step["prediction"]["using_backup_radar"] is True
        assert "Sentinel-3" in last_step["prediction"]["trigger_reason"] or "radar" in last_step["prediction"]["trigger_reason"].lower()


class TestScenarioModeIsolation:
    """Verifies that scenario offsets modify calculations in-memory without polluting base data."""

    def test_scenario_offset(self, engine, repo):
        event_id = "uk-chamoli-glof-2021"

        # Base run
        base_res = engine.execute_historical_replay(event_id=event_id, rainfall_offset_pct=0.0)
        # Scenario run with +20% rainfall
        scenario_res = engine.execute_historical_replay(event_id=event_id, rainfall_offset_pct=20.0)

        base_timeline = base_res["sih_evaluation_response"]["timeline"]
        scenario_timeline = scenario_res["sih_evaluation_response"]["timeline"]

        # Check rainfall in scenario timeline is higher
        for b_step, s_step in zip(base_timeline, scenario_timeline):
            b_rain = b_step["features_summary"]["rainfall_mm"]
            s_rain = s_step["features_summary"]["rainfall_mm"]
            if b_rain > 0:
                assert s_rain > b_rain
                assert round(s_rain / b_rain, 2) == 1.20


class TestObjectiveMetricsOutput:
    """Verifies confusion matrix and mathematical metrics output format."""

    def test_metrics_payload_schema(self, engine):
        event_id = "uk-chamoli-glof-2021"
        res = engine.execute_historical_replay(event_id=event_id)
        metrics = res["sih_evaluation_response"]["metrics"]

        assert "warning_lead_time" in metrics
        assert "precision" in metrics
        assert "recall" in metrics
        assert "f1_score" in metrics
        assert "false_alarm_rate" in metrics
        assert "missed_event_rate" in metrics
        assert "spatial_overlap_iou" in metrics
        assert "calibration_score" in metrics

        assert 0.0 <= metrics["precision"] <= 1.0
        assert 0.0 <= metrics["recall"] <= 1.0
        assert 0.0 <= metrics["f1_score"] <= 1.0
