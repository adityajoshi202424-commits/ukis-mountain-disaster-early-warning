-- ============================================================================
-- Database Upgrade Script: Sensor Health Telemetry & Shelter Occupancy Tracker
-- ============================================================================

-- 1. Support expanded sensor health and edge telemetry decay variables
ALTER TABLE telemetry_features 
ADD COLUMN IF NOT EXISTS battery_voltage_v NUMERIC(4,2) DEFAULT 12.60,
ADD COLUMN IF NOT EXISTS network_latency_ms INTEGER DEFAULT 45;

-- 2. Append active occupancy tracking metrics onto civil assets or shelters configuration data layers
CREATE TABLE IF NOT EXISTS shelter_occupancy_tracker (
    shelter_id VARCHAR(64) PRIMARY KEY,
    shelter_name VARCHAR(255) NOT NULL,
    max_capacity_headcount INTEGER NOT NULL,
    current_occupancy_headcount INTEGER DEFAULT 0,
    last_updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- 3. Seed critical testing profile targets matching the Uttarakhand verification matrix
INSERT INTO shelter_occupancy_tracker (shelter_id, shelter_name, max_capacity_headcount, current_occupancy_headcount, last_updated_at)
VALUES 
    ('UK_SHELTER_01', 'Joshimath Cantonment High-Ground Shelter', 500, 482, NOW()),
    ('UK_SHELTER_02', 'Govt Inter College Joshimath Elevated Campus', 800, 140, NOW())
ON CONFLICT (shelter_id) DO UPDATE 
SET 
    max_capacity_headcount = EXCLUDED.max_capacity_headcount,
    current_occupancy_headcount = EXCLUDED.current_occupancy_headcount,
    last_updated_at = EXCLUDED.last_updated_at;
