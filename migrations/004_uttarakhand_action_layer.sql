-- Uttarakhand action-layer spatial entities.
-- Source geometries must be loaded from verified Bhuvan/Survey of India/OSM data;
-- this migration intentionally contains no seed coordinates or synthetic rows.

CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS villages (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    district VARCHAR(128) NOT NULL,
    geom geometry(Point, 4326) NOT NULL,
    population INTEGER
);

CREATE INDEX IF NOT EXISTS idx_villages_geom ON villages USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_villages_district ON villages (district);

CREATE TABLE IF NOT EXISTS lifelines (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(128) NOT NULL,
    geom geometry(LineString, 4326) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_lifelines_geom ON lifelines USING GIST (geom);

CREATE TABLE IF NOT EXISTS hazard_zones (
    id UUID PRIMARY KEY,
    hazard_type VARCHAR(128) NOT NULL,
    risk_score DOUBLE PRECISION NOT NULL CHECK (risk_score >= 0 AND risk_score <= 1),
    geom geometry(Polygon, 4326) NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_hazard_zones_geom ON hazard_zones USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_hazard_zones_updated_at ON hazard_zones (updated_at);