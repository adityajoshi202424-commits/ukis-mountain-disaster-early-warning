"""
Flash Flood Early Warning Platform — Database Models

Tables separated by concern:
- Raw observations (immutable)
- Normalized observations
- Provider status
- Data quality log
- Predictions
- Alerts
- Events
- Users & audit

Uses PostGIS for geospatial, TimescaleDB hypertables for time-series.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

try:
    from geoalchemy2 import Geometry
except ImportError:
    # Fallback for environments without geoalchemy2 binary extension installed
    def Geometry(*args, **kwargs):
        return Text

try:
    from sqlalchemy.dialects.postgresql import JSONB
except ImportError:
    from sqlalchemy import JSON as JSONB

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    UUID,
)
from sqlalchemy.orm import relationship

from backend.database import Base


# ---------------------------------------------------------------------------
# Enums (match the provider base enums)
# ---------------------------------------------------------------------------


class QualityStatusDB(str, enum.Enum):
    VALID = "VALID"
    SUSPECT = "SUSPECT"
    INVALID = "INVALID"
    MISSING = "MISSING"
    STALE = "STALE"


class ProviderStatusDB(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    API_KEY_REQUIRED = "API_KEY_REQUIRED"
    OFFLINE = "OFFLINE"
    RATE_LIMITED = "RATE_LIMITED"
    ERROR = "ERROR"
    STALE = "STALE"


class DataModeDB(str, enum.Enum):
    LIVE = "LIVE"
    HISTORICAL = "HISTORICAL"
    REPLAY = "REPLAY"
    SIMULATION = "SIMULATION"


class RiskLevel(str, enum.Enum):
    NORMAL = "NORMAL"
    WATCH = "WATCH"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class UserRole(str, enum.Enum):
    PUBLIC = "PUBLIC"
    ANALYST = "ANALYST"
    OPERATOR = "OPERATOR"
    ADMIN = "ADMIN"


# ---------------------------------------------------------------------------
# Uttarakhand geospatial action layer
# ---------------------------------------------------------------------------


class Village(Base):
    """Village/Gram Panchayat centroid used for exposure intersection checks."""

    __tablename__ = "villages"

    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(255), nullable=False)
    district = Column(String(128), nullable=False, index=True)
    geom = Column(Geometry("POINT", srid=4326), nullable=False)
    population = Column(Integer, nullable=True)
    is_isolated = Column(Boolean, nullable=False, default=False)
    isolation_last_checked = Column(DateTime(timezone=True), nullable=True)
    isolation_reason = Column(Text, nullable=True)
    current_estimated_load = Column(Integer, nullable=True)
    load_data_source = Column(String(128), nullable=True)
    load_last_updated = Column(DateTime(timezone=True), nullable=True)


class Lifeline(Base):
    """Critical road or infrastructure corridor geometry."""

    __tablename__ = "lifelines"

    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(255), nullable=False)
    type = Column(String(128), nullable=False)
    geom = Column(Geometry("LINESTRING", srid=4326), nullable=False)


class HazardZone(Base):
    """Computed hazard polygon with source timestamp and probabilistic score."""

    __tablename__ = "hazard_zones"

    id = Column(UUID(as_uuid=True), primary_key=True)
    hazard_type = Column(String(128), nullable=False, index=True)
    risk_score = Column(Float, nullable=False)
    geom = Column(Geometry("POLYGON", srid=4326), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )


class SafeHaven(Base):
    """Verified shelter, hospital, or helipad destination."""

    __tablename__ = "safe_havens"

    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(255), nullable=False)
    facility_type = Column(String(128), nullable=False)
    geom = Column(Geometry("POINT", srid=4326), nullable=False)
    capacity = Column(Integer, nullable=True)
    current_estimated_load = Column(Integer, nullable=True)
    medical_kits_needed = Column(Integer, nullable=True)
    rations_tons = Column(Float, nullable=True)
    load_data_source = Column(String(128), nullable=True)
    load_last_updated = Column(DateTime(timezone=True), nullable=True)


class CitizenStatusReport(Base):
    """Offline Bluetooth mesh status reports synchronized when connectivity restores."""

    __tablename__ = "citizen_status_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    village_id = Column(String(64), nullable=False, index=True)
    status_code = Column(String(32), nullable=False)
    status_code_category = Column(String(64), nullable=False)
    report_timestamp = Column(DateTime(timezone=True), nullable=False)
    device_id = Column(String(64), nullable=False)
    synced_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    is_offline_origin = Column(Boolean, nullable=False, default=True)

    __table_args__ = (
        UniqueConstraint("village_id", "status_code_category", name="uq_village_status_cat"),
    )


class CitizenPing(Base):
    """Unverified inbound SOS report linked to a known village geometry."""

    __tablename__ = "citizen_pings"

    id = Column(UUID(as_uuid=True), primary_key=True)
    village_name = Column(String(255), nullable=False, index=True)
    reported_hazard = Column(String(64), nullable=False)
    geom = Column(Geometry("POINT", srid=4326), nullable=False)
    verified = Column(Boolean, nullable=False, default=False)


class RoadEdge(Base):
    """Persisted OSM/Overpass edge state consumed by the route graph."""

    __tablename__ = "road_edges"

    edge_id = Column(UUID(as_uuid=True), primary_key=True)
    from_node = Column(String(128), nullable=False, index=True)
    to_node = Column(String(128), nullable=False, index=True)
    geom = Column(Geometry("LINESTRING", srid=4326), nullable=False)
    base_weight = Column(Float, nullable=False)
    current_weight = Column(Float, nullable=False)
    is_blocked = Column(Boolean, nullable=False, default=False)
    blocked_reason = Column(Text, nullable=True)
    blocked_since = Column(DateTime(timezone=True), nullable=True)


# ---------------------------------------------------------------------------
# Raw Observations — NEVER overwritten
# ---------------------------------------------------------------------------


class RawObservation(Base):
    """
    Immutable raw observation from an external provider.
    Never overwritten. Never modified after insertion.
    Full provenance stored as JSONB.
    """

    __tablename__ = "raw_observations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    variable = Column(String(64), nullable=False, index=True)
    value = Column(Float, nullable=True)  # None = DATA UNAVAILABLE
    unit = Column(String(16), nullable=True)

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location = Column(Geometry("POINT", srid=4326), nullable=True)

    observation_time = Column(DateTime(timezone=True), nullable=True, index=True)
    retrieved_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Full provenance as JSONB — searchable, queryable
    provenance = Column(JSONB, nullable=False)

    # Provider info
    provider_name = Column(String(64), nullable=False, index=True)
    dataset = Column(String(128), nullable=True)

    quality_status = Column(
        Enum(QualityStatusDB, name="quality_status_enum"),
        nullable=False,
        default=QualityStatusDB.VALID,
    )

    data_mode = Column(
        Enum(DataModeDB, name="data_mode_enum"),
        nullable=False,
        default=DataModeDB.LIVE,
    )

    __table_args__ = (
        Index("ix_raw_obs_time_var", "observation_time", "variable"),
        Index("ix_raw_obs_provider_time", "provider_name", "observation_time"),
    )


# ---------------------------------------------------------------------------
# Provider Health Log
# ---------------------------------------------------------------------------


class ProviderHealthLog(Base):
    """Tracks provider availability over time."""

    __tablename__ = "provider_health_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    provider_name = Column(String(64), nullable=False, index=True)
    status = Column(
        Enum(ProviderStatusDB, name="provider_status_enum"),
        nullable=False,
    )
    checked_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    latency_ms = Column(Float, nullable=True)
    battery_voltage_v = Column(Float, nullable=True, default=12.4)
    network_latency_ms = Column(Integer, nullable=True, default=120)
    error_message = Column(Text, nullable=True)
    observations_count = Column(Integer, nullable=True)


# ---------------------------------------------------------------------------
# Predictions
# ---------------------------------------------------------------------------


class Prediction(Base):
    """
    ML model prediction with full lineage.
    Every prediction records: model_version, inputs used, data quality, uncertainty.
    """

    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    prediction_id = Column(String(64), unique=True, nullable=False)

    timestamp = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location = Column(Geometry("POINT", srid=4326), nullable=True)

    # Prediction output
    probability = Column(Float, nullable=True)
    risk_level = Column(
        Enum(RiskLevel, name="risk_level_enum"),
        nullable=False,
        default=RiskLevel.NORMAL,
    )
    prediction_horizon_minutes = Column(Integer, nullable=False)

    # Model lineage
    model_name = Column(String(64), nullable=False)
    model_version = Column(String(32), nullable=False)
    training_dataset_version = Column(String(32), nullable=True)
    feature_version = Column(String(32), nullable=True)

    # Input quality
    input_quality = Column(JSONB, nullable=True)  # Which inputs were available/missing
    uncertainty = Column(Float, nullable=True)

    # Data lineage — which raw observations fed this prediction
    input_observation_ids = Column(JSONB, nullable=True)  # List of raw_observation IDs
    feature_values = Column(JSONB, nullable=True)  # Actual feature vector

    data_mode = Column(
        Enum(DataModeDB, name="data_mode_enum"),
        nullable=False,
        default=DataModeDB.LIVE,
    )

    validation_status = Column(
        String(64),
        nullable=False,
        default="EXPERIMENTAL — NOT VALIDATED FOR OPERATIONAL USE",
    )


# ---------------------------------------------------------------------------
# Alerts
# ---------------------------------------------------------------------------


class Alert(Base):
    """
    Alert record with full metadata.
    Implements: deduplication, cooldown, escalation, expiry.
    """

    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    alert_id = Column(String(64), unique=True, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    risk_level = Column(Enum(RiskLevel, name="risk_level_enum"), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location = Column(Geometry("POINT", srid=4326), nullable=True)
    region = Column(String(128), nullable=True)

    reason = Column(Text, nullable=False)
    prediction_horizon_minutes = Column(Integer, nullable=True)
    data_timestamp = Column(DateTime(timezone=True), nullable=True)
    model_version = Column(String(32), nullable=True)

    # Alert lifecycle
    expires_at = Column(DateTime(timezone=True), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    acknowledged_by = Column(String(128), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(32), nullable=False, default="ACTIVE")

    # Deduplication
    dedup_key = Column(String(256), nullable=True, index=True)

    # Link to prediction
    prediction_id = Column(String(64), nullable=True)


# ---------------------------------------------------------------------------
# Historical Flood Events
# ---------------------------------------------------------------------------


class FloodEvent(Base):
    """
    Real historical flood event.
    Only populated from verified sources (Copernicus EMS, ASDMA, CWC).
    NEVER fabricated.
    """

    __tablename__ = "flood_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(64), unique=True, nullable=False)

    region = Column(String(128), nullable=False, index=True)
    location_name = Column(String(256), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    extent = Column(Geometry("MULTIPOLYGON", srid=4326), nullable=True)

    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)

    source = Column(String(128), nullable=False)  # e.g., "Copernicus EMS EMSR-XXX"
    source_url = Column(Text, nullable=True)
    event_type = Column(String(64), nullable=True)  # flash_flood, riverine, pluvial
    confidence = Column(String(32), nullable=True)  # HIGH, MEDIUM, LOW

    data_availability = Column(JSONB, nullable=True)  # Which data sources exist for this event
    metadata_json = Column(JSONB, nullable=True)


# ---------------------------------------------------------------------------
# Users & Auth
# ---------------------------------------------------------------------------


class User(Base):
    """User accounts with role-based access control."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    email = Column(String(256), unique=True, nullable=False)
    hashed_password = Column(String(256), nullable=False)
    role = Column(
        Enum(UserRole, name="user_role_enum"),
        nullable=False,
        default=UserRole.PUBLIC,
    )
    is_active = Column(Boolean, default=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )


# ---------------------------------------------------------------------------
# Audit Log
# ---------------------------------------------------------------------------


class AuditLog(Base):
    """
    Audit trail for all sensitive operations.
    Never deleted. Never modified.
    """

    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
    user_id = Column(Integer, nullable=True)
    username = Column(String(64), nullable=True)
    action = Column(String(128), nullable=False)
    resource = Column(String(256), nullable=True)
    details = Column(JSONB, nullable=True)
    ip_address = Column(String(45), nullable=True)
    request_id = Column(String(64), nullable=True)


# ---------------------------------------------------------------------------
# Region Configuration
# ---------------------------------------------------------------------------


class RegionConfig(Base):
    """Database-driven region configuration. Not hard-coded."""

    __tablename__ = "region_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    region_id = Column(String(64), unique=True, nullable=False)
    name = Column(String(128), nullable=False)
    country = Column(String(64), nullable=False)

    boundary = Column(Geometry("MULTIPOLYGON", srid=4326), nullable=True)
    center_lat = Column(Float, nullable=False)
    center_lon = Column(Float, nullable=False)
    default_zoom = Column(Integer, default=8)

    # Available data sources for this region
    available_providers = Column(JSONB, nullable=True)
    # Risk thresholds for this region
    risk_thresholds = Column(JSONB, nullable=True)

    is_active = Column(Boolean, default=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )


