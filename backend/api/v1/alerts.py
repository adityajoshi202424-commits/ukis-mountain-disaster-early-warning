"""
Alert & Emergency Dispatch API Router

Endpoints:
- GET /api/v1/alerts/active (List currently active flood warnings)
- POST /api/v1/alerts/dispatch (Dispatch new warning across SMS, Push, Webhooks)
- GET /api/v1/alerts/cap/{alert_id}.xml (Common Alerting Protocol CAP v1.2 XML output)
- POST /api/v1/alerts/{alert_id}/acknowledge (Operator acknowledgment)
"""

from __future__ import annotations

from typing import List, Optional
import time
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Response, Depends, Request
from backend.services.alert_dispatch import (
    alert_dispatch_service,
    AlertPayload,
    AlertRecord,
)
from backend.services.emergency_notification_router import (
    emergency_notification_router,
    EmergencySMSPayload,
    DispatchResult,
    TelemetryTriggers,
)
from backend.services.auth import require_role
from backend.services.cap_serializer import serialize_cap_alert

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/sync/alerts/minimal")
async def minimal_alert_sync():
    """Return compact alert vectors for low-bandwidth browser cache updates."""
    return [
        [
            alert.alert_id,
            alert.risk_level,
            alert.region,
            round(alert.latitude, 5),
            round(alert.longitude, 5),
            alert.created_at.isoformat(),
            alert.expires_at.isoformat(),
        ]
        for alert in alert_dispatch_service.list_active_alerts()
        if alert.status == "ACTIVE"
    ]


@router.get("/active", response_model=List[AlertRecord])
async def list_active_alerts():
    """Lists all active emergency flash flood warnings."""
    return alert_dispatch_service.list_active_alerts()


@router.post("/dispatch", response_model=AlertRecord)
async def dispatch_emergency_alert(
    payload: AlertPayload,
    current_user: Optional[dict] = Depends(require_role(["OPERATOR", "ADMIN"])),
):
    """
    Dispatches a new emergency alert across SMS, Push (FCM), CAP XML, and Webhooks.
    Requires OPERATOR or ADMIN role.
    """
    return alert_dispatch_service.dispatch_alert(payload)


@router.get("/cap/{alert_id}.xml")
async def get_cap_xml_format(alert_id: str):
    """Returns official CAP v1.2 XML emergency message for NDMA / ASDMA ingestion."""
    alert = alert_dispatch_service.active_alerts.get(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    xml_content = serialize_cap_alert(
        sender="usdma.eoc@uk.gov.in",
        headline=f"URGENT: Mountain hazard warning for {alert.region}",
        description=alert.reason,
        area_description=alert.region,
        latitude=alert.latitude,
        longitude=alert.longitude,
        severity="Extreme" if alert.risk_level == "CRITICAL" else "Severe",
        identifier=alert.alert_id,
    )
    return Response(content=xml_content, media_type="application/xml")


@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    current_user: Optional[dict] = Depends(require_role(["OPERATOR", "ADMIN"])),
):
    """Records operator acknowledgment of an active warning."""
    username = current_user.get("username", "operator") if current_user else "operator"
    record = alert_dispatch_service.acknowledge_alert(alert_id, username)
    if not record:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"status": "success", "alert": record}


# ---------------------------------------------------------------------------
# Emergency SMS Router Endpoints (with Evaluation Mode Simulation Failsafe)
# ---------------------------------------------------------------------------

from backend.services.emergency_notification_router import (
    emergency_notification_router,
    EmergencySMSPayload,
    DispatchResult,
)


class DirectMobileSMSPayload(BaseModel):
    recipient_phone: str = Field(..., json_schema_extra={"example": "+919837012345"})
    district: str = Field(default="Chamoli", json_schema_extra={"example": "Chamoli"})
    language: str = Field(default="hi", description="'en' | 'hi' | 'gar' | 'kum' | 'jau' | 'sa'")
    hazard_level: str = Field(default="HIGH", description="'HIGH' | 'CRITICAL' | 'WARNING'")
    river_surge_m_hr: Optional[float] = Field(default=1.45)
    custom_notes: Optional[str] = None


