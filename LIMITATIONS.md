# Platform Limitations & Operational Calibration Scope
## UKIS Problem Statement P-011: AI Mountain Disaster Early-Warning Intelligence — Uttarakhand

---

## 1. Scientific Calibration & Geography Scope
* **Regional Terrain Adaptation**: Hydrodynamic coefficients ($n$ Manning roughness factor $\approx 0.040$, steep gorge wave celerity $c \approx 6.8\text{ m/s}$, wave attenuation $\lambda = 0.08\text{ hr}^{-1}$) and slope failure models are calibrated specifically for **Uttarakhand's Himalayan river systems** (Alaknanda, Bhagirathi, Mandakini, Rishiganga, Dhauliganga, Pindar, Nayar, and Kosi) and its 13 hill districts.
* **Glacial Lake Satellite Update Cadence**: Satellite SAR passes (Copernicus Sentinel-1) have a 6-day revisit cycle over Uttarakhand. Glacial lake expansion is monitored as a multi-temporal time-series rate-of-change ($\Delta A_{\text{lake}}/\Delta t$) rather than a continuous real-time video stream.
* **Micro-Catchment Infiltration**: Infiltration estimates depend on 30m Cartosat/SRTM DEM topographic grids and NASA SMAP / ERA5-Land topsoil moisture. Localized slope fractures or moraine fissures require in-situ geotechnical piezometers for sub-surface pore pressure validation.

---

## 2. Infrastructure & Carrier Integrations
* **Cellular SMS Carrier Gateway**: The platform generates valid OASIS CAP v1.2 XML feeds (for NDMA / USDMA Sachet integration) and native cellular intent dispatch. Direct automated SMS broadcast requires production Twilio / C-DoT SMS gateway credentials in `.env`.
* **Government Cloud Deployment**: Production deployment under MeghRaj / Uttarakhand State Data Centre (SDC) infrastructure requires STQC security audit certification.
