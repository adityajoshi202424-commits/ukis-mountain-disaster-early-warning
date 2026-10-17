"""
Server-Sent Events (SSE) & Real-Time Push Gateway
UKIS P-011 Mountain Disaster Intelligence — Low-Latency Broadcast Gateway

Provides:
- GET /api/v1/stream/alerts: High-efficiency SSE stream for real-time alert push
- GET /api/v1/alerts/unified: Direct query of current normalized disaster alerts
- POST /api/v1/stream/broadcast: Broadcasts new emergency alert across SSE and C-DOT channels
- GET /api/v1/shelters/live: Queries live USDMA high-ground safety hubs
- GET /api/v1/hazards/matrix: Returns the 14+ Indian & Himalayan hazard registry
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from typing import AsyncGenerator, Dict, List, Optional, Any
from fastapi import APIRouter, Query, Request, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from backend.services.indian_hazard_matrix import indian_hazard_engine
from backend.services.payload_normalizer import payload_normalizer, UnifiedDisasterAlertPayload
from backend.services.usdma_shelter_registry import usdma_shelter_service, SafetyHubFacility
from backend.services.resilient_cache import resilient_cache
from backend.services.cdot_cell_broadcast import cdot_broadcast_service

router = APIRouter(prefix="/stream", tags=["Indian Emergency Push Gateway"])

# Global event bus for SSE listeners
_subscribers: List[asyncio.Queue] = []
_active_alerts_store: List[UnifiedDisasterAlertPayload] = []


class EmergencyBroadcastRequest(BaseModel):
    hazard_code: str = Field(..., description="Hazard key from 14-hazard matrix (e.g. FLASH_FLOOD_GLOF)")
    districts: List[str] = Field(default_factory=lambda: ["Chamoli", "Rudraprayag"])
    severity: str = Field(default="CRITICAL", description="'CRITICAL' | 'ALERT' | 'WATCH' | 'NORMAL'")
    en_title: Optional[str] = None
    en_instruction: Optional[str] = None
    trigger_cell_broadcast: bool = True


async def alert_event_generator(request: Request, district: Optional[str] = None) -> AsyncGenerator[str, None]:
    """Generates SSE formatted events for connected mobile clients."""
    queue: asyncio.Queue = asyncio.Queue(maxsize=100)
    _subscribers.append(queue)

    try:
        # 1. Send initial heartbeat and connection confirmation
        connect_msg = {
            "type": "CONNECTION_ESTABLISHED",
            "timestamp": int(datetime.now(timezone.utc).timestamp()),
            "state": "Uttarakhand",
            "monitored_district": district or "ALL_DISTRICTS",
        }
        yield f"event: connect\ndata: {json.dumps(connect_msg)}\n\n"

        # 2. Replay active alerts
        for alert in _active_alerts_store:
            if not district or any(d.lower() == district.lower() for d in alert.localization.districts):
                yield f"event: alert\ndata: {json.dumps(alert.model_dump())}\n\n"

        # 3. Stream new alerts as they arrive
        while True:
            if await request.is_disconnected():
                break

            try:
                alert_payload = await asyncio.wait_for(queue.get(), timeout=15.0)
                if not district or any(d.lower() == district.lower() for d in alert_payload.localization.districts):
                    yield f"event: alert\ndata: {json.dumps(alert_payload.model_dump())}\n\n"
            except asyncio.TimeoutError:
                # Periodic keep-alive ping (vital for mobile 2G/3G connections)
                ping = {"type": "HEARTBEAT", "timestamp": int(datetime.now(timezone.utc).timestamp())}
                yield f": ping {json.dumps(ping)}\n\n"

    finally:
        if queue in _subscribers:
            _subscribers.remove(queue)


@router.get("/alerts")
async def stream_disaster_alerts(
    request: Request,
    district: Optional[str] = Query(None, description="Filter stream to a specific Uttarakhand district"),
):
    """
    Server-Sent Events (SSE) endpoint:
    Streams live unified emergency alerts to mobile applications with 0 polling overhead.
    """
    return StreamingResponse(
        alert_event_generator(request=request, district=district),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/broadcast", response_model=UnifiedDisasterAlertPayload)
async def broadcast_emergency_alert(payload: EmergencyBroadcastRequest):
    """
    Broadcasts an official emergency warning across all active SSE listeners and C-DOT Cell Broadcast.
    """
    # 1. Attach nearest shelter for the primary district
    primary_dist = payload.districts[0] if payload.districts else "Chamoli"
    shelters = usdma_shelter_service.list_all_shelters(primary_dist)
    nearest_sh = shelters[0].model_dump() if shelters else None

    # 2. Normalize payload
    normalized = payload_normalizer.normalize_from_hazard(
        hazard_code=payload.hazard_code,
        districts=payload.districts,
        source="SEOC_UTTARAKHAND_FEED",
        severity_override=payload.severity,
        custom_en_title=payload.en_title,
        custom_en_instruction=payload.en_instruction,
        nearest_shelter=nearest_sh,
    )

    # 3. Store active alert
    _active_alerts_store.append(normalized)

    # 4. Trigger C-DOT cell broadcast if requested
    if payload.trigger_cell_broadcast and payload.severity in ("CRITICAL", "ALERT"):
        cdot_broadcast_service.format_cell_broadcast(normalized, target_district=primary_dist)

    # 5. Push to all active mobile SSE subscribers
    for q in list(_subscribers):
        try:
            q.put_nowait(normalized)
        except asyncio.QueueFull:
            pass

    return normalized


# Extra helper endpoints mounted on the same router for clean client aggregation
@router.get("/alerts/unified", response_model=List[UnifiedDisasterAlertPayload])
async def list_unified_active_alerts(
    district: Optional[str] = Query(None, description="Optional district filter"),
):
    """Returns all currently active unified disaster alerts."""
    if not _active_alerts_store:
        # Generate current live monitoring alert if none explicitly triggered
        shelter, dist_km, direction = usdma_shelter_service.find_nearest_safety_hub(30.5526, 79.5632)
        base_alert = payload_normalizer.normalize_from_hazard(
            hazard_code="FLASH_FLOOD_GLOF",
            districts=["Chamoli", "Rudraprayag"],
            source="NDMA_CAP_GATEWAY",
            severity_override="ALERT",
            nearest_shelter=shelter.model_dump(),
        )
        return [base_alert]

    if district:
        return [a for a in _active_alerts_store if any(d.lower() == district.lower() for d in a.localization.districts)]
    return _active_alerts_store


@router.get("/shelters/live", response_model=List[SafetyHubFacility])
async def get_live_shelters(
    district: Optional[str] = Query(None, description="Filter by Uttarakhand district"),
):
    """Lists certified USDMA high-ground safety hubs and current available capacity."""
    return usdma_shelter_service.list_all_shelters(district=district)


@router.get("/shelters/nearest")
async def get_nearest_shelter(
    lat: float = Query(..., ge=28.7, le=31.5),
    lon: float = Query(..., ge=77.5, le=81.1),
):
    """Calculates nearest safety hub, distance in kilometers, and compass vector."""
    sh, dist_km, direction = usdma_shelter_service.find_nearest_safety_hub(lat, lon)
    return {
        "nearest_shelter": sh,
        "distance_km": dist_km,
        "compass_direction": direction,
        "recommended_action": f"Head {direction} towards {sh.name} ({dist_km} km away).",
    }


@router.get("/hazards/matrix")
async def get_indian_hazard_matrix():
    """Returns the full 14+ Indian & Himalayan hazard registry."""
    return {
        "status": "SUCCESS",
        "jurisdiction": "Republic of India & State of Uttarakhand",
        "total_hazards": len(indian_hazard_engine.list_all_hazards()),
        "hazards": indian_hazard_engine.list_all_hazards(),
    }
