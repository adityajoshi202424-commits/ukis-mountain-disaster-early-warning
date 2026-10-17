# Data Source Registry

Every data value in this system must have provenance. This document records all data sources,
their access methods, licenses, limitations, and authentication requirements.

**RULE: If a source cannot provide a value, the system returns `DATA UNAVAILABLE`.
It NEVER fabricates replacement values.**

---

## Tier 1 — Free, No API Key Required

### NASA POWER

| Field | Value |
|---|---|
| **Provider** | NASA Langley Research Center POWER Project |
| **URL** | https://power.larc.nasa.gov/ |
| **Data** | Hourly precipitation, temperature, and relative humidity |
| **Access** | REST API — no key required |
| **Spatial Resolution** | NASA POWER model grid point |
| **Temporal Resolution** | Hourly |
| **Status** | ✅ IMPLEMENTED |

**Limitations:** Model/reanalysis estimates are not a replacement for IMD or AWS gauges.

### USGS Earthquake Hazards Program

| Field | Value |
|---|---|
| **Provider** | USGS Earthquake Hazards Program |
| **URL** | https://earthquake.usgs.gov/fdsnws/event/1/ |
| **Data** | Earthquake event magnitude, epicenter, and event time |
| **Access** | GeoJSON REST API — no key required |
| **Spatial Resolution** | Event epicenter |
| **Temporal Resolution** | Event-driven |
| **Status** | ✅ IMPLEMENTED |

**Important limitation:** USGS is the live fallback seismic feed. India's NCS feed remains the authoritative target but does not expose an equally simple public API.

### Open-Meteo

| Field | Value |
|---|---|
| **Provider** | Open-Meteo GmbH |
| **URL** | https://open-meteo.com/ |
| **Data** | Weather forecast (7-day), historical weather (1940–present) |
| **Variables** | Temperature, precipitation, humidity, wind, pressure, cloud cover, soil moisture |
| **Access** | REST API — no key required |
| **License** | CC-BY 4.0 (non-commercial free) |
| **Spatial Resolution** | ~0.25° (~25 km, ECMWF HRES model) |
| **Temporal Resolution** | Hourly |
| **Update Frequency** | Real-time (forecast), 5-day delay (final archive) |
| **Rate Limit** | Undocumented, but throttled under heavy load |
| **Latency** | Real-time |
| **Status** | ✅ IMPLEMENTED |

**Limitations:**
- Resolution is ~25km — cannot distinguish micro-basins
- Precipitation is model-interpolated, not gauge-observed
- Soil moisture from ERA5-Land reanalysis, not in-situ sensors

**Attribution:** Weather data from Open-Meteo. Models: ECMWF, DWD, NOAA, and others.

---

### OpenStreetMap (Overpass API)

