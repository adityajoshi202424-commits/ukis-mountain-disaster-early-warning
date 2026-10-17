-- ============================================================================
-- SIH Evaluation & Demonstration Schema (PostgreSQL + PostGIS)
-- Zero Temporal Leakage & Isolated Ground Truth Layer
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS postgis;

-- 1. Core Historical Events Catalog
CREATE TABLE IF NOT EXISTS historical_events (
    event_id UUID PRIMARY KEY,
    state VARCHAR(100) NOT NULL,
    district VARCHAR(100) NOT NULL,
    event_name VARCHAR(255) NOT NULL,
    replay_start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    replay_end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    observed_impact_time TIMESTAMP WITH TIME ZONE NOT NULL
);

-- 2. Time-Series Hydro-Met Features (Input Data)
CREATE TABLE IF NOT EXISTS telemetry_features (
    feature_id BIGSERIAL PRIMARY KEY,
    event_id UUID REFERENCES historical_events(event_id),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    station_id VARCHAR(50),
    data_source VARCHAR(100) NOT NULL, -- e.g., 'IMD_Rainfall', 'CWC_River_Level'
    rainfall_mm NUMERIC(6,2),
    river_level_meters NUMERIC(6,2),
    soil_moisture_percentage NUMERIC(5,2),
    is_active BOOLEAN DEFAULT TRUE -- For controlled failure demo
);

CREATE INDEX IF NOT EXISTS ix_telemetry_event_time ON telemetry_features(event_id, timestamp);

-- 3. Isolated Ground Truth Table (Strictly Sequestered)
CREATE TABLE IF NOT EXISTS ground_truth_flood (
    truth_id BIGSERIAL PRIMARY KEY,
    event_id UUID REFERENCES historical_events(event_id),
    observed_at TIMESTAMP WITH TIME ZONE NOT NULL,
    flood_extent_geometry GEOMETRY(MultiPolygon, 4326), -- PostGIS layer
    peak_water_level NUMERIC(6,2)
);

CREATE INDEX IF NOT EXISTS ix_ground_truth_event ON ground_truth_flood(event_id);
