# UKIS 2026 (P-011): AI Mountain Disaster Early-Warning Intelligence

**Theme:** Building Disaster Resilience Through Geospatial Analysis  
**Authority:** Uttarakhand State Disaster Management Authority (USDMA) • ITDA Uttarakhand • SDRF  
**Operational Region:** Uttarakhand (Devbhoomi), India — All 13 Himalayan Districts  
**Problem Statement Reference:** [UKIS P-011](https://www.axocom.in/UKISHackathon/problems/P-011)  
**Permanent 24/7 Live Deployment:** [https://frontend-rosy-phi-23.vercel.app](https://frontend-rosy-phi-23.vercel.app) *(Runs globally on Vercel Edge 24/7/365 — accessible anytime from any device worldwide, even when local development machines are powered off)*

---

## 🌐 Permanent Live Interactive Links (24/7/365 Cloud Hosted)

| Platform Feature | Direct Permanent URL | Live Interactive Capability |
| :--- | :--- | :--- |
| **Citizen Active Alerts** | [https://frontend-rosy-phi-23.vercel.app](https://frontend-rosy-phi-23.vercel.app) | Official CAP v1.2 emergency warnings (Chamoli, Rudraprayag, Uttarkashi) |
| **Interactive AI Commander Bot** | [https://frontend-rosy-phi-23.vercel.app](https://frontend-rosy-phi-23.vercel.app) | Floating bot on bottom-right. Answers evacuation queries, hazard reasons & SOPs |
| **ISRO Bhuvan GIS Map** | [https://frontend-rosy-phi-23.vercel.app/emergency](https://frontend-rosy-phi-23.vercel.app/emergency) | Interactive 14-hazard spatial grid, satellite/terrain layers & telemetry badges |
| **Admin Room & SMS Dispatcher** | [https://frontend-rosy-phi-23.vercel.app/admin](https://frontend-rosy-phi-23.vercel.app/admin) | Tab 7: Test live multilingual SMS push & dispatch automated authority voice calls |
| **Evacuation Shelters Directory** | [https://frontend-rosy-phi-23.vercel.app/shelters](https://frontend-rosy-phi-23.vercel.app/shelters) | High-ground shelter capacities, GPS coordinates & emergency supply tracking |
| **Citizen Guidebook** | [https://frontend-rosy-phi-23.vercel.app/guidebook](https://frontend-rosy-phi-23.vercel.app/guidebook) | Offline survival protocols, flash flood evacuation rules & hotlines (112 / 1070) |
| **Live CAP Feed API** | [https://frontend-rosy-phi-23.vercel.app/api/v1/alerts/feed](https://frontend-rosy-phi-23.vercel.app/api/v1/alerts/feed) | Real-time JSON CAP v1.2 alert feed served from edge serverless runtime |
| **Live Multi-Hazard Engine** | [https://frontend-rosy-phi-23.vercel.app/api/v1/mountain/hazard/composite](https://frontend-rosy-phi-23.vercel.app/api/v1/mountain/hazard/composite) | Dynamic hazard scoring connected live to Open-Meteo & USGS Seismicity |

---

## Zero Data Fabrication Guarantee

> [!IMPORTANT]
> **Strict Empirical Integrity:** Every environmental observation, digital elevation model (DEM) metric, river discharge forecast, and seismic telemetry reading served by this platform is dynamically retrieved from verified public scientific APIs:
> - **Open-Meteo Weather API**: Hourly and 48h rainfall, snowpack depth, freezing level isotherm ($Z_{0^\circ\text{C}}$), soil moisture, temperature.
> - **Open-Meteo Elevation API**: Real SRTM and Copernicus 90m/30m DEM for accurate slope gradient analysis.
> - **Copernicus GloFAS v4 (Open-Meteo Flood API)**: Real river discharge ($m^3/s$) for Himalayan river networks.
> - **USGS Real-Time Earthquake Feed**: Real-time seismic events ($M \ge 2.0$) within the Uttarakhand Himalayan arc ($28.5^\circ\text{N} - 31.5^\circ\text{N}, 77.5^\circ\text{E} - 81.5^\circ\text{E}$).
> Missing data is reported as `DATA UNAVAILABLE`. No synthetic numbers are fabricated.

---

## 5 Core Capabilities (UKIS P-011 Specification)

1. **Monitor Glaciers & Analyse Snow-Cover Change (GLOF Radar)**
   - Continuous tracking of high-altitude proglacial lakes: Chorabari (Kedarnath), Rishiganga hanging wedge, Gangotri terminus (Gaumukh), Milam, and Pindari.
   - Live freezing-level isotherm height ($Z_{0^\circ\text{C}}$) vs moraine elevation.
   - Positive degree-day (PDD) ablation melting rate ($mm/day$).
   - Froehlich dam-break peak breach discharge ($Q_{peak} = 0.607 \cdot V^{0.295} \cdot H^{1.24}$) and wave travel time to downstream settlements.

2. **Assess Flash-Flood & Landslide Risk**
   - Dynamic Landslide Susceptibility Index (LSI) combining live 48h antecedent precipitation, slope angle, and soil moisture saturation ($S_m$).
   - Central Himalayan calibrated Caine rainfall threshold exceedance ($I = 14.82 \cdot D^{-0.39}$).
   - Char Dham Yatra highway transit corridors passability monitoring (NH-58, NH-107, NH-108, NH-94, NH-125).

3. **Monitor Fragile Mountain Slopes for Meaningful Change**
   - Infinite slope Factor of Safety ($F_s$) calculation based on real DEM slope angle ($38.5^\circ - 52^\circ$), shear strength, and pore-water pressure ratio $r_u$.
   - Active chronic subsidence tracking: Joshimath urban moraine creep (54 mm/yr), Bhatwari active slide, Balia Nala Nainital fault scarp.
   - Proximity buffers to regional tectonic thrust faults: Main Central Thrust (MCT) and Main Boundary Thrust (MBT).

4. **Combine Weather, Terrain, Hydrology & Remote-Sensing Layers**
   - Statutory IMD cloudburst detection ($\ge 100\text{ mm/hr}$ or localized extreme micro-burst $\ge 40\text{ mm/hr}$).
   - 7-day GloFAS river discharge forecast hydrograph for Alaknanda, Bhagirathi, Mandakini, Dhauliganga, and Kali basins.
   - Real-time seismic peak ground acceleration (PGA) triggering slope failures.

5. **Issue Explainable, Severity-Based Warnings for High-Risk Locations (XAI)**
   - Multi-Hazard Composite Risk Index ($0 - 100$) and NDMA/USDMA severity tiers: GREEN, YELLOW, ORANGE, RED.
   - SHAP-style feature attribution breakdown showing percentage contribution of Precipitation, Slope, Glacier/GLOF, Soil Moisture, and Seismicity.
   - Bilingual (English & Hindi) official emergency bulletins with Common Alerting Protocol (CAP v1.2) XML broadcast for USDMA and SDRF teams.

---

## 13 Districts of Uttarakhand Covered

- **Chamoli**: Joshimath Subsidence, Tapovan/Rishiganga GLOF, Badrinath (NH-58)
- **Rudraprayag**: Kedarnath, Chorabari Lake, Gaurikund, Mandakini Valley (NH-107)
- **Uttarkashi**: Gangotri Glacier, Gaumukh, Bhatwari Chronic Slide (NH-108)
- **Pithoragarh**: Milam Glacier, Dharchula, Malpa Landslide Zone (NH-125)
- **Bageshwar**: Pindari Glacier, Sunderdhunga Outflow Grid
- **Tehri Garhwal**: Tehri Dam Reservoir Rim Slope Stability Hub
- **Nainital**: Naini Lake Basin, Balia Nala Fragile Ridge, Krol Thrust (NH-109)
- **Dehradun**: Mussoorie Steep Scarp, Rispana Torrent Flood Grid
- **Pauri Garhwal**: Srinagar Garhwal Alaknanda Hydrometric Base
- **Almora**: Almora Tectonic Ridge & Kosi Catchment Hub
- **Champawat**: Champawat - Sharda River Gorge Station
- **Haridwar**: Bhimgoda Ganga Barrage Control Hub
- **Udham Singh Nagar**: Tarai Drainage Grid & Waterlogged Belt

---

## Quick Start

### 1. Backend (FastAPI)
```powershell
uvicorn backend.main:app --reload --port 8000
```
- Interactive API Docs: `http://localhost:8000/docs`
- Mountain Intelligence Endpoints: `http://localhost:8000/api/v1/mountain/stations`

### 2. Frontend (Next.js 14)
```powershell
cd frontend
npm run dev
```
- Tactical Command Portal: `http://localhost:3000`

---

---

## Key Differentiators (Hackathon Winning Edge)

1. **Autonomous Emergency Route Optimization**: Dijkstra / A* dynamic rerouting around hazard-compromised road segments with 3-state reachability (`connected`, `isolated`, `unmapped`).
2. **Field-Monitoring Prioritization Matrix**: Automated ranking of watersheds by rate-of-change, telemetry staleness, and risk trend for tactical SDRF / DDMA ground inspection dispatch.
3. **Connectivity-Realistic Last-Mile Resilience**: Degrades gracefully to low-bandwidth plain-text SMS (Indian DLT-compliant templates) and offline client-side civil defence acoustic sirens.
4. **Localization & Language Readiness**: Full bilingual warning engine (English & Hindi) with OASIS CAP v1.2 XML feeds for direct NDMA SACHET integration.
5. **Real Connected Scientific APIs**: NASA POWER, Open-Meteo, Copernicus GloFAS, and USGS Earthquake API with zero data fabrication in operational paths.
6. **Historical Disaster Replay**: Zero-temporal-leakage replay of the February 7, 2021 Chamoli GLOF and 2013 Kedarnath cloudburst for empirical validation.
7. **Citizen Ground Truth & SOS Telemetry**: Ingests field hazard observations and automated SMS SOS pings (`^SOS <village> <hazard>$`) with photo evidence verification.

---

## Technical Documentation

- **Data Sources & Tiered Integration Matrix**: [`docs/data-sources.md`](file:///c:/Users/USER/Desktop/Adii%20Folder/ukis/sih%20ps%20flashflood/docs/data-sources.md)
- **Multi-Hazard Risk Model & Statutory Citations**: [`docs/risk-model.md`](file:///c:/Users/USER/Desktop/Adii%20Folder/ukis/sih%20ps%20flashflood/docs/risk-model.md)
- **Historical Replay Demonstration Script (2021 Chamoli GLOF)**: [`docs/historical-demo-script.md`](file:///c:/Users/USER/Desktop/Adii%20Folder/ukis/sih%20ps%20flashflood/docs/historical-demo-script.md)
- **Last-Mile Resilience & Safe Haven Protocol**: [`docs/last-mile-resilience.md`](file:///c:/Users/USER/Desktop/Adii%20Folder/ukis/sih%20ps%20flashflood/docs/last-mile-resilience.md)
- **System Limitations & Audit Ledger**: [`backend/services/system_limitations.py`](file:///c:/Users/USER/Desktop/Adii%20Folder/ukis/sih%20ps%20flashflood/backend/services/system_limitations.py)

---

## Verification & Testing
```powershell
# Run comprehensive backend test suite (151 tests)
python -m pytest tests/

# Compile frontend static export & verify typings
cd frontend
npm run build
```

