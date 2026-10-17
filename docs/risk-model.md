# Multi-Hazard Mountain Risk Model & Explainability Engine
## UKIS Problem Statement P-011: AI Mountain Disaster Early-Warning Intelligence — Uttarakhand

---

## 1. Physical Context & Hydro-Meteorological Paradigm Shift

The physics of mountain hazards in the young, fractured Himalayan terrain of Uttarakhand differ fundamentally from riverine floodplain inundation:

| Physical Dimension | Lowland Floodplain Model (Assam/Brahmaputra) | Steep Himalayan Mountain Model (Uttarakhand) |
|---|---|---|
| **Dominant Hazard Mechanism** | Prolonged regional overbank river spilling | High-velocity flash floods, cloudbursts, GLOF, debris torrents |
| **Response Time ($T_c$)** | 24 to 96 hours | **30 to 120 minutes** |
| **Warning Lead Time** | Multi-day flood stage tracking | **Sub-hourly calculus rates of rise & satellite delta triggers** |
| **Risk Spatial Unit** | River basin polygon ($> 500\text{ km}^2$) | **Micro-watershed / ravine catchment ($2 - 25\text{ km}^2$)** |
| **Exposed Assets** | Floodplain farming communities | **Hill villages, Char Dham pilgrimage routes, hydroelectric plants** |

All threshold parameters in this engine are loaded from versioned configuration (`backend/config/hazard_thresholds.py`), which cites statutory Indian early-warning directives.

---

## 2. Mathematical Formulations of the 4 Hazard Modules

### Module 1: Cloudburst-Triggered Flash Flood

#### A. Precipitation Intensity Acceleration
In mountain catchments, total daily rainfall is less dangerous than short-duration intensity. We compute the first derivative of precipitation:

$$\dot{P} = \frac{dP}{dt} \approx \frac{P(t) - P(t - \Delta t)}{\Delta t} \quad [\text{mm/hr}]$$

* **IMD Cloudburst Definition**: $\dot{P} \ge 100\text{ mm/hr}$ or $\ge 50\text{ mm}$ in 30 minutes over an area of $\sim 20 - 30\text{ km}^2$ (*IMD Standard Operating Procedure for Weather Forecasting, SOP-01*).
* **IMD Color-Coded Intensity Bands**:
  $$\text{Alert Level} = \begin{cases}
  \text{GREEN (Normal)} & \dot{P} < 15.0\text{ mm/hr} \\
  \text{YELLOW (Watch)} & 15.0 \le \dot{P} < 30.0\text{ mm/hr} \\
  \text{ORANGE (Warning)} & 30.0 \le \dot{P} < 64.4\text{ mm/hr} \\
  \text{RED (Severe Emergency)} & \dot{P} \ge 64.5\text{ mm/hr}
  \end{cases}$$

#### B. Dynamic Mountain Runoff Coefficient ($C$)
The peak discharge $Q_{\text{peak}}$ entering the village channel is governed by the Rational-Himalayan equation:

$$Q_{\text{peak}} = C(S_m) \cdot \dot{P} \cdot A_{\text{catchment}}$$

$$C(S_m) = C_0 + (1.0 - C_0) \cdot S_m^{1.8}$$

Where:
- $C_0 = 0.35$ (baseline rocky forest infiltration capacity).
- $S_m$ is the topsoil volumetric saturation ($0.0 - 1.0$) from NASA SMAP / ERA5-Land.
- When antecedent rains push $S_m \ge 0.82$, topsoil pores are completely filled; $C \to 0.94$, converting almost $100\%$ of rainfall directly into roaring surface runoff within 20 minutes.

---

### Module 2: Glacial Lake Outburst Flood (GLOF) Time-Series Change

GLOF hazards arise from the sudden failure of moraine dams containing supraglacial or proglacial lakes.

#### A. Lake Surface Expansion Rate
Rather than relying on a static lake-area threshold (which ignores expanding dangerous lakes), the model tracks the **rate of area change** across successive satellite passes:

$$\Delta A_{\text{lake}}(t) = \frac{A_{\text{lake}}(t) - A_{\text{lake}}(t - \tau)}{\tau} \quad [\text{m}^2/\text{day}]$$

$$\text{Expansion Ratio } (\mathcal{R}_{\text{GLOF}}) = \frac{A_{\text{lake}}(t) - A_{\text{baseline}}}{A_{\text{baseline}}} \times 100\%$$

