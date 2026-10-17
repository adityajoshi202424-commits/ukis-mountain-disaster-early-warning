"""
Android SMS Gateway API Endpoints
UKIS P-011 Mountain Disaster Intelligence — Mobile Gateway Bridge

Endpoints:
- POST /api/v1/telecom/android-gateway/register: Register an active Android mobile device
- GET /api/v1/telecom/android-gateway/pending: Android app polls to retrieve queued SMS to send
- POST /api/v1/telecom/android-gateway/ack: Android app reports delivery receipts from SmsManager
- POST /api/v1/telecom/android-gateway/dispatch: Enqueue an emergency SMS for Android SIM dispatch
- GET /api/v1/telecom/android-gateway/devices: List all active registered Android dispatch units
- GET /api/v1/telecom/android-gateway/queue: Queue status metrics
"""

from __future__ import annotations

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field
from datetime import datetime, timezone

from backend.services.android_sms_gateway import (
    android_sms_gateway_service,
    AndroidDeviceRegistration,
    AndroidDeliveryReceipt,
    QueuedEmergencySMS,
)

router = APIRouter(prefix="/telecom/android-gateway", tags=["Android SMS Gateway"])


class DirectDispatchRequest(BaseModel):
    recipient_phone: str = Field(..., description="Target mobile number (e.g. +919876543210)")
    message: str = Field(..., min_length=5, max_length=500, description="Evacuation alert message body")
    target_community: str = Field(default="Uttarakhand_Himalayan_Zone")
    hazard_tier: str = Field(default="CRITICAL", description="'ORANGE' | 'RED' | 'CRITICAL'")
    safe_shelter: Optional[str] = None
    route_direction: Optional[str] = None


@router.post("/register", response_model=AndroidDeviceRegistration)
async def register_android_device(registration: AndroidDeviceRegistration):
    """
    Registers an on-the-ground Android device with hardware specs, SIM carrier, and battery.
    Keeps the device active in the disaster dispatch fleet via periodic heartbeats.
    """
    return android_sms_gateway_service.register_device(registration)


@router.get("/pending", response_model=List[QueuedEmergencySMS])
async def get_pending_sms_for_device(
    device_id: str = Query(..., description="Unique device ID of the polling Android phone"),
    limit: int = Query(5, ge=1, le=25, description="Maximum number of messages to fetch"),
):
    """
    Called by the background Android Gateway Service to pull pending emergency SMS.
    Returns messages and marks them as IN_TRANSIT with the querying device ID.
    """
    return android_sms_gateway_service.fetch_pending_sms(device_id=device_id, limit=limit)


@router.post("/ack", response_model=Dict[str, Any])
async def acknowledge_sms_delivery(receipt: AndroidDeliveryReceipt):
    """
    Android SmsManager callback: reports cellular transmission result (DELIVERED or FAILED).
    """
    updated = android_sms_gateway_service.acknowledge_delivery(receipt)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SMS task with id {receipt.sms_id} not found in gateway queue.",
        )
    return {
        "status": "SUCCESS",
        "sms_id": updated.sms_id,
        "delivery_status": updated.status,
        "delivered_at": updated.delivered_at.isoformat() if updated.delivered_at else None,
    }


@router.post("/dispatch", response_model=QueuedEmergencySMS)
async def dispatch_emergency_sms_to_android(payload: DirectDispatchRequest):
    """
    Disaster Control Room endpoint to route an emergency SMS directly to field Android SIMs.
    """
    return android_sms_gateway_service.enqueue_sms(
        recipient_phone=payload.recipient_phone,
        message=payload.message,
        target_community=payload.target_community,
        hazard_tier=payload.hazard_tier,
        safe_shelter=payload.safe_shelter,
        route_direction=payload.route_direction,
    )


@router.get("/devices", response_model=List[AndroidDeviceRegistration])
async def list_registered_android_devices():
    """
    Returns all registered Android dispatch units along with their battery and cellular carrier status.
    """
    return android_sms_gateway_service.list_active_devices()


@router.get("/queue")
async def get_android_queue_status():
    """
    Returns queue status, count of pending, in-transit, and delivered messages.
    """
    return {
        "status": "ONLINE",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metrics": android_sms_gateway_service.get_queue_status(),
        "recent_messages": [
            {
                "sms_id": m.sms_id,
                "recipient": m.recipient_phone,
                "status": m.status,
                "tier": m.hazard_tier,
                "created_at": m.created_at.isoformat(),
                "device_id": m.device_id,
            }
            for m in android_sms_gateway_service.list_all_messages(limit=10)
        ],
    }
