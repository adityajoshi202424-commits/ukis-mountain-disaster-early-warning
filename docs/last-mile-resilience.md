# Last-Mile Resilience & Tactical Transit Network Loop
**UKIS Problem Statement P-011 | Task 6 (Hardened) Specification**

This document details the operational architecture of the transit graph network, topological lifeline isolation engine, dynamic transient population load layer, and compressed offline state synchronization.

---

## 6.1 Network Graph & Topological Isolation Engine (Unified Graph Service)

### Single Graph Architecture
In accordance with the "one continuous pipeline" principle, **there is exactly one graph service in the system**: `DynamicEvacuationRouter` (`backend/services/evacuation_routing.py`). It avoids parallel disconnected graphs that risk disagreeing during emergency operations.
- **Nodes**: Villages, gram panchayats, district headquarters, designated safe havens/shelters, hospitals, and helipads.
- **Edges**: Roads and mountain transit corridors (NH-58, NH-107, NH-34, NH-94, and rural link arteries) extracted from OpenStreetMap/Overpass Uttarakhand layers.
- **Traversal Weights**: Dynamic weights computed using the hydraulic friction and vehicle clearance formula (`backend/spatial_models.py`).

### Corrected Reachability Algorithm
Rather than testing whole-graph connectivity via `networkx.is_connected()`, reachability is evaluated outward from the set of active emergency hubs (district headquarters, hospitals, designated high-ground shelters):
$$\text{reachable\_nodes} = \bigcup_{h \in \text{hubs}} \text{multi\_source\_dijkstra\_path\_length}(G, \text{sources}=\{h\})$$
A village node is isolated if and only if it has no passable path to *any* designated emergency hub.

### Fail-Visibly 3-State Logic
To prevent silent assumption errors where road extraction gaps cause unmapped settlements to default to "connected":
1. **`connected`**: Passable ground route exists from the village to at least one designated hub. Rendered in green/blue.
2. **`isolated`**: Village is mapped in the network graph, but all connecting edges/bridges are blocked by hazards. Triggers aerial relief. Rendered in hard red/black.
3. **`unmapped`**: Settlement has no road network edges mapped in the OpenStreetMap/Overpass dataset. Rendered as a hatched/grey warning marker. Never silently collapsed into `connected`.

### Critical Alert Payload Requirement
When a village is flagged with `is_isolated = TRUE`, SMS, WhatsApp, and CAP alert dispatches strictly suppress stale ground routing and state:
> `"CRITICAL ALERT: Village Joshimath Sector B is ISOLATED — no ground route exists. Move to high ground immediately. Airborne rescue & pre-positioned relief alerted."`

---

## 6.2 Dynamic Transient Population Load Layer (Char Dham Yatra Proxy)

### Authentic Data Source (No Simulated Cell-Tower CDRs)
Cellular carrier CDR tracking data is proprietary and unavailable without telecom partnerships. To comply with the "no fake data in production paths" rule, dynamic transient loads are sourced from the **official Uttarakhand Char Dham Yatra Registration Portal and Tourism Footfall Registers**:
- **Source Citation**: Uttarakhand Tourism Development Board (UTDB) & Badrinath-Kedarnath Temple Committee (BKTC).
- **Update Cadence**: Daily portal aggregation (6 to 24-hour publish latency).
- **Demo-Mode Fallback**: When live portal feeds are offline, `--demo-mode` utilizes historical published seasonal multipliers (e.g., 2.8x to 3.8x baseline along NH-58 and NH-107 during May–November yatra months), explicitly tagged as `load_data_source = 'yatra_season_multiplier_demo_mode'`.

### Safety Capped Resource Scaler
Dynamic load augments, but never reduces, baseline emergency provisioning:
```python
MAX_LOAD_MULTIPLIER: float = 4.5

def compute_resource_requirement(base_requirement: float, static_population: int, current_estimated_load: int) -> float:
    if static_population <= 0:
        raise ValueError("static_population must be a real, non-zero census figure")
    load_ratio = max(1.0, current_estimated_load / static_population)
    load_ratio = min(load_ratio, MAX_LOAD_MULTIPLIER)
    return round(base_requirement * load_ratio, 2)
```
- **Medical Kits Needed**: Baseline 1 kit per 50 people, scaled up to 4.5x during peak pilgrimage surges.
- **Rations Needed**: Baseline 0.002 tons (2 kg) per person for a 3-day emergency buffer, scaled up to 4.5x.

---

## 6.3 Compressed Offline State Synchronization (Bluetooth Mesh Relay)

### Two-Way Pipeline Architecture
Connected to the Tier 3 Section 3.12 Bluetooth relay prototype. While Section 3.12 pushes outbound alerts from device to device, Section 6.3 provides the return path for field-collected citizen status reports once a courier device regains internet connectivity.

