"""
SIH Demonstration & Evaluation Engine - Data Models & Storage

Isolated data structures for:
1. Historical Events Catalog
2. Time-Series Hydro-Met Telemetry Features
3. Ground Truth Flood Inundation Geometries (Strictly sequestered from inference)
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Pydantic Schemas for API & Validation
# ---------------------------------------------------------------------------

class HistoricalEventCatalog(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    state: str
    district: str
    event_name: str
    simulation_start: datetime
    simulation_end: datetime
    actual_breach_time: datetime
    description: str
    center_lat: float
    center_lon: float
    default_zoom: int = 11


class TelemetryPoint(BaseModel):
    timestamp: datetime
    station_id: str
    station_name: str
    lat: float
    lon: float
    source_id: str
    source_type: str  # 'precipitation' | 'hydrology' | 'soil_moisture' | 'radar_altimetry'
    measured_value: float
    unit: str  # 'mm' | 'meters' | 'percentage' | 'm/s'
    is_active: bool = True
    provenance_source: str


class GroundTruthPolygon(BaseModel):
    truth_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_id: str
    observed_at: datetime
    peak_water_level_observed: float
    affected_area_sqkm: float
    breach_point: Dict[str, Any]
    geojson_multipolygon: Dict[str, Any]  # GeoJSON feature collection / polygon


class TelemetryFeatureRow(BaseModel):
    feature_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_id: str
    timestamp: datetime
    rainfall_mm: float
    rainfall_intensity_mm_hr: float
    river_level_meters: Optional[float]
    river_surge_m_hr: Optional[float]
    soil_moisture_percentage: float
    soil_saturation_index: float  # 0.0 - 1.0
    radar_altimetry_meters: Optional[float] = None
    battery_voltage_v: Optional[float] = 12.4
    network_latency_ms: Optional[int] = 120
    station_data: Dict[str, Any] = Field(default_factory=dict)
    is_cwc_active: bool = True