@router.post("/send-live-sms")
async def send_live_mobile_sms(payload: DirectMobileSMSPayload):
    """
    Real Mobile Emergency SMS Dispatcher.
    Dispatches live alert directly to a real citizen/authority mobile phone number:
    1. Synthesizes official vernacular emergency broadcast in target regional dialect.
    2. Sends via Twilio REST API if credentials exist.
    3. Generates native cellular SMS deep-link (`sms:+919864...?body=...`) for instant mobile device dispatch.
    """
    import urllib.parse
    from backend.utils.localization_engine import localization_engine, LOCALIZATION_REGISTRY

    # Generate dialect alert
    localized_dict = localization_engine.generate_localized_alert(
        district=payload.district,
        river_surge_m_hr=payload.river_surge_m_hr or 1.45,
        risk_level=payload.hazard_level,
        horizon_minutes=45,
    )
    alert_text = localized_dict.get(payload.language.lower(), localized_dict.get("en", "Flash Flood Warning"))
    if payload.custom_notes:
        alert_text += f" Note: {payload.custom_notes}"

    # Clean phone number
    phone = payload.recipient_phone.strip().replace(" ", "").replace("-", "")
    if not phone.startswith("+") and len(phone) == 10:
        phone = f"+91{phone}"

    # Prepare native cellular SMS intent URL
    encoded_body = urllib.parse.quote(alert_text)
    sms_native_uri = f"sms:{phone}?body={encoded_body}"

    # Dispatch through EmergencyNotificationRouter in LIVE_PRODUCTION mode
    live_payload = EmergencySMSPayload(
        event_id=f"LIVE-MOBILE-{int(time.time())}",
        mode="LIVE_PRODUCTION",
        target_community=f"{payload.district}_Live_Zone",
        telemetry_triggers=TelemetryTriggers(
            river_surge_m_hr=payload.river_surge_m_hr or 1.45,
            rain_velocity_mm_hr=35.0,
            soil_saturation_pct=88.0,
        ),
        alert_message=alert_text,
        localized_alerts=localized_dict,
        recipient_phone=phone,
    )
    
    dispatch_res = await emergency_notification_router.dispatch_critical_alert(live_payload)

    return {
        "status": "SUCCESS",
        "dispatch_id": dispatch_res.dispatch_id,
        "recipient_phone": phone,
        "district": payload.district,
        "language": payload.language,
        "language_name": LOCALIZATION_REGISTRY.get(payload.language.lower(), {}).get("language_name", payload.language),
        "alert_text": alert_text,
        "carrier_dispatch_status": dispatch_res.status,
        "status_message": dispatch_res.status_message,
        "sms_native_uri": sms_native_uri,
        "execution_time_ms": dispatch_res.execution_time_ms,
        "dispatched_at": dispatch_res.dispatched_at.isoformat(),
    }


@router.post("/sms-dispatch", response_model=DispatchResult)
async def dispatch_emergency_sms(payload: EmergencySMSPayload):
    """
    Dispatches immediate SMS early warning.
    Enforces Failsafe: If mode is HISTORICAL_REPLAY or SIMULATION, intercepts network calls and logs payload.
    """
    return await emergency_notification_router.dispatch_critical_alert(payload)


@router.get("/sms-logs", response_model=List[DispatchResult])
async def get_emergency_sms_logs():
    """Retrieves real-time audit logs of outbound emergency SMS notifications."""
    return emergency_notification_router.get_audit_logs()


# ---------------------------------------------------------------------------
# Authority Voice Escalation Calling Endpoints (Moving beyond passive dashboard)
# ---------------------------------------------------------------------------
from backend.services.authority_call_dispatcher import (
    authority_call_dispatcher,
    AuthorityCallRequest,
    CallDetailRecord,
    NodalAuthorityContact,
)


@router.post("/call-authorities")
async def trigger_emergency_authority_calls(
    payload: AuthorityCallRequest,
    mode: str = "LIVE_PRODUCTION",
):
    """
    Automated Authority Escalation Call Dispatch.
    Initiates emergency phone calls with synthesized bilingual audio briefings directly to:
    - State Emergency Operations Centre (SEOC)
    - SDRF High-Altitude Quick Response Teams
    - District Magistrate / DDMA EOC
    - NDRF Battalion Command
    """
    return await authority_call_dispatcher.dispatch_emergency_authority_calls(payload, mode=mode)


@router.get("/authorities/directory", response_model=List[NodalAuthorityContact])
async def get_nodal_authorities_directory(district: Optional[str] = None):
    """Lists official emergency contact directory of Uttarakhand disaster authorities."""
    return authority_call_dispatcher.get_directory(district=district)


@router.get("/authorities/call-logs", response_model=List[CallDetailRecord])
async def get_authority_call_detail_records(limit: int = 25):
    """Retrieves Call Detail Records (CDRs) of all automated authority phone calls."""
    return authority_call_dispatcher.get_call_records(limit=limit)


@router.post("/authorities/call-gather")
async def handle_call_gather_webhook(request: Request):
    """Twilio IVR Gather Webhook: Records officer DTMF keypad acknowledgment."""
    form_data = await request.form()
    digits = form_data.get("Digits", "1")
    call_sid = form_data.get("CallSid", "")
    authority_call_dispatcher.record_acknowledgment(call_id=call_sid, dtmf_digit=digits)
    return Response(
        content='<?xml version="1.0" encoding="UTF-8"?><Response><Say language="en-IN">Acknowledgment recorded. SDRF Quick Response Teams alerted.</Say></Response>',
        media_type="application/xml",
    )


