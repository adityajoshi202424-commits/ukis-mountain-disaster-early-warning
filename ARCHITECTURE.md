# National Disaster Management Authority (NDMA) & Central Water Commission (CWC)
## Flash Flood Early Warning & Emergency Evacuation Platform Architecture

---

## 1. System Architecture Overview

The system is designed as a high-density, real-time crisis command platform adhering to **Guidelines for Indian Government Websites (GIGW 3.0)** and modeled after the **European Flood Awareness System (EFAS - Copernicus CEMS)**.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   Next.js 14 GIGW 3.0 / EFAS Dashboard                      │
│     (Bilingual: English + Hindi, Leaflet GIS, Ensemble Hydrograph SVG)      │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ HTTP / REST / WebSocket
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FastAPI Production Gateway                          │
│     (Async I/O, Pydantic v2 Validation, CORS, JWT Role-Based Auth)          │
└──────────────┬───────────────────────┬───────────────────────┬──────────────┘
               │                       │                       │
               ▼                       ▼                       ▼
┌──────────────────────────┐ ┌───────────────────┐ ┌──────────────────────────┐
│   Data Ingestion Engine  │ │ Hydrodynamic Risk │ │  Dead-Hand Alert Engine  │
│  (IMD, CWC, ISRO MOSDAC, │ │  (Rate of Rise,   │ │ (Sachet CAP v1.2 XML,    │
│    Copernicus Sentinel)  │ │ Saint-Venant 1D)  │ │  Dijkstra Evacuation)    │
└──────────────┬───────────┘ └─────────┬─────────┘ └───────────┬──────────────┘
               │                       │                       │
               └───────────────────────┼───────────────────────┘
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                 PostgreSQL / PostGIS & Cryptographic Ledger                 │
│         (FIPS PUB 180-4 SHA-256 Consensus Chain, Spatial Geometries)        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Directory Structure

* **`backend/`**:
  * `main.py`: FastAPI application lifespan, CORS, non-blocking provider initialization.
  * `api/v1/`:
    * `sih_ps192_engine.py`: Geospatial layers (`/geospatial/layers`), 51-member ensemble forecasting (`/hydrometrics/forecast/ensemble/{id}`), station telemetry, CSV streaming export, disaster bulletins CRUD, Dijkstra profile routing (`/routing/evacuate`), and CAP v1.2 broadcasting.
    * `alerts.py`: Active alert management, acknowledge/resolve state machine, SMS cellular dispatch.
    * `data.py`: Multi-provider data ingestion and quality validation engine.
    * `sih_demo.py`: Chronological replay engine enforcing $T \le T_{\text{curr}}$ temporal isolation.
  * `data/providers/`: Direct adapters for Open-Meteo, OSM Overpass, CWC AWS gauges, and IMD radars.
  * `models/`: SQLAlchemy and Pydantic v2 data models.
* **`frontend/src/`**:
  * `app/page.tsx`: Master GIGW 3.0 & Copernicus EFAS Light-Mode Scientific Dashboard.
  * `app/globals.css`: Institutional color tokens (`#002E6D`, `#0B4F8A`, `#F4F7FA`), alert borders, and accessibility styles.
  * `components/gis/MapComponent.tsx`: Leaflet tactical map with dynamic GeoJSON overlay rendering.
  * `components/bars/ShelterCapacityBar.tsx`: High-ground shelter occupancy tracking.
  * `components/common/DataSourcesModal.tsx`: Provenance transparency documentation modal.
* **`tests/`**:
  * `api/test_sih_ps192_engine.py`: 78 unit and integration tests validating all mathematical formulas, routing algorithms, and API contracts.
  * `verify_all_evaluation_workflows.py`: Automated end-to-end evaluation suite.
