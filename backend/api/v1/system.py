"""
Flash Flood Early Warning Platform — System API Routes

Provider health, data source registry, system status.
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter

from backend.config import DataMode, settings
from backend.data.providers.registry import provider_registry
from backend.regions.uttarakhand.config import REGION_CONFIG

CURRENT_DATA_MODE = DataMode.LIVE

router = APIRouter(tags=["system"])


@router.get("/system/providers")
async def list_providers():
    """
    List all registered data providers and their status.

    Shows:
    - Available providers with metadata
    - Unavailable providers with reason and required configuration
    """
    registered = provider_registry.list_providers()
    unavailable = provider_registry.get_unavailable_providers()
    health = await provider_registry.check_all_health()

    return {
        "data_mode": CURRENT_DATA_MODE.value,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "registered_providers": [
            {
                **p,
                "health": {
                    "status": health[p["name"]].status.value,
                    "credentials": health[p["name"]].credentials_configured,
                }
                if p["name"] in health
                else {"status": "UNKNOWN"},
            }
            for p in registered
        ],
        "unavailable_providers": unavailable,
        "notice": (
            "Providers marked API_KEY_REQUIRED need credentials configured in .env. "
            "The system operates with available providers and honestly reports "
            "which data sources are missing."
        ),
    }


@router.get("/system/providers/{provider_name}/health")
async def get_provider_health(provider_name: str):
    """Get detailed health status for a specific provider."""
    health = await provider_registry.get_health(provider_name)
    if health is None:
        return {
            "provider": provider_name,
            "status": "NOT_REGISTERED",
            "message": f"Provider '{provider_name}' is not registered in the system.",
        }
    return {
        "provider": provider_name,
        "status": health.status.value,
        "credentials_configured": health.credentials_configured,
        "last_successful_fetch": (
            health.last_successful_fetch.isoformat()
            if health.last_successful_fetch
            else None
        ),
        "last_error": health.last_error,
    }


@router.get("/system/regions")
async def list_regions():
    """List available regions. Primary region: Uttarakhand (Devbhoomi)."""
    return {
        "regions": [
            {
                "region_id": REGION_CONFIG["region_id"],
                "name": REGION_CONFIG["name"],
                "country": REGION_CONFIG["country"],
                "center": {
                    "lat": REGION_CONFIG["center_lat"],
                    "lon": REGION_CONFIG["center_lon"],
                },
                "zoom": REGION_CONFIG["default_zoom"],
                "flood_season": REGION_CONFIG["flood_season"],
                "available_providers": REGION_CONFIG["available_providers"],
            }
        ],
        "notice": "Additional regions can be added without rewriting core logic.",
    }


@router.get("/system/regions/{region_id}")
async def get_region_detail(region_id: str):
    """Get detailed configuration for a region."""
    if region_id != REGION_CONFIG["region_id"]:
        return {
            "error": f"Region '{region_id}' not found.",
            "available_regions": [REGION_CONFIG["region_id"]],
        }
    return {
        "region": REGION_CONFIG,
        "risk_thresholds_notice": (
            "Risk thresholds are INITIAL values and have NOT been validated "
            "against historical events. Calibration pending Phase 9-10 backtesting."
        ),
    }


@router.get("/system/data-mode")
async def get_data_mode():
    """
    Get current operating data mode.
    The UI MUST display this prominently.
    """
    mode_display = {
        "LIVE": "● LIVE DATA",
        "HISTORICAL": "◷ HISTORICAL DATA",
        "REPLAY": "◷ HISTORICAL REPLAY",
        "SIMULATION": "⚠ SIMULATION MODE",
    }
    return {
        "mode": CURRENT_DATA_MODE.value,
        "display": mode_display.get(CURRENT_DATA_MODE.value, CURRENT_DATA_MODE.value),
        "description": {
            "LIVE": "Real-time/recent external observations.",
            "HISTORICAL": "Real historical observations.",
            "REPLAY": "Historical data being replayed chronologically.",
            "SIMULATION": "Synthetic values for development/testing ONLY.",
        }[CURRENT_DATA_MODE.value],
    }


# ---------------------------------------------------------------------------
# Feature 2: Satellite Blind-Spot & Cloud-Piercing Radar Controller
# ---------------------------------------------------------------------------

from backend.services.satellite_fallback import (
    satellite_fallback_controller,
    RadarInterpolationResult,
)
from fastapi import Query


@router.get("/system/satellite-status", response_model=RadarInterpolationResult)
async def get_satellite_pipeline_status(
    cloud_cover_pct: float = Query(default=94.5, ge=0.0, le=100.0, description="Optical cloud coverage score"),
    is_satellite_blackout: bool = Query(default=False, description="Simulate total satellite constellation blackout"),
):
    """
    Cloud-Piercing Radar Interpolation & Satellite Blind-Spot Monitor.
    If cloud cover > 92%, shifts from optical to Sentinel-1 C-band Synthetic Aperture Radar.
    If total blackout, shifts to 1D hydrodynamic ground telemetry mesh.
    """
    return satellite_fallback_controller.evaluate_satellite_pipeline(
        cloud_cover_pct=cloud_cover_pct,
        is_satellite_blackout=is_satellite_blackout,
    )


# ---------------------------------------------------------------------------
# Feature 3: Secure Administrative Audit Logging (Immutable Hash Chain)
# ---------------------------------------------------------------------------

from backend.services.audit_logger import audit_logger, AuditLogRecord
from typing import List


@router.get("/system/audit-trail")
async def get_system_audit_trail(limit: int = Query(default=25, ge=1, le=100)):
    """
    Retrieves the cryptographically signed append-only audit trail.
    Verifies SHA-256 hash chain integrity for tamper-proof government accountability.
    """
    is_valid, checked_count = audit_logger.verify_integrity()
    logs = audit_logger.get_recent_logs(limit=limit)

    return {
        "audit_integrity_status": "VERIFIED_TAMPER_PROOF" if is_valid else "CORRUPTED_HASH_MISMATCH",
        "hash_chain_verified": is_valid,
        "total_records_checked": checked_count,
        "verification_timestamp": datetime.now(timezone.utc).isoformat(),
        "cryptographic_algorithm": "SHA-256 Recursive Chain",
        "genesis_hash": audit_logger.GENESIS_HASH,
        "latest_block_hash": logs[-1].current_hash if logs else audit_logger.GENESIS_HASH,
        "audit_logs": logs,
    }


# ---------------------------------------------------------------------------
# Section 3.17: System Limitations & What This System Does Not Claim
# ---------------------------------------------------------------------------

from backend.services.system_limitations import system_limitations_service, SystemLimitationsReport


@router.get("/system/limitations", response_model=SystemLimitationsReport)
async def get_system_limitations():
    """
    UKIS Addendum v2 Section 3.17: System Limitations & Operational Boundaries.
    Transparently reports:
    - Watershed coverage matrix (Full vs. Partial vs. None)
    - Feature maturity classification (Tiers 1 to 4)
    - Data latency citations
    - Probabilistic decision-support disclaimer (not an IMD/NDMA replacement)
    """
    return system_limitations_service.get_limitations_report()


