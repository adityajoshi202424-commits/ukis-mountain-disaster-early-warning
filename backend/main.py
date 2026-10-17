"""
Flash Flood Early Warning Platform — FastAPI Application

Entry point for the backend API.
All data served through here comes from real sources with provenance.
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import DataMode, settings
from backend.data.providers.registry import provider_registry

logger = structlog.get_logger(__name__)

# Current operating mode — displayed in every API response and UI
CURRENT_DATA_MODE = DataMode.LIVE


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown."""
    # Startup
    logger.info("application_starting", env=settings.app_env.value)
    await provider_registry.initialize()

    # Check initial provider health in background
    import asyncio
    async def _bg_check():
        try:
            health = await asyncio.wait_for(provider_registry.check_all_health(), timeout=5.0)
            for name, h in health.items():
                logger.info(
                    "provider_status",
                    provider=name,
                    status=h.status.value,
                    credentials=h.credentials_configured,
                )
        except Exception as e:
            logger.warning("background_health_check_skipped", error=str(e))
    asyncio.create_task(_bg_check())

    yield

    # Shutdown
    await provider_registry.shutdown()
    logger.info("application_shutdown")


app = FastAPI(
    title="UKIS 2026 (P-011): AI Mountain Disaster Early-Warning Intelligence",
    description=(
        "Geospatial early-warning platform combining historical and near-real-time environmental "
        "data to monitor mountain hazards and communicate explainable risk assessments. "
        "Primary region: Uttarakhand (Devbhoomi), India. "
        "All data sourced from verified external providers with full provenance. Zero fabricated data."
    ),
    version="1.0.0",
    lifespan=lifespan,
    swagger_ui_parameters={"docExpansion": "list", "filter": True, "tryItOutEnabled": True},
)

# Config-driven CORS with Vercel and local environment support
configured_origins_env = os.environ.get("ALLOWED_ORIGINS", os.environ.get("CORS_ORIGINS", ""))
cors_origins = [o.strip() for o in configured_origins_env.split(",") if o.strip()]
default_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://frontend-rosy-phi-23.vercel.app",
]
for origin in default_origins:
    if origin not in cors_origins:
        cors_origins.append(origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=r"^https://.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Import and register route modules
# ---------------------------------------------------------------------------

from backend.api.v1 import data as data_routes  # noqa: E402
from backend.api.v1 import system as system_routes  # noqa: E402
from backend.api.v1 import sih_demo as sih_demo_routes  # noqa: E402
from backend.api.v1 import auth as auth_routes  # noqa: E402
from backend.api.v1 import classification as classification_routes  # noqa: E402
from backend.api.v1 import alerts as alert_routes  # noqa: E402
from backend.api.v1 import telemetry as telemetry_routes  # noqa: E402
from backend.api.v1 import sih_ps192_engine  # noqa: E402
from backend.api.v1 import mountain_hazard_engine  # noqa: E402
from backend.api.v1 import action_layer  # noqa: E402
from backend.api.v1 import android_gateway  # noqa: E402
from backend.api.v1 import sse_push_gateway  # noqa: E402
from backend.api.v1 import user_profile  # noqa: E402
from backend.api.v1 import user_and_ops_endpoints  # noqa: E402

# UKIS 2026 Problem Statement P-011 Core Router
app.include_router(mountain_hazard_engine.router, prefix="/api/v1")
app.include_router(data_routes.router, prefix="/api/v1")
app.include_router(system_routes.router, prefix="/api/v1")
app.include_router(sih_demo_routes.router, prefix="/api/v1")
app.include_router(auth_routes.router, prefix="/api/v1")
app.include_router(classification_routes.router, prefix="/api/v1")
app.include_router(alert_routes.router, prefix="/api/v1")
app.include_router(telemetry_routes.router, prefix="/api/v1")
app.include_router(sih_ps192_engine.router, prefix="/api/v1")
app.include_router(action_layer.router, prefix="/api/v1")
app.include_router(android_gateway.router, prefix="/api/v1")
app.include_router(sse_push_gateway.router, prefix="/api/v1")
app.include_router(user_profile.router, prefix="/api/v1")
app.include_router(user_and_ops_endpoints.router)


from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Mount static files
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/sih-demo", response_class=FileResponse)
async def sih_demo_page():
    """Serves the SIH Demonstration & Historical Evaluation interactive UI."""
    demo_file = static_dir / "sih_demo.html"
    if demo_file.exists():
        return FileResponse(demo_file)
    return {"error": "Demo interface file not found"}


@app.get("/")
async def root():
    """Root endpoint — UKIS P-011 system status summary and quick navigation."""
    return {
        "system": "AI Mountain Disaster Early-Warning Intelligence",
        "problem_code": "P-011",
        "hackathon": "UKIS 2026 (Uttarakhand Innovation & Solutions Hackathon)",
        "problem_url": "https://www.axocom.in/UKISHackathon/problems/P-011",
        "version": "1.0.0",
        "region": "Uttarakhand (Devbhoomi), India",
        "authority": "Uttarakhand State Disaster Management Authority (USDMA)",
        "partner": "ITDA Uttarakhand & SDRF",
        "data_mode": CURRENT_DATA_MODE.value,
        "capabilities": [
            "Monitor glaciers and analyse snow-cover change (GLOF)",
            "Assess flash-flood and landslide risk",
            "Monitor fragile mountain slopes for meaningful change",
            "Combine weather, terrain, hydrology and remote-sensing layers",
            "Issue explainable, severity-based warnings for high-risk locations",
        ],
        "mountain_hazard_api": "/api/v1/mountain",
        "api_docs": "/docs",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "operational",
        "data_integrity_notice": (
            "All data served by this system comes from verified external sources "
            "(Open-Meteo Weather, Open-Meteo Elevation SRTM DEM, GloFAS River Discharge, USGS Earthquakes). "
            "No values are fabricated. Missing data is reported as DATA UNAVAILABLE."
        ),
    }


@app.get("/health")
async def health_check():
    """System health check."""
    provider_health = await provider_registry.check_all_health()
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data_mode": CURRENT_DATA_MODE.value,
        "providers": {
            name: {
                "status": h.status.value,
                "credentials_configured": h.credentials_configured,
            }
            for name, h in provider_health.items()
        },
        "unavailable_providers": provider_registry.get_unavailable_providers(),
    }


@app.post("/alerts/critical/trigger-siren")
async def trigger_critical_siren_alias(payload: Optional[dict] = None):
    """
    Direct hackathon specification alias: POST /alerts/critical/trigger-siren
    Actuates on-site physical buzzer / strobe relay for high-altitude community alarms.
    """
    from backend.services.emergency_notification_router import emergency_notification_router
    stn_id = (payload or {}).get("station_id", "UK-CHAMOLI-01")
    district = (payload or {}).get("district", "Chamoli")
    return await emergency_notification_router.trigger_physical_siren(
        station_id=stn_id,
        district=district,
        alert_level="CRITICAL",
    )

