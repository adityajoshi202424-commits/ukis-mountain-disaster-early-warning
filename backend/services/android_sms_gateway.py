"""
Android SMS Gateway Service
UKIS P-011 Mountain Disaster Intelligence — Mobile Cellular Relay Pipeline

Enables dedicated field Android devices / smartphones to act as on-the-ground SMS gateways
via their physical cellular SIM cards (BSNL, Airtel, Jio).
- Handles emergency alert queuing when cloud telecom gateways (Fast2SMS/Twilio) are offline or unconfigured
- Supports device heartbeats, battery & signal telemetry
- Collects native Android SmsManager delivery acknowledgments with zero synthetic data
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class QueuedEmergencySMS(BaseModel):
    sms_id: str = Field(default_factory=lambda: f"AND-SMS-{uuid.uuid4().hex[:8].upper()}")
    recipient_phone: str
    message: str
    target_community: str
    hazard_tier: str = "HIGH"
    safe_shelter: Optional[str] = None
    route_direction: Optional[str] = None
    status: str = "QUEUED"  # 'QUEUED' | 'IN_TRANSIT' | 'DELIVERED' | 'FAILED'
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    dispatched_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    device_id: Optional[str] = None
    carrier: Optional[str] = None
    cellular_message_ref: Optional[str] = None
    error_detail: Optional[str] = None


class AndroidDeviceRegistration(BaseModel):
    device_id: str
    device_model: str = "Android Gateway Unit"
    android_version: str = "Android 14 (API 34)"
    sim_carrier: str = "BSNL Mobile"
    sim_slot_count: int = 1
    battery_pct: int = 100
    signal_strength_bars: int = 4
    app_version: str = "1.0.0"
    registered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_heartbeat: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    total_sms_dispatched: int = 0
    is_active: bool = True


class AndroidDeliveryReceipt(BaseModel):
    sms_id: str
    device_id: str
    status: str  # 'DELIVERED' | 'FAILED' | 'SENT_RADIO_ACK'
    carrier_message_ref: Optional[str] = None
    error_message: Optional[str] = None
    delivered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AndroidSMSGatewayService:
    """
    In-memory and persistent manager for Android mobile SMS dispatch agents.
    """

    def __init__(self):
        self._devices: Dict[str, AndroidDeviceRegistration] = {}
        self._sms_queue: Dict[str, QueuedEmergencySMS] = {}

    def register_device(self, reg: AndroidDeviceRegistration) -> AndroidDeviceRegistration:
        """Register or update an active Android SMS relay device."""
        now = datetime.now(timezone.utc)
        if reg.device_id in self._devices:
            dev = self._devices[reg.device_id]
            dev.battery_pct = reg.battery_pct
            dev.signal_strength_bars = reg.signal_strength_bars
            dev.sim_carrier = reg.sim_carrier
            dev.last_heartbeat = now
            dev.is_active = True
            return dev

        reg.registered_at = now
        reg.last_heartbeat = now
        reg.is_active = True
        self._devices[reg.device_id] = reg
        return reg

    def enqueue_sms(
        self,
        recipient_phone: str,
        message: str,
        target_community: str,
        hazard_tier: str = "HIGH",
        safe_shelter: Optional[str] = None,
        route_direction: Optional[str] = None,
    ) -> QueuedEmergencySMS:
        """Enqueue an emergency SMS for dispatch via an active Android SIM device."""
        sms = QueuedEmergencySMS(
            recipient_phone=recipient_phone,
            message=message,
            target_community=target_community,
            hazard_tier=hazard_tier,
            safe_shelter=safe_shelter,
            route_direction=route_direction,
            status="QUEUED",
        )
        self._sms_queue[sms.sms_id] = sms
        return sms

    def fetch_pending_sms(self, device_id: str, limit: int = 10) -> List[QueuedEmergencySMS]:
        """
        Android device polls this to retrieve pending messages to transmit via native SIM.
        Marks returned items as IN_TRANSIT with the assigned device ID.
        """
        now = datetime.now(timezone.utc)
        if device_id in self._devices:
            self._devices[device_id].last_heartbeat = now
            self._devices[device_id].is_active = True

        pending: List[QueuedEmergencySMS] = []
        for item in self._sms_queue.values():
            if item.status == "QUEUED":
                item.status = "IN_TRANSIT"
                item.dispatched_at = now
                item.device_id = device_id
                pending.append(item)
                if len(pending) >= limit:
                    break
        return pending

    def acknowledge_delivery(self, receipt: AndroidDeliveryReceipt) -> Optional[QueuedEmergencySMS]:
        """Process cellular delivery status callback reported by Android SmsManager."""
        sms = self._sms_queue.get(receipt.sms_id)
        if not sms:
            return None

        sms.status = receipt.status
        sms.cellular_message_ref = receipt.carrier_message_ref
        sms.error_detail = receipt.error_message
        sms.delivered_at = receipt.delivered_at

        if receipt.device_id in self._devices and receipt.status in ("DELIVERED", "SENT_RADIO_ACK"):
            self._devices[receipt.device_id].total_sms_dispatched += 1
            self._devices[receipt.device_id].last_heartbeat = datetime.now(timezone.utc)

        return sms

    def list_active_devices(self, stale_timeout_minutes: int = 15) -> List[AndroidDeviceRegistration]:
        """Returns registered devices that reported a heartbeat within the threshold."""
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=stale_timeout_minutes)
        for dev in self._devices.values():
            dev.is_active = dev.last_heartbeat >= cutoff
        return list(self._devices.values())

    def get_queue_status(self) -> Dict[str, Any]:
        """Returns statistics on the current SMS queue."""
        total = len(self._sms_queue)
        queued = sum(1 for s in self._sms_queue.values() if s.status == "QUEUED")
        in_transit = sum(1 for s in self._sms_queue.values() if s.status == "IN_TRANSIT")
        delivered = sum(1 for s in self._sms_queue.values() if s.status in ("DELIVERED", "SENT_RADIO_ACK"))
        failed = sum(1 for s in self._sms_queue.values() if s.status == "FAILED")
        active_devices = sum(1 for d in self.list_active_devices() if d.is_active)

        return {
            "total_messages": total,
            "queued": queued,
            "in_transit": in_transit,
            "delivered": delivered,
            "failed": failed,
            "active_devices_count": active_devices,
        }

    def list_all_messages(self, limit: int = 50) -> List[QueuedEmergencySMS]:
        """Returns recent messages in the queue ordered newest to oldest."""
        return sorted(self._sms_queue.values(), key=lambda s: s.created_at, reverse=True)[:limit]


android_sms_gateway_service = AndroidSMSGatewayService()
