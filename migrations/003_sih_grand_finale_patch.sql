-- ============================================================================
-- PostgreSQL + PostGIS Schema Extension Package (SIH PS #192 Compliant)
-- ============================================================================

-- 1. Upgraded Relief Shelter Schema with Vehicle Access Attributes
ALTER TABLE shelter_occupancy_tracker 
ADD COLUMN IF NOT EXISTS max_accessible_vehicle_weight NUMERIC(5,2) DEFAULT 40.00,
ADD COLUMN IF NOT EXISTS flood_clearance_threshold_meters NUMERIC(3,2) DEFAULT 0.30;

-- 2. Extended Citizen Ground-Truth Report with Cryptographic Payloads
ALTER TABLE citizen_ground_truth_reports 
ADD COLUMN IF NOT EXISTS citizen_public_key TEXT DEFAULT NULL,
ADD COLUMN IF NOT EXISTS cryptographic_signature TEXT DEFAULT NULL,
ADD COLUMN IF NOT EXISTS verification_consensus_score NUMERIC(3,2) DEFAULT 1.00;

-- 3. Injected Validation Ledger to Prevent Crowdsourced Spoofing Attacks
CREATE TABLE IF NOT EXISTS citizen_ledger_signatures (
    signature_id VARCHAR(64) PRIMARY KEY,
    report_id VARCHAR(64),
    validator_node_id VARCHAR(64) NOT NULL,
    computed_payload_hash VARCHAR(64) NOT NULL,
    signature_valid BOOLEAN DEFAULT TRUE,
    verified_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexing for high-performance spatial cross-joins and metric projections
CREATE INDEX IF NOT EXISTS idx_historical_events_spatial_centroid 
ON historical_events (center_lat, center_lon);
