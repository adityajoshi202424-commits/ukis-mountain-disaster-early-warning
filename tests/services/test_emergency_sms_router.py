"""
Tests for Emergency Notification Router & SMS Dispatch Pipeline
Validates Evaluation Mode Simulation Failsafe, Anti-Accident Guardrails, and Timeout Handling
"""

import pytest
from datetime import datetime, timezone
from backend.services.emergency_notification_router import (
    emergency_notification_router,
    EmergencySMSPayload,
    TelemetryTriggers,
)


class TestEmergencyNotificationRouter:
    @pytest.mark.asyncio
    async def test_failsafe_intercept_in_historical_replay_mode(self):
        """Validates that HISTORICAL_REPLAY mode intercepts network calls and produces UI logs."""
        payload = EmergencySMSPayload(
            event_id="SIH-2026-FL-001",
            mode="HISTORICAL_REPLAY",
            target_community="Chamoli_District_Zone_B",
            telemetry_triggers=TelemetryTriggers(
                river_surge_m_hr=1.45,
                rain_velocity_mm_hr=35.2,
                soil_saturation_pct=88.0,
            ),
            alert_message="CRITICAL EMERGENCY: Flash Flood warning issued for Chamoli Zone B. Rapid river surge detected (+1.4m/hr).",
        )

        res = await emergency_notification_router.dispatch_critical_alert(payload)
        assert res.status == "SIMULATED_INTERCEPTED"
        assert "[SIMULATED SMS ROUTED TO Chamoli_District_Zone_B]" in res.status_message
        assert res.execution_time_ms < 100.0  # Fast, in-memory execution

        # Verify terminal log entries
        logs_str = " ".join(res.system_terminal_logs)
        assert "ALERT_ENGINE: Risk Tier High. SMS Payload generated" in logs_str
        assert "COMM_ROUTER: Replay Mode active" in logs_str
        assert "Twilio API intercepted" in logs_str

    @pytest.mark.asyncio
    async def test_failsafe_intercept_in_simulation_scenario_mode(self):
        """Validates that SIMULATION mode also safely intercepts external calls."""
        payload = EmergencySMSPayload(
            event_id="SIH-2026-SCENARIO-02",
            mode="SIMULATION",
            target_community="Joshimath_Alaknanda_Zone_C",
            telemetry_triggers=TelemetryTriggers(
                river_surge_m_hr=1.80,
                rain_velocity_mm_hr=42.0,
            ),
            alert_message="SCENARIO SIMULATION: Evacuation advisory test.",
        )

        res = await emergency_notification_router.dispatch_critical_alert(payload)
        assert res.status == "SIMULATED_INTERCEPTED"
        assert "Joshimath_Alaknanda_Zone_C" in res.status_message

    @pytest.mark.asyncio
    async def test_live_mode_handles_missing_credentials_gracefully(self):
        """Validates that LIVE_PRODUCTION without Twilio credentials falls back safely without crashing."""
        payload = EmergencySMSPayload(
            event_id="SIH-2026-LIVE-003",
            mode="LIVE_PRODUCTION",
            target_community="Rudraprayag_Mandakini_Zone_A",
            telemetry_triggers=TelemetryTriggers(
                river_surge_m_hr=1.35,
                rain_velocity_mm_hr=31.0,
            ),
            alert_message="LIVE TEST: Emergency advisory.",
        )

        # Assuming no credentials in default test env
        res = await emergency_notification_router.dispatch_critical_alert(payload)
        assert res.status in ["TELECOM_CARRIER_TRANSMITTED", "LIVE_QUEUED_NO_KEYS", "LIVE_DISPATCHED", "FAILED_ERROR", "FAILED_TIMEOUT", "SOURCE_UNAVAILABLE"]
        assert res.execution_time_ms < 2500.0  # Respects strict execution limit
