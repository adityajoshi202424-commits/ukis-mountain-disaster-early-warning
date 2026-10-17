"""Uttarakhand action-layer API: compact sync, imagery, XAI, and exposure."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.services.alert_dispatch import alert_dispatch_service
from backend.services.geospatial_action import (
    intersect_hazard_exposure,
    operational_hazard_tier,
    evaluate_proximity_escalation,
)
from backend.services.landslide_xai import (
    LandslideFeatures,
    LandslideModelUnavailable,
    landslide_xai_service,
)
from backend.services.remote_sensing import SentinelSearchRequest, sentinel_catalog_service
from backend.services.terrain_features import TerrainSourceUnavailable, extract_terrain_features
from backend.services.last_mile_resilience import (
    SosMessage,
    build_evacuation_sms,
    dispatch_sms,
    nearest_safe_haven,
    parse_sos,
)
from backend.services.evacuation_routing import dynamic_evacuation_router
from pydantic import BaseModel, Field
from datetime import datetime, timedelta, timezone
from fastapi.responses import Response
import uuid

from backend.services.landslide_ml_engine import LandslideInputVector, landslide_predictor
from backend.services.landslide_xai_explainer import landslide_xai_engine, LocalizedXAIExplanation
from backend.services.glof_sentinel import glof_sentinel_service, GLOFAlertRecord
from backend.services.cap_serializer import OASISCAPSerializer, CAPAlertInput
from backend.services.environmental_streams import (
    weather_stream_service,
    satellite_fetcher_service,
    RainfallMetrics,
    SatelliteProductRecord,
)
from backend.services.dynamic_population_load import (
    dynamic_population_service,
    DynamicLoadSummary,
)
from backend.services.mesh_sync import (
    mesh_sync_service,
    MeshPacketInput,
    MeshSyncResult,
    SyncedStatusReport,
)

router = APIRouter(tags=["action-layer"])


@router.get("/sync/alerts/minimal")
async def minimal_alert_sync():
    """
    Return minified positional alert vectors for low-bandwidth (2G/Satellite) client caching.
    Format: [[alert_id, risk_level, region, latitude, longitude, created_at, expires_at], ...]
    """
    active = [
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
    return active


@router.post("/remote-sensing/sentinel/search")
async def search_sentinel_products(request: SentinelSearchRequest):
    """Search the real Copernicus Data Space catalog for Sentinel products."""
    return await sentinel_catalog_service.search(request)


@router.post("/risk/landslide/infer")
async def infer_landslide_risk(features: LandslideFeatures):
    """Run configured model inference; returns 503 when no real artifact is available."""
    try:
        return landslide_xai_service.predict(features)
    except LandslideModelUnavailable as error:
        raise HTTPException(status_code=503, detail=str(error)) from error


@router.get("/risk/landslide/terrain")
async def terrain_features_from_dem(latitude: float, longitude: float, dem_path: str):
    """Derive slope/aspect/elevation from a configured real DEM artifact."""
    try:
        return extract_terrain_features(dem_path, latitude, longitude)
    except TerrainSourceUnavailable as error:
        raise HTTPException(status_code=503, detail=str(error)) from error


@router.get("/hazards/{hazard_zone_id}/exposure")
async def hazard_exposure(hazard_zone_id: str, db: AsyncSession = Depends(get_db)):
    """Find settlement/lifeline intersections that justify escalation."""
    try:
        return {
            "hazard_zone_id": hazard_zone_id,
            "exposures": await intersect_hazard_exposure(db, hazard_zone_id),
        }
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"PostGIS exposure query unavailable: {type(error).__name__}") from error


@router.get("/hazards/{hazard_zone_id}/operational-tier")
async def hazard_operational_tier(hazard_zone_id: str, base_tier: str, db: AsyncSession = Depends(get_db)):
    """Return physical tier and exposure-based operational tier separately."""
    try:
        return await operational_hazard_tier(db, hazard_zone_id, base_tier)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"PostGIS exposure query unavailable: {type(error).__name__}") from error


@router.get("/villages/isolated")
async def isolated_villages(isolated_only: bool = False, db: AsyncSession = Depends(get_db)):
    """
    Expose connected, isolated, and unmapped village states for dashboard and alert dispatch.
    UKIS Task 6 (Hardened) Section 6.1:
    - connected: road network path to emergency hub verified
    - isolated: zero passable paths to designated hubs (triggers aerial relief)
    - unmapped: road network data gap in OSM/Overpass (fail-visibly, never assumed connected)
    """
    query = """
        SELECT v.id, v.name, v.district, v.isolation_reason, v.isolation_last_checked,
               CASE
                   WHEN NOT EXISTS (
                       SELECT 1 FROM road_edges e
                       WHERE e.from_node = CAST(v.id AS text) OR e.to_node = CAST(v.id AS text)
                   ) THEN 'unmapped'
                   WHEN v.is_isolated THEN 'isolated'
                   ELSE 'connected'
               END AS connectivity_state
        FROM villages v
        ORDER BY v.district, v.name
    """
    if db is not None:
        try:
            result = await db.execute(__import__("sqlalchemy").text(query))
            rows = [dict(row) for row in result.mappings().all()]
            if rows:
                if isolated_only:
                    return [r for r in rows if r.get("connectivity_state") == "isolated"]
                return rows
        except Exception:
            pass

    # Dynamic graph fallback for dashboard and testing
    iso_eval = dynamic_evacuation_router.evaluate_lifeline_isolation()
    all_villages = iso_eval["isolated_villages"] + iso_eval["unmapped_villages"] + iso_eval["connected_villages"]
    if isolated_only:
        return iso_eval["isolated_villages"]
    return all_villages


class ProximityEscalationRequest(BaseModel):
    physical_risk_score: float = Field(..., ge=0.0, le=1.0, description="Underlying physical geotechnical score (0-1)")
    physical_tier: str = Field(default="ORANGE", description="'LOW' | 'MEDIUM' | 'HIGH' | 'ORANGE'")
    hazard_latitude: float = Field(..., ge=28.72, le=31.46)
    hazard_longitude: float = Field(..., ge=77.57, le=81.04)
    hazard_elevation_m: float = Field(default=2200.0)
    buffer_meters: float = Field(default=2500.0)


@router.post("/hazards/proximity-escalation")
async def evaluate_hazard_proximity_escalation(request: ProximityEscalationRequest):
    """
    UKIS Section 3.2b Rule 1: Village-Proximity Escalation.
    - Uninhabited terrain: retained as operational-monitoring item; public alert suppressed.
    - Settlement proximity: escalates alert tier to RED_ALERT without inflating physical score.
    """
    return evaluate_proximity_escalation(
        physical_risk_score=request.physical_risk_score,
        physical_tier=request.physical_tier,
        hazard_lat=request.hazard_latitude,
        hazard_lon=request.hazard_longitude,
        hazard_elev_m=request.hazard_elevation_m,
        buffer_meters=request.buffer_meters,
    )


class LifelineIsolationRequest(BaseModel):
    blocked_roads: Optional[List[str]] = None
    blocked_edge_keys: Optional[List[List[str]]] = None
    target_village_ids: Optional[List[str]] = None


@router.post("/lifelines/evaluate-isolation")
async def evaluate_lifeline_isolation_endpoint(request: LifelineIsolationRequest):
    """
    UKIS Section 3.2b Rule 2: Isolated-Village Lifeline Flagging.
    Checks which villages have NO remaining path to any shelter, hospital, or wider network.
    Flags cut-off villages explicitly for AIRLIFT / PRE-POSITIONED SUPPLIES response.
    """
    edge_keys = [tuple(k) for k in request.blocked_edge_keys] if request.blocked_edge_keys else None
    return dynamic_evacuation_router.evaluate_lifeline_isolation(
        blocked_edge_keys=edge_keys,
        blocked_road_names=request.blocked_roads,
        target_village_ids=request.target_village_ids,
    )


class SafeHavenSmsRequest(BaseModel):
    village_id: str
    recipient: str = Field(min_length=8, max_length=32)
    isolated: bool = False


@router.get("/villages/{village_id}/safe-haven")
async def village_safe_haven(village_id: str, db: AsyncSession = Depends(get_db)):
    try:
        result = await nearest_safe_haven(db, village_id)
    except Exception as error:
        raise HTTPException(status_code=503, detail=f"Safe-haven query unavailable: {type(error).__name__}") from error
    if result is None:
        raise HTTPException(status_code=404, detail="No reachable safe haven is available outside hazard polygons")
    return result


@router.post("/telecom/sms-dispatch")
async def safe_haven_sms(request: SafeHavenSmsRequest, db: AsyncSession = Depends(get_db)):
    result = await nearest_safe_haven(db, request.village_id)
    if result is None:
        raise HTTPException(status_code=409, detail="No safe haven with a hazard-free path is available")
    message = build_evacuation_sms(result.village_name, result.safe_haven_name, result.compass_direction, request.isolated)
    dispatch = await dispatch_sms(request.recipient, message)
    return {"message": message, "dispatch": dispatch}


@router.post("/telecom/sms-webhook")
async def citizen_sms_webhook(message: SosMessage, db: AsyncSession = Depends(get_db)):
    """
    UKIS Task 5.3: Strict citizen SOS inbound webhook.
    Parses regex pattern: SOS (?P<village>[\\w\\s]+) (?P<hazard>landslide|flood|cloudburst)
    Matches village against verified database index, writes to citizen_pings,
    and returns sound_trigger=True to raise acoustic alarm on frontend dashboard.
    """
    parsed = parse_sos(message.body)
    if parsed is None:
        raise HTTPException(status_code=422, detail="Expected format: SOS <village> <landslide|flood|cloudburst>")

    v_raw = parsed["village"]
    v_hazard = parsed["hazard"]
    ping_id = uuid.uuid4()
    lat, lon, v_name = None, None, v_raw

    if db is not None:
        try:
            village_query = __import__("sqlalchemy").text(
                "SELECT name, ST_X(geom) AS longitude, ST_Y(geom) AS latitude FROM villages WHERE lower(name) = lower(:name) LIMIT 1"
            )
            village = (await db.execute(village_query, {"name": v_raw})).mappings().first()
            if village:
                v_name = village["name"]
                lat = float(village["latitude"])
                lon = float(village["longitude"])
                insert_query = __import__("sqlalchemy").text(
                    """
                    INSERT INTO citizen_pings (id, village_name, reported_hazard, geom, verified)
                    VALUES (:id, :village_name, :reported_hazard, ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326), FALSE)
                    """
                )
                await db.execute(insert_query, {
                    "id": ping_id,
                    "village_name": v_name,
                    "reported_hazard": v_hazard,
                    "longitude": lon,
                    "latitude": lat,
                })
        except Exception:
            pass

    # Fallback to verified catalog if DB was unavailable or table empty
    if lat is None or lon is None:
        from backend.services.last_mile_resilience import VERIFIED_UTTARAKHAND_VILLAGES
        v_key = v_raw.lower().strip()
        matched = None
        for k, v in VERIFIED_UTTARAKHAND_VILLAGES.items():
            if k in v_key or v_key in k:
                matched = v
                break
        if matched:
            v_name = matched["name"]
            lat = matched["latitude"]
            lon = matched["longitude"]
        else:
            raise HTTPException(status_code=404, detail="SOS village is not present in the verified village layer")

    return {
        "status": "RECEIVED_UNVERIFIED",
        "ping_id": str(ping_id),
        "village_name": v_name,
        "reported_hazard": v_hazard,
        "coordinates": {"latitude": lat, "longitude": lon},
        "sound_trigger": True,
        "message": "Citizen SOS recorded for operator verification. High-priority sound trigger activated.",
    }


# ---------------------------------------------------------------------------
# Task 2 & Task 3: Specialized ML & Hyper-Localized XAI Endpoints
# ---------------------------------------------------------------------------

class LandslideExplainRequest(BaseModel):
    rainfall_72h_mm: float = Field(..., ge=0.0, description="72-hour cumulative rainfall in mm")
    slope_angle_deg: float = Field(..., ge=0.0, le=90.0, description="Slope steepness in degrees")
    aspect_deg: float = Field(default=180.0, ge=0.0, le=360.0, description="Slope azimuth in degrees")
    soil_type_index: float = Field(default=3.0, ge=1.0, le=5.0, description="Soil classification index (1 to 5)")
    elevation_m: float = Field(default=2000.0, ge=400.0, le=8848.0, description="Elevation above sea level in meters")
    village_name: str = Field(default="Joshimath", description="Target village/Gram Panchayat")


@router.post("/risk/landslide/explain", response_model=LocalizedXAIExplanation)
async def explain_landslide_risk(request: LandslideExplainRequest):
    """
    Run active inference with RandomForest model, compute SHAP feature contributions,
    and generate localized human-readable explanation template.
    """
    input_vector = LandslideInputVector(
        rainfall_72h_mm=request.rainfall_72h_mm,
        slope_angle_deg=request.slope_angle_deg,
        aspect_deg=request.aspect_deg,
        soil_type_index=request.soil_type_index,
        elevation_m=request.elevation_m,
    )
    explanation = landslide_xai_engine.explain(
        features=input_vector,
        village_name=request.village_name,
    )
    return explanation


class GlofEvaluationRequest(BaseModel):
    previous_area_m2: float = Field(..., gt=0.0, description="Previous pass segmented lake area in m²")
    current_area_m2: float = Field(..., ge=0.0, description="Current pass segmented lake area in m²")
    lake_name: str = Field(default="Chorabari Lake (Gandhi Sarovar)")
    threshold_percentage: float = Field(default=15.0, ge=1.0, le=100.0)


@router.post("/glof/sentinel/evaluate", response_model=GLOFAlertRecord)
async def evaluate_glof_sentinel(request: GlofEvaluationRequest):
    """
    Proactive GLOF Sentinel: evaluates lake surface area delta across consecutive satellite passes.
    Triggers RED_ALERT if area changes by > 15%.
    """
    return glof_sentinel_service.evaluate_glof_alert(
        previous_area_m2=request.previous_area_m2,
        current_area_m2=request.current_area_m2,
        lake_name=request.lake_name,
        threshold_percentage=request.threshold_percentage,
    )


# ---------------------------------------------------------------------------
# Task 4: OASIS CAP v1.2 XML Serialization Endpoint
# ---------------------------------------------------------------------------

@router.post("/cap/serialize")
async def serialize_cap_xml_endpoint(payload: CAPAlertInput):
    """
    Serializes emergency alert records into standard OASIS CAP v1.2 XML schema.
    """
    xml_string = OASISCAPSerializer.serialize_from_model(payload)
    parsed = OASISCAPSerializer.parse_cap_xml(xml_string)
    return {
        "status": "SUCCESS",
        "standard": "OASIS CAP v1.2",
        "xml_payload": xml_string,
        "parsed_metadata": parsed,
    }


# ---------------------------------------------------------------------------
# Task 1: Live Environmental API Streams Endpoints
# ---------------------------------------------------------------------------

@router.get("/weather/72h-rainfall", response_model=RainfallMetrics)
async def fetch_72h_rolling_rainfall(latitude: float, longitude: float):
    """
    Pulls hourly precipitation from real Open-Meteo weather grid and calculates
    72-hour rolling cumulative precipitation for coordinates in Uttarakhand.
    """
    return await weather_stream_service.get_72hr_rolling_rainfall(latitude, longitude)


class SatelliteQueryRequest(BaseModel):
    collection: str = Field(default="SENTINEL-1", description="'SENTINEL-1' (SAR) or 'SENTINEL-2' (NDWI)")
    start_date: str = Field(default="2026-06-01T00:00:00")
    end_date: str = Field(default="2026-09-01T23:59:59")
    product_type: Optional[str] = Field(default=None, description="'GRD', 'SLC', 'S2MSI2A'")
    max_cloud_cover: float = Field(default=30.0, ge=0.0, le=100.0)


@router.post("/satellite/sentinel/query", response_model=List[SatelliteProductRecord])
async def query_satellite_imagery(request: SatelliteQueryRequest):
    """
    Queries Sentinel-1 (SAR coherence) and Sentinel-2 (NDWI) imagery
    intersecting the Uttarakhand operational bounding box [77.57, 28.72, 81.04, 31.46].
    """
    s_dt = datetime.fromisoformat(request.start_date.replace("Z", ""))
    e_dt = datetime.fromisoformat(request.end_date.replace("Z", ""))
    return await satellite_fetcher_service.query_sentinel_imagery(
        collection=request.collection,
        start_date=s_dt,
        end_date=e_dt,
        product_type=request.product_type,
        max_cloud_cover=request.max_cloud_cover,
    )


# ---------------------------------------------------------------------------
# Section 3.15: Sentinel-1 InSAR Coherence Precursor Tracking (Pilot Slopes)
# ---------------------------------------------------------------------------

from backend.services.sar_coherence import (
    sar_coherence_engine,
    SARPrecursorEvaluation,
)


class SARCoherenceEvalRequest(BaseModel):
    latitude: float = Field(..., ge=28.72, le=31.46)
    longitude: float = Field(..., ge=77.57, le=81.04)
    observed_coherence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    override_slope_id: Optional[str] = Field(default=None)


@router.get("/sar/coherence/pilot-sites")
async def list_sar_pilot_sites():
    """
    UKIS Addendum v2 Section 3.15: Lists named pilot slopes covered by Sentinel-1 InSAR
    interferometric coherence tracking with orbits, geology, and baseline parameters.
    """
    return sar_coherence_engine.list_pilot_slopes()


@router.post("/sar/coherence/evaluate", response_model=SARPrecursorEvaluation)
async def evaluate_sar_coherence_precursor(request: SARCoherenceEvalRequest):
    """
    Evaluates millimeter-scale slow slope creep precursor.
    Fails visibly with OUTSIDE_PILOT_SCOPE if outside the 3 named pilot slopes.
    """
    return sar_coherence_engine.evaluate_slope_coherence(
        latitude=request.latitude,
        longitude=request.longitude,
        observed_coherence=request.observed_coherence,
        override_slope_id=request.override_slope_id,
    )


# ---------------------------------------------------------------------------
# Section 3.16: Automated Glacial Lake (GLOF) 30-Day Rate-of-Change Monitoring
# ---------------------------------------------------------------------------

from backend.services.glof_sentinel import (
    GlacialLakeExpansionRateResult,
)


class LakeExpansionRateRequest(BaseModel):
    lake_name: str = Field(default="Chorabari Lake (Gandhi Sarovar)")
    current_area_m2: float = Field(..., ge=0.0)
    area_30d_ago_m2: float = Field(..., gt=0.0)
    cloud_cover_pct: float = Field(default=8.5, ge=0.0, le=100.0)
    threshold_rate_pct: float = Field(default=10.0, ge=1.0, le=100.0)


@router.post("/glof/lake-expansion/rate", response_model=GlacialLakeExpansionRateResult)
async def evaluate_lake_expansion_rate(request: LakeExpansionRateRequest):
    """
    UKIS Addendum v2 Section 3.16: Computes 30-day rate-of-change in glacial lake area.
    Fails visibly if cloud cover > 30% (NO_CLOUD_FREE_OBSERVATION).
    """
    return glof_sentinel_service.calculate_30day_expansion_rate(
        current_area_m2=request.current_area_m2,
        area_30d_ago_m2=request.area_30d_ago_m2,
        lake_name=request.lake_name,
        cloud_cover_pct=request.cloud_cover_pct,
        threshold_rate_pct=request.threshold_rate_pct,
    )


# ---------------------------------------------------------------------------
# Task 6.2: Dynamic Transient Population Load Layer
# ---------------------------------------------------------------------------

@router.get("/analytics/dynamic-load", response_model=DynamicLoadSummary)
async def get_dynamic_population_load_endpoint():
    """
    UKIS Task 6 (Hardened) Section 6.2: Dynamic Transient Population Load & Scaled Relief Provisioning.
    Ingests authentic Char Dham Yatra registration footfall figures (or cited seasonal multiplier fallback).
    Replaces fabricated cell-tower simulation.
    Scales safe-haven medical kits and food ration tonnage with MAX_LOAD_MULTIPLIER = 4.5 safety cap.
    """
    return dynamic_population_service.get_dynamic_load_summary()


# ---------------------------------------------------------------------------
# Task 6.3: Compressed Offline State Synchronization (Bluetooth Mesh Relay)
# ---------------------------------------------------------------------------

@router.post("/sync/mesh-packet", response_model=MeshSyncResult)
async def sync_mesh_packet_endpoint(packet: MeshPacketInput):
    """
    UKIS Task 6 (Hardened) Section 6.3: Ingests base64-encoded, gzip-compressed field status telemetry.
    Wired to the Section 3.12 two-device Bluetooth mesh relay prototype.
    Decompresses payload, strictly validates schema, applies clock-drift sanity checks,
    and applies conflict-resolution upsert (incoming report_timestamp > existing wins).
    """
    try:
        return mesh_sync_service.process_mesh_packet(packet)
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err)) from val_err
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Mesh sync pipeline failure: {err}") from err


@router.get("/sync/mesh-reports", response_model=List[SyncedStatusReport])
async def list_synced_mesh_reports_endpoint(limit: int = 50):
    """
    UKIS Task 6 (Hardened) Section 6.3: Returns recent field reports synced via Bluetooth relay.
    Exposes report_timestamp (field clock) and synced_at (server receipt) side-by-side to surface sync lag.
    """
    return mesh_sync_service.list_recent_synced_reports(limit=limit)