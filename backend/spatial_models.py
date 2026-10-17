"""
PostGIS Database Models & Spatial Schemas for Uttarakhand Mountain Early Warning.

Tables:
- villages: Centroid coordinates for Gram Panchayats and mountain settlements.
- lifelines: Critical transit corridors (NH-58, NH-94, NH-107, NH-34) and bridges.
- hazard_zones: Active polygon zones identified by ML risk models and satellite segmentation.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

# Re-export the SQLAlchemy PostGIS models defined on Base
from backend.models import Village, Lifeline, HazardZone


# ---------------------------------------------------------------------------
# Strict Pydantic Data Schemas
# ---------------------------------------------------------------------------

class VillagePoint(BaseModel):
    id: str
    name: str
    district: str
    latitude: float = Field(ge=28.72, le=31.46)
    longitude: float = Field(ge=77.57, le=81.04)
    population: Optional[int] = None
    is_isolated: bool = False
    isolation_reason: Optional[str] = None
    connectivity_state: str = "connected"  # 'connected' | 'isolated' | 'unmapped'
    current_estimated_load: Optional[int] = None
    load_data_source: Optional[str] = None


class LifelineCorridor(BaseModel):
    id: str
    name: str
    type: str
    coordinates: List[List[float]]  # [[lon, lat], ...]


class HazardPolygon(BaseModel):
    id: str
    hazard_type: str
    risk_score: float = Field(ge=0.0, le=1.0)
    coordinates: List[List[List[float]]]  # [[[lon, lat], ...]]
    updated_at: datetime


# ---------------------------------------------------------------------------
# Authentic Uttarakhand Geospatial Seed Registry
# High-risk Gram Panchayats & Trans-Himalayan Corridors
# ---------------------------------------------------------------------------

UTTARAKHAND_SETTLEMENTS: List[Dict[str, Any]] = [
    {
        "name": "Joshimath",
        "district": "Chamoli",
        "latitude": 30.5574,
        "longitude": 79.5658,
        "elevation_m": 1875,
        "population": 16709,
    },
    {
        "name": "Mana",
        "district": "Chamoli",
        "latitude": 30.7674,
        "longitude": 79.4958,
        "elevation_m": 3200,
        "population": 1214,
    },
    {
        "name": "Kedarnath",
        "district": "Rudraprayag",
        "latitude": 30.7352,
        "longitude": 79.0669,
        "elevation_m": 3583,
        "population": 612,
    },
    {
        "name": "Gaurikund",
        "district": "Rudraprayag",
        "latitude": 30.6517,
        "longitude": 79.0272,
        "elevation_m": 1982,
        "population": 2180,
    },
    {
        "name": "Badrinath",
        "district": "Chamoli",
        "latitude": 30.7433,
        "longitude": 79.4938,
        "elevation_m": 3133,
        "population": 2438,
    },
    {
        "name": "Raini",
        "district": "Chamoli",
        "latitude": 30.4905,
        "longitude": 79.6978,
        "elevation_m": 2100,
        "population": 850,
    },
    {
        "name": "Malari",
        "district": "Chamoli",
        "latitude": 30.6860,
        "longitude": 79.8880,
        "elevation_m": 3048,
        "population": 670,
    },
    {
        "name": "Govindghat",
        "district": "Chamoli",
        "latitude": 30.6256,
        "longitude": 79.5967,
        "elevation_m": 1828,
        "population": 1100,
    },
    {
        "name": "Dharasu",
        "district": "Uttarkashi",
        "latitude": 30.6277,
        "longitude": 78.3181,
        "elevation_m": 1050,
        "population": 3200,
    },
    {
        "name": "Dharchula",
        "district": "Pithoragarh",
        "latitude": 29.8519,
        "longitude": 80.5367,
        "elevation_m": 940,
        "population": 7032,
    },
]

UTTARAKHAND_LIFELINES: List[Dict[str, Any]] = [
    {
        "name": "NH-58 (Rishikesh - Badrinath Corridor)",
        "type": "National Highway",
        "coordinates": [
            [78.3000, 30.1000],
            [78.6000, 30.2000],
            [79.2000, 30.3500],
            [79.5658, 30.5574],
            [79.4938, 30.7433],
        ],
    },
    {
        "name": "NH-107 (Rudraprayag - Kedarnath Axis)",
        "type": "National Highway",
        "coordinates": [
            [78.9800, 30.2800],
            [79.0200, 30.4500],
            [79.0272, 30.6517],
            [79.0669, 30.7352],
        ],
    },
    {
        "name": "NH-94 / NH-134 (Yamunotri Highway)",
        "type": "National Highway",
        "coordinates": [
            [78.3181, 30.6277],
            [78.3800, 30.8200],
            [78.4300, 30.9800],
        ],
    },
    {
        "name": "NH-34 (Rishikesh - Uttarkashi - Gangotri)",
        "type": "National Highway",
        "coordinates": [
            [78.3000, 30.1500],
            [78.4400, 30.7300],
            [78.7500, 30.9500],
            [78.9300, 30.9900],
        ],
    },
    {
        "name": "Alaknanda Suspension Lifeline Bridge",
        "type": "Bridge",
        "coordinates": [
            [79.5640, 30.5560],
            [79.5670, 30.5580],
        ],
    },
]