# ---------------------------------------------------------------------------
# SIH Evaluation & Demonstration Mode Database Schema (PostgreSQL / PostGIS)
# ---------------------------------------------------------------------------


class HistoricalEventDB(Base):
    """Core Historical Events Catalog for chronological replay."""

    __tablename__ = "historical_events"

    event_id = Column(String(64), primary_key=True)
    state = Column(String(100), nullable=False)
    district = Column(String(100), nullable=False)
    event_name = Column(String(255), nullable=False)
    replay_start_time = Column(DateTime(timezone=True), nullable=False)
    replay_end_time = Column(DateTime(timezone=True), nullable=False)
    observed_impact_time = Column(DateTime(timezone=True), nullable=False)


class TelemetryFeatureDB(Base):
    """Time-Series Hydro-Met Features (Input Data with is_active flag for outage test)."""

    __tablename__ = "telemetry_features"

    feature_id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(64), ForeignKey("historical_events.event_id"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    station_id = Column(String(50), nullable=True)
    data_source = Column(String(100), nullable=False)
    rainfall_mm = Column(Float, nullable=True)
    river_level_meters = Column(Float, nullable=True)
    soil_moisture_percentage = Column(Float, nullable=True)
    battery_voltage_v = Column(Float, nullable=True, default=12.60)
    network_latency_ms = Column(Integer, nullable=True, default=45)
    is_active = Column(Boolean, default=True, nullable=False)


class GroundTruthFloodDB(Base):
    """Isolated Ground Truth Flood Layer (Strictly Sequestered from Inference Loop)."""

    __tablename__ = "ground_truth_flood"

    truth_id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(64), ForeignKey("historical_events.event_id"), nullable=False, index=True)
    observed_at = Column(DateTime(timezone=True), nullable=False)
    flood_extent_geometry = Column(Geometry("MULTIPOLYGON", srid=4326), nullable=True)
    peak_water_level = Column(Float, nullable=True)


