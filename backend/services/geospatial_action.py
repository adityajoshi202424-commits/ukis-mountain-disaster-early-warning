"""
PostGIS Exposure Intersection, Downslope Vector Analysis, and Escalation Queries.

Complies with UKIS P-011 Core Constraints:
- Priority alerts trigger immediate escalations ONLY when a high-hazard zone intersects
  or sits topographically upslope of a populated settlement (village) or a critical lifeline asset.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.last_mile_resilience import escalate_operational_tier
from backend.services.landslide_ml_engine import dem_parser


def compute_downslope_vector(
    hazard_lat: float,
    hazard_lon: float,
    hazard_elev_m: float,
    village_lat: float,
    village_lon: float,
    village_elev_m: float,
) -> Dict[str, Any]:
    """
    Computes topographic gravity gradient and downslope flow vector
    from the hazard zone polygon centroid towards the settlement.
    """
    # Planar conversion in metric EPSG:3857 approximation
    dx_meters = (village_lon - hazard_lon) * 111320.0 * math.cos(math.radians(hazard_lat))
    dy_meters = (village_lat - hazard_lat) * 111320.0
    distance_meters = round(math.hypot(dx_meters, dy_meters), 2)

    # Elevation drop: positive when hazard is higher than village (topographically upslope)
    elevation_drop_m = round(hazard_elev_m - village_elev_m, 2)
    is_upslope = elevation_drop_m > 0.0

    # Downward hydraulic/debris gradient (rise / run)
    gradient = round(elevation_drop_m / max(1.0, distance_meters), 4) if distance_meters > 0 else 0.0

    # Azimuth heading from hazard toward village (0° North, 90° East, 180° South, 270° West)
    flow_azimuth_deg = round((math.degrees(math.atan2(dx_meters, dy_meters)) + 360.0) % 360.0, 1)

    # Escalation determination
    if is_upslope and distance_meters <= 2500.0:
        threat_level = "RED_ALERT"
        rationale = (
            f"Hazard centroid sits topographically upslope (+{elevation_drop_m}m drop) "
            f"within {distance_meters}m of village centroid on a {gradient} downslope gradient."
        )
    elif distance_meters <= 300.0:
        threat_level = "RED_ALERT"
        rationale = f"Hazard zone directly intersects settlement buffer zone ({distance_meters}m proximity)."
    else:
        threat_level = "WATCH"
        rationale = "Hazard is downslope or distant from settlement."

    return {
        "is_upslope": is_upslope,
        "elevation_drop_meters": elevation_drop_m,
        "distance_meters": distance_meters,
        "downslope_gradient": gradient,
        "flow_azimuth_degrees": flow_azimuth_deg,
        "threat_level": threat_level,
        "downslope_rationale": rationale,
    }


async def intersect_hazard_exposure(
    session: AsyncSession,
    hazard_zone_id: str,
    village_buffer_m: float = 500.0,
) -> List[Dict[str, Any]]:
    """
    Return exposed villages and lifelines for a hazard polygon.
    Calculates ST_DWithin for villages and ST_Intersects for lifelines.
    Computes downslope vector to escalate to RED_ALERT if the hazard sits upslope.
    """
    query = text(
        """
        SELECT hz.id AS hazard_id,
               hz.hazard_type,
               hz.risk_score,
               ST_X(ST_Centroid(hz.geom)) AS hazard_lon,
               ST_Y(ST_Centroid(hz.geom)) AS hazard_lat,
               v.id AS village_id,
               v.name AS village_name,
               v.district,
               v.population,
               ST_X(v.geom) AS village_lon,
               ST_Y(v.geom) AS village_lat,
               l.id AS lifeline_id,
               l.name AS lifeline_name,
               l.type AS lifeline_type
        FROM hazard_zones hz
        LEFT JOIN villages v ON ST_DWithin(
            ST_Transform(v.geom, 3857), ST_Transform(hz.geom, 3857), :village_buffer_m
        )
        LEFT JOIN lifelines l ON ST_Intersects(l.geom, hz.geom)
        WHERE hz.id = CAST(:hazard_zone_id AS uuid)
          AND (v.id IS NOT NULL OR l.id IS NOT NULL)
        """
    )
    result = await session.execute(
        query, {"hazard_zone_id": hazard_zone_id, "village_buffer_m": village_buffer_m}
    )
    rows = [dict(row) for row in result.mappings().all()]

    processed_exposures: List[Dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        v_id = item.get("village_id")
        l_id = item.get("lifeline_id")

        if v_id and item.get("hazard_lat") and item.get("village_lat"):
            # Sample terrain elevations using rasterio DEM parser
            try:
                h_terrain = dem_parser.parse_terrain(item["hazard_lat"], item["hazard_lon"])
                v_terrain = dem_parser.parse_terrain(item["village_lat"], item["village_lon"])
                h_elev = h_terrain.elevation_m
                v_elev = v_terrain.elevation_m
            except Exception:
                # Default elevation heuristics if DEM raster query falls outside bounds
                h_elev = 2400.0
                v_elev = 1900.0

            downslope_meta = compute_downslope_vector(
                hazard_lat=item["hazard_lat"],
                hazard_lon=item["hazard_lon"],
                hazard_elev_m=h_elev,
                village_lat=item["village_lat"],
                village_lon=item["village_lon"],
                village_elev_m=v_elev,
            )
            item.update(downslope_meta)
            item["escalation"] = downslope_meta["threat_level"]
        elif l_id:
            # Critical lifeline asset intersection
            item["is_upslope"] = False
            item["escalation"] = "RED_ALERT"
            item["downslope_rationale"] = (
                f"Hazard polygon directly intersects critical lifeline transit corridor: {item.get('lifeline_name')}."
            )
        else:
            item["escalation"] = "NO_ESCALATION"

        processed_exposures.append(item)

    return processed_exposures


async def operational_hazard_tier(
    session: AsyncSession,
    hazard_zone_id: str,
    base_tier: str,
    village_buffer_m: float = 500.0,
) -> Dict[str, Any]:
    """
    Escalates operational tier to RED_ALERT / CRITICAL when exposure or upslope vector exists.
    """
    exposures = await intersect_hazard_exposure(session, hazard_zone_id, village_buffer_m)
    has_red_alert = any(exp.get("escalation") == "RED_ALERT" for exp in exposures)
    effective_operational_tier = "CRITICAL" if has_red_alert else escalate_operational_tier(base_tier, bool(exposures))

    return {
        "hazard_zone_id": hazard_zone_id,
        "physical_risk_tier": base_tier.upper(),
        "operational_risk_tier": effective_operational_tier,
        "exposure_count": len(exposures),
        "has_red_alert": has_red_alert,
        "exposures": exposures,
    }


def evaluate_proximity_escalation(
    physical_risk_score: float,
    physical_tier: str,
    hazard_lat: float,
    hazard_lon: float,
    hazard_elev_m: float,
    settlements: Optional[List[Dict[str, Any]]] = None,
    buffer_meters: float = 2500.0,
) -> Dict[str, Any]:
    """
    UKIS Section 3.2b Rule 1: Village-Proximity Escalation.

    - Uninhabited terrain rule: A hazard flagged on terrain with no settlement downstream/downslope
      stays at its computed severity as an operational-monitoring item, NOT a public alert.
      (An uninhabited ridge slipping is a data point).
    - Settlement proximity rule: The same hazard flagged above or upstream of a village settlement
      escalates the alert tier to RED_ALERT (the underlying physical risk score is NOT inflated).
      (The same slip above a village is a Red Alert).
    """
    from backend.spatial_models import UTTARAKHAND_SETTLEMENTS

    targets = settlements or UTTARAKHAND_SETTLEMENTS
    downslope_exposed = []

    for settlement in targets:
        v_lat = settlement.get("latitude")
        v_lon = settlement.get("longitude")
        v_elev = settlement.get("elevation_m", 1800.0)

        vector = compute_downslope_vector(
            hazard_lat=hazard_lat,
            hazard_lon=hazard_lon,
            hazard_elev_m=hazard_elev_m,
            village_lat=v_lat,
            village_lon=v_lon,
            village_elev_m=v_elev,
        )

        # A village is downstream/downslope if it is topographically lower and within buffer,
        # or directly overlapping within immediate vicinity
        if (vector["is_upslope"] and vector["distance_meters"] <= buffer_meters) or vector["distance_meters"] <= 300.0:
            downslope_exposed.append({
                "village_name": settlement.get("name"),
                "district": settlement.get("district", "Chamoli"),
                "population": settlement.get("population", 0),
                "distance_meters": vector["distance_meters"],
                "elevation_drop_meters": vector["elevation_drop_meters"],
                "downslope_gradient": vector["downslope_gradient"],
                "flow_azimuth_deg": vector["flow_azimuth_degrees"],
            })

    # Case A: No populated settlement sits downstream/downslope
    if not downslope_exposed:
        return {
            "physical_risk_score": round(physical_risk_score, 4),
            "physical_tier": physical_tier.upper(),
            "operational_alert_tier": physical_tier.upper(),
            "is_public_alert": False,
            "alert_scope": "OPERATIONAL_MONITORING",
            "escalation_triggered": False,
            "downslope_settlements_count": 0,
            "downslope_settlements": [],
            "operational_summary": (
                f"Uninhabited terrain / ridge slip (physical tier {physical_tier.upper()}): "
                f"retained as operational-monitoring item. Public alert suppressed as no settlement "
                f"sits downstream/downslope."
            ),
        }

    # Case B: One or more populated settlements sit topographically downstream/downslope
    village_names = [s["village_name"] for s in downslope_exposed]
    return {
        "physical_risk_score": round(physical_risk_score, 4),
        "physical_tier": physical_tier.upper(),
        "operational_alert_tier": "RED_ALERT",
        "is_public_alert": True,
        "alert_scope": "PUBLIC_EMERGENCY",
        "escalation_triggered": True,
        "downslope_settlements_count": len(downslope_exposed),
        "downslope_settlements": downslope_exposed,
        "operational_summary": (
            f"VILLAGE-PROXIMITY ESCALATION: Hazard flagged above/upstream of {', '.join(village_names)}. "
            f"Physical risk score ({round(physical_risk_score, 4)}) preserved without inflation; "
            f"operational alert tier escalated to RED_ALERT."
        ),
    }