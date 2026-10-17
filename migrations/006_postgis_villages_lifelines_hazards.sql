-- ============================================================================
-- PostGIS Database Schema Extension: Uttarakhand Mountain Disaster Platform
-- Problem Statement: UKIS 2026 P-011
-- Target Geography: Uttarakhand, India [77.57, 28.72, 81.04, 31.46]
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Villages Table (Centroid coordinates for Gram Panchayats / settlements)
CREATE TABLE IF NOT EXISTS villages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    district VARCHAR(128) NOT NULL,
    geom geometry(Point, 4326) NOT NULL,
    population INT DEFAULT NULL,
    is_isolated BOOLEAN NOT NULL DEFAULT FALSE,
    isolation_last_checked TIMESTAMPTZ DEFAULT NULL,
    isolation_reason TEXT DEFAULT NULL
);

CREATE INDEX IF NOT EXISTS idx_villages_geom ON villages USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_villages_district ON villages (district);
CREATE INDEX IF NOT EXISTS idx_villages_name ON villages (name);

-- 2. Lifelines Table (Critical transit corridors: NH-58, NH-94, NH-107, NH-34, Bridges)
CREATE TABLE IF NOT EXISTS lifelines (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(128) NOT NULL, -- 'National Highway', 'Bridge', 'Evacuation Route'
    geom geometry(LineString, 4326) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_lifelines_geom ON lifelines USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_lifelines_type ON lifelines (type);

-- 3. Hazard Zones Table (Active hazard polygons from ML / satellite segmentation)
CREATE TABLE IF NOT EXISTS hazard_zones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    hazard_type VARCHAR(128) NOT NULL, -- 'LANDSLIDE', 'GLOF', 'CLOUDBURST', 'FLASH_FLOOD'
    risk_score FLOAT NOT NULL CHECK (risk_score >= 0.0 AND risk_score <= 1.0),
    geom geometry(Polygon, 4326) NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_hazard_zones_geom ON hazard_zones USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_hazard_zones_type ON hazard_zones (hazard_type);
CREATE INDEX IF NOT EXISTS idx_hazard_zones_updated ON hazard_zones (updated_at);