### Endpoint Contract
- **Endpoint**: `POST /api/v1/sync/mesh-packet`
- **Content-Type**: `application/json`
```json
{
  "device_id": "SDRF-RELAY-04",
  "payload": "H4sIC... (base64-encoded, gzip-compressed JSON array)",
  "packet_timestamp": "2026-09-14T14:30:00Z"
}
```

### Decompression & Validation Pipeline
1. Base64 decode with strict validation.
2. Gzip decompression of payload bytes.
3. JSON array deserialization into `CitizenStatusRecord` models. Missing required fields (`village_id`, `status_code`, `timestamp`) are rejected and logged; partial rows are never written.

### Conflict Resolution & Clock Drift Caveat
- **Conflict Resolution**: `WHERE EXCLUDED.report_timestamp > citizen_status_reports.report_timestamp`. When multiple packets arrive for the same village status category, the report with the newest field creation timestamp wins.
- **Clock Drift Sanity Check**: Devices offline without NTP network time sync may suffer RTC clock drift. The ingestion pipeline sanity-checks incoming packet timestamps against server time: packets timestamped > 2.0 hours in the future are flagged as `CLOCK_DRIFT_SUSPECT`.
- **Visible Sync Lag**: Synced reports expose both `report_timestamp` (when field personnel logged it) and `synced_at` (when it reached central servers) side-by-side on the dashboard.

---

## 5. The Last-Mile Resilience Loop (Task 5 Specification & Judge Pitch)

### The Grand Pitch Narrative: Space to Logic to Human
> *"How the AI analyzes data from space (Sentinel-1 InSAR & Sentinel-2 optical), translates it into logic on Earth (SHAP explanations), and directly drives a human to safety via basic SMS text messages—even if the internet completely fails."*

```
┌─────────────────────────┐
│     SPACE (Tier 1)      │ Sentinel-1 SAR Coherence + Sentinel-2 NDWI Lake Expansion
└───────────┬─────────────┘
            ▼
┌─────────────────────────┐
│     EARTH (Tier 2)      │ Geotechnical ML + TreeExplainer SHAP Localization
└───────────┬─────────────┘
            ▼
┌─────────────────────────┐
│    ACTION (Tier 3)      │ PostGIS ST_Distance & ST_Azimuth Safe Haven Pathfinder
└───────────┬─────────────┘
            ▼
┌─────────────────────────┐
│    HUMAN (Last-Mile)    │ Basic GSM SMS Evacuation Guidance ("Vector: NE to Haven")
└─────────────────────────┘
```

### 5.1 Safe Zone Schema & Querying with Hazard Exclusion
- **PostGIS Table**: `safe_havens` (`id` UUID, `name` VARCHAR, `facility_type` VARCHAR, `geom` geometry(Point, 4326), `capacity` INT).
- **PostGIS Nearest Safe Haven Query**:
```sql
SELECT v.id AS village_id, v.name AS village_name,
       sh.id AS safe_haven_id, sh.name AS safe_haven_name,
       sh.facility_type,
       ST_Distance(v.geom::geography, sh.geom::geography) AS distance_m,
       degrees(ST_Azimuth(v.geom, sh.geom)) AS azimuth_deg
FROM villages v
CROSS JOIN safe_havens sh
WHERE v.id = :village_id
  AND NOT EXISTS (
      SELECT 1 FROM hazard_zones hz
      WHERE ST_Intersects(hz.geom, ST_MakeLine(v.geom, sh.geom))
  )
ORDER BY ST_Distance(v.geom::geography, sh.geom::geography)
LIMIT 1;
```
- **Exclusion Mechanism**: If the straight-line vector between the village and the candidate safe haven intersects a calculated `hazard_zones` polygon (`ST_Intersects`), that shelter is automatically dropped, and the next closest valid safe haven is retrieved.

### 5.2 SMS Gateway Dispatcher Engine & Strict DLT Format
- **DLT Approved Template Pattern**: Matches Indian Telecom DLT registration standards (`sender_id = 'UKSDMA'`, template ID `1107161829304859`).
- **Exact Message Variable Pattern**:
```
EMERGENCY ALERT: Landslide risk detected near {village_name}. EVACUATE IMMEDIATELY to the nearest safe shelter at {safe_haven_name}. Path vector direction: {compass_direction}. Stay away from riverbanks.
```

### 5.3 Citizen SOS Inbound Webhook (`/api/v1/telecom/sms-webhook`)
- **Strict Regex Parsing**:
```python
SOS_PATTERN = re.compile(r"^SOS (?P<village>[\w\s]+) (?P<hazard>landslide|flood|cloudburst)$", re.IGNORECASE)
```
- **Database Insertion**: Ingests into `citizen_pings` table (`id` UUID, `village_name` VARCHAR, `reported_hazard` VARCHAR, `geom` geometry(Point, 4326), `verified` BOOLEAN DEFAULT FALSE) matched against verified village centroids.
- **Acoustic Siren Alarm**: Returns `sound_trigger = True`, which triggers the Web Audio dual-tone civil defence siren on the frontend operator dashboard.
