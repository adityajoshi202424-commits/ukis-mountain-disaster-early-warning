"""
User Profile & Remote Subscriber Localization State Management
UKIS DMMC Uttarakhand Multi-Platform Disaster Warning System

Handles real-time subscriber registration, device push tokens, and language preference handshakes:
- POST /api/v1/user/update-locale
- GET /api/v1/user/profile
"""

from __future__ import annotations

import time
from typing import Dict, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/user", tags=["User Localization & Subscriber Profile"])

# In-memory subscriber registry (can be persisted to PostgreSQL/Redis)
_subscriber_profiles: Dict[str, Dict] = {}


class LocalizationSyncRequest(BaseModel):
    phone: Optional[str] = Field(default=None, description="Subscriber contact number")
    token: Optional[str] = Field(default=None, description="FCM / APNs device push token")
    locale: str = Field(..., description="Locale code: 'hi' | 'en' | 'gb' | 'ku' or 'hi-IN' | 'en-IN' | 'gb-IN' | 'ku-IN'")
    preferred_dialect_fallback: Optional[str] = Field(default="hi", description="Fallback dialect code")
    timestamp: Optional[int] = Field(default=None, description="Client sync timestamp in epoch ms")


class LocalizationSyncResponse(BaseModel):
    status: str
    message: str
    subscriber_id: str
    applied_locale: str
    preferred_dialect_fallback: str
    sync_timestamp: int


@router.post("/update-locale", response_model=LocalizationSyncResponse)
async def update_user_locale(payload: LocalizationSyncRequest):
    """
    Synchronizes the user's active language and dialect preference across the distributed
    disaster notification infrastructure (Push Notifications, Cell Broadcast, and SMS Dispatch).
    """
    valid_locales = {
        "hi": "hi-IN", "hi-in": "hi-IN",
        "en": "en-IN", "en-in": "en-IN",
        "gb": "gb-IN", "gb-in": "gb-IN", "gar": "gb-IN",
        "ku": "ku-IN", "ku-in": "ku-IN", "kum": "ku-IN",
    }
    
    normalized_locale = valid_locales.get(payload.locale.lower(), "en-IN")
    subscriber_id = payload.phone or payload.token or "anonymous_device"
    now_epoch = int(time.time() * 1000)

    profile_data = {
        "phone": payload.phone,
        "token": payload.token,
        "locale": normalized_locale,
        "fallback": payload.preferred_dialect_fallback or "hi",
        "last_synced_at": now_epoch,
    }

    if payload.phone:
        raw_phone = payload.phone.strip()
        _subscriber_profiles[raw_phone] = profile_data
        _subscriber_profiles[raw_phone.replace("+", "").strip()] = profile_data
        _subscriber_profiles[raw_phone.replace("+", " ").strip()] = profile_data
    if payload.token:
        _subscriber_profiles[payload.token.strip()] = profile_data

    logger.info(
        "user_locale_synchronized",
        subscriber_id=subscriber_id,
        locale=normalized_locale,
        timestamp=now_epoch,
    )

    return LocalizationSyncResponse(
        status="SUCCESS_SYNCHRONIZED",
        message="Subscriber localization profile updated successfully.",
        subscriber_id=subscriber_id,
        applied_locale=normalized_locale,
        preferred_dialect_fallback=payload.preferred_dialect_fallback or "hi",
        sync_timestamp=now_epoch,
    )


@router.get("/profile")
async def get_user_profile(identifier: str):
    """Retrieves subscriber preferences for the given phone or device token."""
    clean_id = identifier.strip()
    profile = (
        _subscriber_profiles.get(clean_id)
        or _subscriber_profiles.get("+" + clean_id.lstrip("+ "))
        or _subscriber_profiles.get(clean_id.replace(" ", "+"))
        or _subscriber_profiles.get(clean_id.replace("+", ""))
    )
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subscriber profile not found for identifier: {identifier}",
        )
    return profile

