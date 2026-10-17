-- UKIS Task 6 (Hardened): Dynamic Transient Population Load & Compressed Offline Mesh Sync
-- Extends existing base schema without parallel tables.

-- 1. Dynamic Transient Population Load columns for villages
ALTER TABLE villages ADD COLUMN IF NOT EXISTS current_estimated_load INTEGER;
ALTER TABLE villages ADD COLUMN IF NOT EXISTS load_data_source TEXT; -- 'yatra_registration_live' | 'yatra_season_multiplier_demo_mode'
ALTER TABLE villages ADD COLUMN IF NOT EXISTS load_last_updated TIMESTAMPTZ;

-- 2. Scaled emergency provisioning columns for safe havens
ALTER TABLE safe_havens ADD COLUMN IF NOT EXISTS current_estimated_load INTEGER;
ALTER TABLE safe_havens ADD COLUMN IF NOT EXISTS medical_kits_needed INTEGER;
ALTER TABLE safe_havens ADD COLUMN IF NOT EXISTS rations_tons NUMERIC(10, 2);
ALTER TABLE safe_havens ADD COLUMN IF NOT EXISTS load_data_source TEXT;
ALTER TABLE safe_havens ADD COLUMN IF NOT EXISTS load_last_updated TIMESTAMPTZ;

-- 3. Offline Bluetooth mesh status reports (Section 6.3)
CREATE TABLE IF NOT EXISTS citizen_status_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    village_id VARCHAR(64) NOT NULL,
    status_code VARCHAR(32) NOT NULL,
    status_code_category VARCHAR(64) NOT NULL,
    report_timestamp TIMESTAMPTZ NOT NULL,
    device_id VARCHAR(64) NOT NULL,
    synced_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    is_offline_origin BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT uq_village_status_cat UNIQUE (village_id, status_code_category)
);

CREATE INDEX IF NOT EXISTS idx_status_reports_village ON citizen_status_reports (village_id);
CREATE INDEX IF NOT EXISTS idx_status_reports_synced_at ON citizen_status_reports (synced_at);
