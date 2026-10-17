# Sentinel-1 SAR & Sentinel-2 GLOF Pilot Monitoring Sites Registry
## UKIS Problem Statement P-011: AI Mountain Disaster Early-Warning Intelligence (Uttarakhand)
### Deliverable 9 (Addendum v2 Section 3.15, 3.16, & Section 5)

> [!IMPORTANT]
> **HONEST SCOPING MANDATE**:
> In strict accordance with the Hackathon Honesty Principle, this platform **does not claim state-wide, real-time InSAR slope monitoring**. Sentinel-1 InSAR coherence tracking is deployed across **three documented pilot slopes** selected for their documented structural vulnerability and strategic lifeline alignment. Automated glacial lake monitoring covers **four critical high-altitude proglacial tarns** in Chamoli and Rudraprayag districts.

---

## 1. Sentinel-1 InSAR Coherence Pilot Slopes (Section 3.15)

### Slope 1: Helang–Joshimath Subsidence Slope
- **Identifier**: `SLOPE-JOSHIMATH-HELANG`
- **District**: Chamoli
- **Lifeline Alignment**: NH-58 (Rishikesh–Badrinath National Highway)
- **Centroid Coordinates**: $30.5420^\circ\text{N}, 79.5480^\circ\text{E}$
- **Elevation Range**: 1,850 m to 2,450 m ASL
- **Slope Aspect & Gradient**: $295^\circ$ (WNW facing scarp), Mean Gradient: $38.5^\circ$
- **Geological Setting**: Main Central Thrust (MCT) shear zone; Vaikrita Group high-grade garnetiferous mica-schists and quartzites overlain by thick colluvial overburden and morainic boulders.
- **Sentinel-1 Orbital Track**: Track 165 (Ascending pass, IW mode, VV+VH polarization)
- **Baseline Coherence ($\gamma_0$)**: $0.74$
- **Critical Coherence Loss Threshold ($\Delta \gamma_{\text{crit}}$)**: $0.28$
- **Selected Archive Imagery Pairs**:
  - Pair 1: 2026-08-01 to 2026-08-13 ($B_\perp = 42.5\text{ m}, \Delta t = 12\text{ days}$)
  - Pair 2: 2026-08-13 to 2026-08-25 ($B_\perp = 68.2\text{ m}, \Delta t = 12\text{ days}$)
  - Pair 3: 2026-08-25 to 2026-09-06 ($B_\perp = 35.0\text{ m}, \Delta t = 12\text{ days}$)
- **Selection Rationale**:
  Chronic slope subsidence documented by CBRI and NGRI in January 2023; toe erosion caused by the Alaknanda riverbed. Millimeter-scale shear creep directly threatens NH-58 transit corridor and the town of Joshimath.

---

### Slope 2: Kedarnath Valley–Mandakini Gorge Flank
- **Identifier**: `SLOPE-KEDARNATH-MANDAKINI`
- **District**: Rudraprayag
- **Lifeline Alignment**: NH-107 (Rudraprayag–Gaurikund Highway)
- **Centroid Coordinates**: $30.7180^\circ\text{N}, 79.0550^\circ\text{E}$
- **Elevation Range**: 2,100 m to 3,200 m ASL
- **Slope Aspect & Gradient**: $185^\circ$ (South facing steep gorge flank), Mean Gradient: $44.0^\circ$
- **Geological Setting**: Central Crystalline Gneissic Complex, fractured granitic gneisses with poorly sorted glacial till mantles.
- **Sentinel-1 Orbital Track**: Track 063 (Descending pass, IW mode, VV polarization)
- **Baseline Coherence ($\gamma_0$)**: $0.68$
- **Critical Coherence Loss Threshold ($\Delta \gamma_{\text{crit}}$)**: $0.25$
- **Selected Archive Imagery Pairs**:
  - Pair 1: 2026-07-28 to 2026-08-09 ($B_\perp = 51.0\text{ m}, \Delta t = 12\text{ days}$)
  - Pair 2: 2026-08-09 to 2026-08-21 ($B_\perp = 39.4\text{ m}, \Delta t = 12\text{ days}$)
  - Pair 3: 2026-08-21 to 2026-09-02 ($B_\perp = 62.1\text{ m}, \Delta t = 12\text{ days}$)
- **Selection Rationale**:
  Site of the devastating 2013 Kedarnath debris surge reactivated during high monsoonal pore pressure. High pilgrim traffic along NH-107 mandates continuous slow-onset creep detection.

