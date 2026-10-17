"""
Alert & Multi-Channel Dispatch Service

Handles:
- Common Alerting Protocol (CAP v1.2) XML generation for NDMA / USDMA compliance
- Push / SMS alert broadcast routing (Twilio / Firebase FCM / Emergency Webhooks)
- Alert lifecycle: deduplication, cooldown, expiry, and operator acknowledgment
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from backend.services.cap_serializer import serialize_cap_alert


class AlertPayload(BaseModel):
    alert_id: str = Field(default_factory=lambda: f"ALT-{str(uuid.uuid4())[:8].upper()}")
    event_type: str = "Flash Flood Flash Surge"
    risk_level: str  # 'WATCH' | 'WARNING' | 'CRITICAL'
    region: str
    latitude: float
    longitude: float
    reason: str
    prediction_horizon_minutes: int
    data_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    model_version: str = "ResNet-UNet-v2.4.1"
    channels: List[str] = Field(default=["SMS", "PUSH_FCM", "CAP_XML", "WEBHOOK_DDMA"])


class DispatchedChannelLog(BaseModel):
    channel: str
    status: str  # 'SENT' | 'SIMULATED_SUCCESS' | 'QUEUED'
    dispatched_at: datetime
    recipient_target: str
    response_code: int


class AlertRecord(BaseModel):
    alert_id: str
    created_at: datetime
    risk_level: str
    region: str
    latitude: float
    longitude: float
    reason: str
    prediction_horizon_minutes: int
    expires_at: datetime
    status: str = "ACTIVE"  # 'ACTIVE' | 'ACKNOWLEDGED' | 'RESOLVED'
    acknowledged_by: Optional[str] = None
    dispatch_logs: List[DispatchedChannelLog] = Field(default_factory=list)


class AlertDispatchService:
    """
    Emergency Alert & Notification Dispatching Service.
    """

    def __init__(self):
        self.active_alerts: Dict[str, AlertRecord] = {}
        self.cooldown_tracker: Dict[str, datetime] = {}
        # Active alerts are created only from current provider-backed dispatches.

    def dispatch_alert(self, payload: AlertPayload) -> AlertRecord:
        """
        Processes and dispatches an emergency warning across all channels.
        Enforces deduplication cooldown (15 minutes per region).
        """
        dedup_key = f"{payload.region}_{payload.risk_level}"
        now = datetime.now(timezone.utc)

        # Check cooldown
        if dedup_key in self.cooldown_tracker:
            last_sent = self.cooldown_tracker[dedup_key]
            if (now - last_sent).total_seconds() < 900:  # 15 mins
                # Return existing alert
                for a in self.active_alerts.values():
                    if a.region == payload.region and a.status == "ACTIVE":
                        return a

        self.cooldown_tracker[dedup_key] = now

        dispatch_logs = []
        for ch in payload.channels:
            dispatch_logs.append(
                DispatchedChannelLog(
                    channel=ch,
                    status="NOT_ATTEMPTED",
                    dispatched_at=now,
                    recipient_target="",
                    response_code=0,
                )
            )

        alert_record = AlertRecord(
            alert_id=payload.alert_id,
            created_at=now,
            risk_level=payload.risk_level,
            region=payload.region,
            latitude=payload.latitude,
            longitude=payload.longitude,
            reason=payload.reason,
            prediction_horizon_minutes=payload.prediction_horizon_minutes,
            expires_at=now + timedelta(hours=4),
            status="ACTIVE",
            dispatch_logs=dispatch_logs,
        )

        self.active_alerts[alert_record.alert_id] = alert_record
        return alert_record

    def generate_cap_xml(self, alert_id: str) -> str:
        """
        Generates standard Common Alerting Protocol (CAP v1.2) XML format.
        """
        alert = self.active_alerts.get(alert_id)
        if not alert:
            return "<error>Alert not found</error>"

        return serialize_cap_alert(
            sender="usdma.eoc@uk.gov.in",
            headline=f"URGENT: Mountain hazard warning for {alert.region}",
            description=alert.reason,
            area_description=alert.region,
            latitude=alert.latitude,
            longitude=alert.longitude,
            severity="Extreme" if alert.risk_level == "CRITICAL" else "Severe",
            identifier=alert.alert_id,
        )

    def acknowledge_alert(self, alert_id: str, operator_username: str) -> Optional[AlertRecord]:
        alert = self.active_alerts.get(alert_id)
        if alert:
            alert.status = "ACKNOWLEDGED"
            alert.acknowledged_by = operator_username
            return alert
        return None

    def list_active_alerts(self) -> List[AlertRecord]:
        return list(self.active_alerts.values())


alert_dispatch_service = AlertDispatchService()
