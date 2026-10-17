-- Last-mile resilience layer. Rows must be loaded from verified OSM/Bhuvan/
-- Census/authority sources; this migration inserts no coordinates or contacts.

CREATE TABLE IF NOT EXISTS safe_havens (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    facility_type VARCHAR(128) NOT NULL,
    geom geometry(Point, 4326) NOT NULL,
    capacity INTEGER
);
CREATE INDEX IF NOT EXISTS idx_safe_havens_geom ON safe_havens USING GIST (geom);

ALTER TABLE villages ADD COLUMN IF NOT EXISTS is_isolated BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE villages ADD COLUMN IF NOT EXISTS isolation_last_checked TIMESTAMPTZ;
ALTER TABLE villages ADD COLUMN IF NOT EXISTS isolation_reason TEXT;

CREATE TABLE IF NOT EXISTS road_edges (
    edge_id UUID PRIMARY KEY,
    from_node VARCHAR(128) NOT NULL,
    to_node VARCHAR(128) NOT NULL,
    geom geometry(LineString, 4326) NOT NULL,
    base_weight DOUBLE PRECISION NOT NULL,
    current_weight DOUBLE PRECISION NOT NULL,
    is_blocked BOOLEAN NOT NULL DEFAULT FALSE,
    blocked_reason TEXT,
    blocked_since TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_road_edges_geom ON road_edges USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_road_edges_nodes ON road_edges (from_node, to_node);

CREATE TABLE IF NOT EXISTS citizen_pings (
    id UUID PRIMARY KEY,
    village_name VARCHAR(255) NOT NULL,
    reported_hazard VARCHAR(64) NOT NULL CHECK (reported_hazard IN ('landslide', 'flood', 'cloudburst')),
    geom geometry(Point, 4326) NOT NULL,
    verified BOOLEAN NOT NULL DEFAULT FALSE
);
CREATE INDEX IF NOT EXISTS idx_citizen_pings_geom ON citizen_pings USING GIST (geom);