| Field | Value |
|---|---|
| **Provider** | OpenStreetMap Community |
| **URL** | https://www.openstreetmap.org/ |
| **API** | Overpass API (https://overpass-api.de/) |
| **Data** | Roads, bridges, hospitals, schools, rivers, villages, emergency services |
| **Access** | REST API — no key required |
| **License** | ODbL (Open Database License) |
| **Spatial Resolution** | Vector (exact positions) |
| **Update Frequency** | Continuous (community edits) |
| **Rate Limit** | Throttled under load, no explicit quota |
| **Status** | ✅ IMPLEMENTED |

**Limitations:**
- Coverage depends on community contributions — may be incomplete in remote rural areas
- No official quality assurance — community-contributed
- Overpass queries on large bounding boxes may timeout

**Attribution:** © OpenStreetMap contributors. Data available under ODbL.

---

## Tier 2 — Free, API Key / Registration Required

### NASA GPM IMERG

| Field | Value |
|---|---|
| **Provider** | NASA Goddard Space Flight Center |
| **URL** | https://gpm.nasa.gov/ |
| **Data** | Satellite-derived precipitation |
| **Access** | Earthdata Login (free registration) |
| **License** | CC-BY 1.0 (free for all use) |
| **Spatial Resolution** | 0.1° (~10 km) |
| **Temporal Resolution** | Half-hourly |
| **Update Frequency** | Early Run (~4h), Late Run (~14h), Final (~3.5 months) |
| **Rate Limit** | Per-user (reasonable for research) |
| **Status** | 🔧 PLANNED (Phase 3) |
| **Required Configuration** | `NASA_EARTHDATA_USERNAME`, `NASA_EARTHDATA_PASSWORD` in .env |

**Registration:** https://urs.earthdata.nasa.gov/

---

### India Meteorological Department (IMD)

| Field | Value |
|---|---|
| **Provider** | IMD, Government of India |
| **URL** | https://api.imd.gov.in/ |
| **Data** | Official weather observations, district-wise rainfall, nowcasts |
| **Access** | API registration |
| **License** | Government of India terms |
| **Spatial Resolution** | Station-level / district-level |
| **Temporal Resolution** | Varies (hourly to daily) |
| **Status** | 🔧 PLANNED (Phase 3) |
| **Required Configuration** | `IMD_API_KEY` in .env |

---

### Central Water Commission (CWC) / NWDP

| Field | Value |
|---|---|
| **Provider** | CWC, Ministry of Jal Shakti, Government of India |
| **URL** | https://nwdp.nwic.gov.in/ |
| **Data** | River water levels and discharge for Uttarakhand's Himalayan river systems |
| **Access** | Portal registration, possible API |
| **License** | Government of India terms |
| **Spatial Resolution** | Station-level (flood forecasting stations) |
| **Temporal Resolution** | Sub-daily (telemetry) to daily (manual) |
| **Status** | 🔧 PLANNED (Phase 3) |
| **Required Configuration** | `CWC_API_KEY` in .env |

**Also available:** FloodWatch India app, ffs.india-water.gov.in

---

### OpenTopography / SRTM

| Field | Value |
|---|---|
| **Provider** | NASA / OpenTopography |
| **URL** | https://opentopography.org/ |
| **Data** | SRTM 30m Digital Elevation Model |
| **Access** | Free API key |
| **License** | Public domain (SRTM) |
| **Spatial Resolution** | 30 meters |
| **Status** | 🔧 PLANNED (Phase 3) |
| **Required Configuration** | `OPENTOPOGRAPHY_API_KEY` in .env |

---

### ESA WorldCover

| Field | Value |
|---|---|
| **Provider** | European Space Agency |
| **URL** | https://esa-worldcover.org/ |
| **Data** | Global land cover classification (2021) |
| **Access** | AWS S3 (free), Google Earth Engine |
| **License** | CC-BY 4.0 |
| **Spatial Resolution** | 10 meters |
| **Status** | 🔧 PLANNED (Phase 3) |

---

### ISRIC SoilGrids

| Field | Value |
|---|---|
| **Provider** | ISRIC — World Soil Information |
| **URL** | https://soilgrids.org/ |
| **Data** | Soil properties (clay, sand, silt, organic carbon, bulk density, pH) |
| **Access** | WCS/WebDAV (free), Google Earth Engine |
| **License** | CC-BY 4.0 / ODbL |
| **Spatial Resolution** | 250 meters |
| **Status** | 🔧 PLANNED (Phase 3) |

**Note:** REST API currently paused by ISRIC. Use WCS or WebDAV.

---

### WorldPop

| Field | Value |
|---|---|
| **Provider** | WorldPop, University of Southampton |
| **URL** | https://hub.worldpop.org/ |
| **Data** | Population density (gridded) |
| **Access** | Direct download (GeoTIFF) |
| **License** | CC-BY 4.0 |
| **Spatial Resolution** | 100 meters |
| **Status** | 🔧 PLANNED (Phase 5) |

---

### Copernicus EMS

| Field | Value |
|---|---|
| **Provider** | European Commission / Copernicus |
| **URL** | https://emergency.copernicus.eu/mapping/ |
| **Data** | Historical flood extent maps (satellite-derived) |
| **Access** | Portal download (free) |
| **License** | European Commission open reuse policy |
| **Status** | 🔧 PLANNED (Phase 6) |

---

### GloFAS (Global Flood Awareness System)

| Field | Value |
|---|---|
| **Provider** | Copernicus / ECMWF |
| **URL** | https://global-flood.emergency.copernicus.eu/ |
| **Data** | Global flood forecasts, river discharge |
| **Access** | Copernicus Climate Data Store (free registration) |
| **License** | Copernicus terms |
| **Spatial Resolution** | ~10 km |
| **Status** | 🔧 PLANNED (Phase 5) |

---

## Tier 3 — Institutional Access Required

### India-WRIS

| Field | Value |
|---|---|
| **Data** | Detailed hydrology, reservoir levels |
| **Access** | Portal, may need approval |
| **Status** | 📋 INVESTIGATION NEEDED |

### MOSDAC (ISRO)

| Field | Value |
|---|---|
| **Data** | INSAT satellite rainfall |
| **Access** | Registration required |
| **Status** | 📋 INVESTIGATION NEEDED |

---

## Source Discovery Protocol

Before implementing any new data source:

```
SOURCE DISCOVERY
↓
DOCUMENTATION REVIEW
↓
ACCESS METHOD (API / download / WCS / scraping NOT allowed)
↓
LICENSE (must be legally usable)
↓
UPDATE FREQUENCY
↓
SPATIAL RESOLUTION
↓
TEMPORAL RESOLUTION
↓
RATE LIMIT
↓
AUTHENTICATION
↓
IMPLEMENTATION
↓
VALIDATION (prove real data flows)
```

---

## Quality & Freshness Assessment Rules

The Data Quality Engine (`quality_engine.validate_batch`) validates all incoming telemetry batches against 5 operational criteria:

1. **Range Validation**: Water level $0\text{ m} \le H \le 120\text{ m}$, Rainfall $0\text{ mm/hr} \le P \le 300\text{ mm/hr}$.
2. **Temporal Freshness**: Observations older than $6\text{ hours}$ are marked `STALE`.
3. **Coordinate Validation**: WGS84 bounding box check for Uttarakhand ($77.5757^\circ\text{E} \le \text{Lon} \le 81.0475^\circ\text{E}$, $28.7161^\circ\text{N} \le \text{Lat} \le 31.4558^\circ\text{N}$).
4. **Consensus Cryptographic Hashing**: SHA-256 block creation per ingestion batch.
5. **Failover Protocol**: Gauge outages automatically trigger fallback to secondary satellite radar altimetry.