* **NDMA GLOF Early Warning Guidelines (2020)**:
  - $\mathcal{R}_{\text{GLOF}} \ge 15.0\%$ over 30 days $\implies$ **High Moraine Unstable Warning**.
  - Moraine freeboard degradation rate $\ge 0.20\text{ m/month}$ $\implies$ **Structural Breach Alert**.

#### B. Multi-Spectral & SAR Water Index (MNDWI & SAR Backscatter)
- **Optical (Cloud-free)**: Modified Normalized Difference Water Index:
  $$\text{MNDWI} = \frac{\rho_{\text{Green}} - \rho_{\text{SWIR}}}{\rho_{\text{Green}} + \rho_{\text{SWIR}}}$$
  Water pixels are classified where $\text{MNDWI} > 0.15$.
- **SAR (Monsoon Overcast Fallback)**: Copernicus Sentinel-1 C-band VV/VH backscatter:
  $$\sigma_0 \le -18.0\text{ dB}$$
  Smooth open water surfaces specularly reflect radar pulses away from the sensor, providing reliable lake boundary mapping through dense monsoon cloud cover.

---

### Module 3: Landslide-Dam-Break Flood (Drop-Then-Spike Anomaly)

Forensic investigations of the **February 7, 2021 Rishiganga disaster** (Wadia Institute of Himalayan Geology / GSI) established that catastrophic rock-ice avalanches create temporary debris dams in narrow gorges, followed within minutes to hours by violent overtopping or catastrophic breach.

#### A. The Anomaly Detection Metric ($\mathcal{A}_{\text{dam}}$)
River stage acceleration $\ddot{H}$ and rate of rise $\dot{H}$ are evaluated against upstream rainfall:

$$\dot{H} = \frac{H(t) - H(t - \Delta t)}{\Delta t} \quad [\text{m/hr}]$$

$$\mathcal{A}_{\text{dam}}(t) = \begin{cases}
\text{CHANNEL BLOCKAGE} & \text{if } \dot{H}_{\text{downstream}} \le -0.40\text{ m/hr} \text{ and } \dot{P}_{\text{upstream}} \ge 15.0\text{ mm/hr} \\
\text{CATASTROPHIC BREACH} & \text{if } \dot{H}_{\text{downstream}} \ge +1.20\text{ m/hr after BLOCKAGE state} \\
\text{NORMAL} & \text{otherwise}
\end{cases}$$

#### B. Wavefront Celerity in Steep Valleys
In high-gradient gorges (average bed slope $S_0 \ge 0.04$), flood wave speed $c$ follows the Saint-Venant kinematic approximation:

$$c = \frac{5}{3} \sqrt{g \cdot R_h \cdot S_0} \approx 6.5 - 9.0\text{ m/s} \quad (23 - 32\text{ km/hr})$$

This rapid velocity yields the following observed cascade lead times:
$$\text{Ronti Glacier} \xrightarrow{12\text{ min}} \text{Raini Village} \xrightarrow{28\text{ min}} \text{Tapovan HEP} \xrightarrow{45\text{ min}} \text{Joshimath} \xrightarrow{80\text{ min}} \text{Chamoli} \xrightarrow{150\text{ min}} \text{Rudraprayag}$$

---

### Module 4: Debris Flow & Slope Failure Susceptibility

Steep hill slopes above road corridors (NH-58, NH-107 Char Dham routes) are evaluated using the limit-equilibrium infinite slope stability model coupled with transient pore-water pressure:

$$F_s = \frac{c' + (\gamma_{\text{soil}} \cdot z \cdot \cos^2\theta - u) \cdot \tan\phi'}{\gamma_{\text{soil}} \cdot z \cdot \sin\theta \cdot \cos\theta}$$

Where:
- $\theta$: Slope gradient angle (derived from 30m Cartosat/SRTM DEM).
- $c' = 12.5\text{ kPa}$ (effective cohesion of weathered Garhwal mica schist).
- $\phi' = 32.0^\circ$ (internal angle of friction).
- $\gamma_{\text{soil}} = 19.5\text{ kN/m}^3$ (bulk unit weight of colluvium).
- $z = 2.5\text{ m}$ (average soil mantle depth over bedrock).
- $u = \gamma_w \cdot m_w \cdot z \cdot \cos^2\theta$ (transient pore-water pressure, where $m_w$ is the saturated thickness fraction driven by the 15-day Antecedent Precipitation Index $API_{15}$).