class ShelterOccupancyTrackerDB(Base):
    """Active occupancy tracking metrics on civil assets & shelters data layer."""

    __tablename__ = "shelter_occupancy_tracker"

    shelter_id = Column(String(64), primary_key=True)
    shelter_name = Column(String(255), nullable=False)
    max_capacity_headcount = Column(Integer, nullable=False)
    current_occupancy_headcount = Column(Integer, default=0, nullable=False)
    max_accessible_vehicle_weight = Column(Float, nullable=True, default=40.0)
    flood_clearance_threshold_meters = Column(Float, nullable=True, default=0.30)
    last_updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )


class CitizenLedgerSignatureDB(Base):
    """Injected Validation Ledger to Prevent Crowdsourced Spoofing attacks."""

    __tablename__ = "citizen_ledger_signatures"

    signature_id = Column(String(64), primary_key=True)
    report_id = Column(String(64), nullable=True)
    validator_node_id = Column(String(64), nullable=False)
    computed_payload_hash = Column(String(64), nullable=False)
    signature_valid = Column(Boolean, default=True, nullable=False)
    verified_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

# Expose spatial module alias for 'backend.models.spatial'
import sys
try:
    from backend import spatial_models
    sys.modules["backend.models.spatial"] = spatial_models
except ImportError:
    pass