---

### Slope 3: Raini / Rishiganga Gorge Ridge
- **Identifier**: `SLOPE-RAINI-RISHIGANGA`
- **District**: Chamoli
- **Lifeline Alignment**: Tapovan–Raini Border Road & Dhauliganga Valley
- **Centroid Coordinates**: $30.4905^\circ\text{N}, 79.6978^\circ\text{E}$
- **Elevation Range**: 2,200 m to 3,850 m ASL
- **Slope Aspect & Gradient**: $230^\circ$ (SW facing canyon scarp), Mean Gradient: $46.5^\circ$
- **Geological Setting**: Martoli Formation quartzites and phyllites; permafrost thermal degradation zones in upper cirques.
- **Sentinel-1 Orbital Track**: Track 165 (Ascending pass, IW mode, VV polarization)
- **Baseline Coherence ($\gamma_0$)**: $0.72$
- **Critical Coherence Loss Threshold ($\Delta \gamma_{\text{crit}}$)**: $0.30$
- **Selected Archive Imagery Pairs**:
  - Historical Baseline: 2021-01-16 to 2021-01-28 ($B_\perp = 44.0\text{ m}, \Delta t = 12\text{ days}$)
  - Pre-Event Pair: 2021-01-28 to 2021-02-09 ($B_\perp = 58.2\text{ m}, \Delta t = 12\text{ days}$)
- **Selection Rationale**:
  Historical ground-zero for the February 7, 2021 disaster (Rishiganga rock-ice avalanche and Tapovan tunnel inundation). Demonstrates zero temporal leakage validation against real historical radar acquisitions.

---

## 2. Automated Glacial Lake (GLOF) Monitoring Sites (Section 3.16)

Automated Normalized Difference Water Index (NDWI) thresholding using Sentinel-2 MSI 10m bands (Band 3 Green $560\text{ nm}$ and Band 8 NIR $842\text{ nm}$):

$$\text{NDWI} = \frac{B_3 - B_8}{B_3 + B_8 + 10^{-7}}$$

| Glacial Lake Name | District | Centroid (Lat, Lon) | Elevation (m) | Downstream River Basin | Baseline Area ($m^2$) | 30-Day Alert Threshold | Sentinel-2 Tile |
|---|---|---|---|---|---|---|---|
| **Chorabari Lake (Gandhi Sarovar)** | Rudraprayag | $30.7483^\circ\text{N}, 79.0620^\circ\text{E}$ | 3,900 m | Mandakini River (Kedarnath - Gaurikund) | $124,500\text{ m}^2$ | $\ge +10.0\%$ | `T44RLV` |
| **Rishiganga Upper Tarn** | Chamoli | $30.4120^\circ\text{N}, 79.7450^\circ\text{E}$ | 4,250 m | Dhauliganga & Alaknanda (Raini - Tapovan) | $82,400\text{ m}^2$ | $\ge +10.0\%$ | `T44RMV` |
| **Vasudhara Glacial Tarn** | Chamoli | $30.7710^\circ\text{N}, 79.4620^\circ\text{E}$ | 3,890 m | Upper Alaknanda (Mana - Badrinath) | $61,200\text{ m}^2$ | $\ge +10.0\%$ | `T44RLV` |
| **Satopanth Glacial Lake** | Chamoli | $30.7420^\circ\text{N}, 79.3550^\circ\text{E}$ | 4,600 m | Alaknanda Headwaters (Swargarohini) | $154,000\text{ m}^2$ | $\ge +10.0\%$ | `T44RLV` |

---

## 3. Fail-Visibly Operational Standards

1. **Cloud Obscuration Protocol**:
   When Sentinel-2 optical cloud cover over any monitored glacial lake exceeds $30\%$, the system:
   - Sets `observation_status = "NO_CLOUD_FREE_OBSERVATION"`.
   - Halts area calculation rather than projecting interpolated synthetic surface water polygons.
   - Visibly flags the observation gap on the operator dashboard.
2. **Outside-Scope Coordinates**:
   When a query or alert request specifies coordinates outside the three pilot slopes, the SAR coherence engine:
   - Returns `within_pilot_scope = false` and `coverage_status = "OUTSIDE_PILOT_SCOPE"`.
   - Never blends or extrapolates SAR signals into unmonitored slopes.
   - Refers the operator to ground telemetry and GPM IMERG rainfall models.