**Slope Failure Criterion:**
- $F_s \ge 1.30$: **STABLE**
- $1.00 \le F_s < 1.30$: **MARGINALLY UNSTABLE (Watch Alert)**
- $F_s < 1.00$: **ACTIVE SLOPE COLLAPSE / DEBRIS FLOW TRIGGERED (Red Evacuation)**

---

## 3. Composite Risk Index Formulation

The overall composite hazard index $I_{\text{composite}} \in [0.0, 1.0]$ is computed as a weighted multi-hazard attribution:

$$I_{\text{composite}} = w_{\text{rain}} \cdot \mathcal{S}_{\text{rain}} + w_{\text{river}} \cdot \mathcal{S}_{\text{river}} + w_{\text{glof}} \cdot \mathcal{S}_{\text{glof}} + w_{\text{slope}} \cdot \mathcal{S}_{\text{slope}} + w_{\text{seismic}} \cdot \mathcal{S}_{\text{seismic}}$$

### Standard Weights Configuration:
- **Rainfall Intensity Weight ($w_{\text{rain}}$)**: $0.35$ (Primary trigger for cloudbursts)
- **River Surge Velocity Weight ($w_{\text{river}}$)**: $0.30$ (Direct hydraulic wavefront measurement)
- **GLOF Rate of Change Weight ($w_{\text{glof}}$)**: $0.15$ (Glacial lake burst potential)
- **Slope Saturation / Stability Weight ($w_{\text{slope}}$)**: $0.10$ (Landslide channel damming risk)
- **Seismic Activity Weight ($w_{\text{seismic}}$)**: $0.10$ (Recent $\mathcal{M} \ge 3.5$ shake trigger)

$$\sum w_i = 1.0$$

### Composite Threshold Classification:
- **LOW / GREEN**: $I_{\text{composite}} < 0.35$
- **MODERATE / YELLOW**: $0.35 \le I_{\text{composite}} < 0.60$
- **HIGH / ORANGE**: $0.60 \le I_{\text{composite}} < 0.80$
- **CRITICAL / RED**: $I_{\text{composite}} \ge 0.80$

---

## 4. Explainable AI (XAI) Feature Attribution Protocol

Every alert emitted by the system contains a **non-black-box plain language rationale** that operators can immediately cite to district magistrates and village heads.

### Example Generated Rationale:
```json
{
  "composite_risk_score": 0.842,
  "risk_tier": "CRITICAL",
  "district": "Chamoli",
  "watershed": "Rishiganga-Alaknanda Basin",
  "rationale": "CRITICAL RISK ELEVATED (0.84): Rainfall intensity 48.5 mm/hr exceeds IMD Orange Warning threshold (30.0 mm/hr per IMD SOP-01); River stage velocity accelerated by +1.45 m/hr over last 45 minutes at Joshimath Gauge (CWC Flash Danger criterion: +0.80 m/hr); Topsoil saturation 88.2% indicates near-zero infiltration (GSI Debris Flow criterion); Vasuki Tal expansion rate at +16.4%/30d (NDMA 2020 GLOF Directive).",
  "citations": [
    "IMD SOP-01: Standard Operating Procedure for Extreme Weather Forecasting",
    "CWC Himalayan River Flash Flood Danger Stage Manual",
    "NDMA 2020: Management of Glacial Lake Outburst Floods",
    "GSI Landslide Hazard Zonation Guidelines for Uttarakhand Himalaya"
  ]
}
```

---

## 5. Statutory References & Citations

1. **India Meteorological Department (IMD)**:
   - *Standard Operating Procedure (SOP-01) for Weather Forecasting and Warning Services*. Ministry of Earth Sciences, Govt. of India.
   - *Guidelines on Cloudburst Monitoring and Nowcasting using Doppler Weather Radars (DWR)*.
2. **Central Water Commission (CWC)**:
   - *Himalayan River Basin Flood Forecasting Manual and Gauge Stage Criteria*. Ministry of Jal Shakti.
3. **National Disaster Management Authority (NDMA)**:
   - *National Disaster Management Guidelines: Management of Glacial Lake Outburst Floods (GLOFs)*. Govt. of India, October 2020.
   - *Guidelines for Management of Landslides and Snow Avalanches*.
4. **Geological Survey of India (GSI)**:
   - *National Landslide Susceptibility Mapping (NLSM) Protocol for Uttarakhand Himalaya*.
5. **Wadia Institute of Himalayan Geology (WIHG)**:
   - Forensic Analysis of the Chamoli Rock-Ice Avalanche and Flash Flood Disaster of February 7, 2021 (*Science / Nature Geoscience* reports).
