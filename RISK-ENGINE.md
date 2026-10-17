# AI Mountain Disaster Early-Warning Intelligence — Risk Engine
## UKIS Problem Statement P-011: Uttarakhand Mountain & Hill Early-Warning System

---

## 1. Mathematical Formulation for Steep Himalayan Catchments

Unlike low-gradient floodplain basins where floodwaters travel over days, Uttarakhand's steep Himalayan micro-watersheds experience response times of **30 to 120 minutes**. The risk engine evaluates four distinct, physically grounded hazard modules.

---

### Module 1: Cloudburst-Triggered Flash Flood
Cloudbursts are characterized by intense precipitation exceeding statutory thresholds over short durations in high-gradient catchments.

$$\frac{\Delta P}{\Delta t} = \frac{P(t) - P(t - \Delta t)}{\Delta t} \quad [\text{mm/hour}]$$

* **IMD Cloudburst Criterion**: Rainfall rate $\ge 100\text{ mm/hr}$ (or $\ge 50\text{ mm}$ in 30 minutes) over a localized micro-catchment (IMD SOP-01).
* **IMD Mountain Warning Thresholds**:
  - Yellow Watch: $15.0 - 30.0\text{ mm/hr}$
  - Orange Warning: $30.0 - 64.4\text{ mm/hr}$
  - Red Emergency: $\ge 65.0\text{ mm/hr}$

**Catchment Runoff Discharge ($Q_{\text{peak}}$):**
$$Q_{\text{peak}} = C \cdot I \cdot A$$
$$C = C_{\text{base}} + (1 - C_{\text{base}}) \cdot S_m^{1.8}$$
Where:
- $C$ is the dynamic mountain runoff coefficient.
- $S_m$ is the topsoil volumetric saturation index ($0.0 - 1.0$) from NASA SMAP / ERA5-Land.
- When $S_m \ge 0.82$, rocky Himalayan terrain exhibits near-total surface impermeability ($C \to 0.95$), triggering immediate torrent surge.

---

### Module 2: Glacial Lake Outburst Flood (GLOF) Expansion & Breach
GLOF risk is evaluated from optical/SAR satellite observations (Sentinel-1 SAR, Sentinel-2 MSI, Landsat-9) tracking moraine-dammed and supraglacial lakes (e.g., Chorabari, Vasuki Tal, Satopanth).

$$R_{\text{GLOF}} = \frac{\Delta A_{\text{lake}}}{\Delta t} = \frac{A_{\text{lake}}(t) - A_{\text{lake}}(t - \Delta t)}{\Delta t} \quad [\text{m}^2/\text{day}]$$

$$\text{Risk}_{\text{GLOF}} = w_1 \cdot \left(\frac{\Delta A_{\text{lake}}}{A_{\text{baseline}}}\right) + w_2 \cdot T_{\text{freezing\_anomaly}} + w_3 \cdot D_{\text{moraine\_steepness}}$$

* **NDMA Guidelines (2020)**: Area expansion $> 15\%$ over 30 days or moraine crest freeboard reduction $< 2.0\text{ m}$ indicates severe breach vulnerability.
* **Sentinel-1 SAR C-Band Advantage**: Penetrates dense monsoon cloud cover to measure water backscatter ($\sigma_0 \le -18\text{ dB}$) when optical sensors are blinded.

---

### Module 3: Landslide-Dammed River Breach (Drop-Then-Spike Anomaly)
As observed in the 2021 Rishiganga/Dhauliganga catastrophe and 1970 Alaknanda disaster, rock-ice avalanches or debris flows dam high-velocity mountain rivers, causing stage levels to abruptly drop downstream, followed by catastrophic breach surge.

**Stage Acceleration Anomaly Metric ($\mathcal{A}_{\text{dam}}$):**
$$\mathcal{A}_{\text{dam}} = \begin{cases} 
\text{BLOCKAGE DETECTED} & \text{if } \frac{dH}{dt} \le -0.40\text{ m/hr} \text{ while upstream rainfall } > 15\text{ mm/hr} \\
\text{CATASTROPHIC BREACH} & \text{if } \frac{dH}{dt} \ge +1.20\text{ m/hr after verified blockage}
\end{cases}$$

Downstream wavefront propagation across Himalayan river corridors:
$$\text{Rishiganga} \xrightarrow{+12\text{ min}} \text{Tapovan / Dhauliganga} \xrightarrow{+40\text{ min}} \text{Joshimath (Alaknanda)} \xrightarrow{+75\text{ min}} \text{Chamoli} \xrightarrow{+135\text{ min}} \text{Rudraprayag} \xrightarrow{+210\text{ min}} \text{Devprayag}$$

---

### Module 4: Slope Failure & Debris Flow Susceptibility
Evaluates infinite slope stability coupled with hydro-mechanical saturation:

$$F_s = \frac{c' + (\gamma_{\text{soil}} \cdot z \cdot \cos^2\theta - u) \cdot \tan\phi'}{\gamma_{\text{soil}} \cdot z \cdot \sin\theta \cdot \cos\theta}$$

Where:
- $\theta$: Slope gradient angle (derived from Cartosat / SRTM 30m DEM).
- $c'$: Effective soil cohesion ($\approx 12\text{ kPa}$ for Garhwal colluvium).
- $\phi'$: Internal friction angle ($\approx 32^\circ$).
- $u$: Pore-water pressure ($u = \gamma_w \cdot h_w \cdot \cos^2\theta$, driven by Antecedent Precipitation Index $API_{15}$).
- **Failure Condition**: $F_s < 1.0$ triggers immediate debris slide into river channel choke points.

---

## 2. Multi-Factor Explainability Matrix

Every early warning issued by the platform decomposes the composite risk index into explicit physical attributions with guideline citations:

| Contributing Factor | Measured Value | Standard Threshold | Statutory Guideline Citation | Factor Weight |
|---|---|---|---|---|
| Rainfall Intensity ($\Delta P/\Delta t$) | $42.0\text{ mm/hr}$ | $30.0\text{ mm/hr}$ | IMD SOP-01 Orange Heavy Rain Protocol | $35\%$ |
| River Surge Velocity ($\Delta H/\Delta t$) | $+1.45\text{ m/hr}$ | $+0.80\text{ m/hr}$ | CWC Himalayan Flash Flood Directive | $30\%$ |
| Glacial Lake Delta ($\Delta A_{\text{lake}}$) | $+18.2\%\text{ / 30d}$ | $+15.0\%\text{ / 30d}$ | NDMA 2020 Glacial Lake Guidelines | $15\%$ |
| Slope Saturation ($S_m$) | $88.5\%$ | $80.0\%$ | GSI/Caine Landslide Saturation Criterion | $10\%$ |
| Seismic Proximity ($\mathcal{M} \ge 3.5$) | $14.2\text{ km}$ | $50.0\text{ km}$ | NCS Seismic Trigger Correlation | $10\%$ |
