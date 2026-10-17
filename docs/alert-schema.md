# Common Alerting Protocol (CAP v1.2) & Multi-Channel Alert Action Schema
## UKIS Problem Statement P-011: AI Mountain Disaster Early-Warning Intelligence

This document defines the actionable alert payload schemas emitted by the Uttarakhand Mountain Disaster Early-Warning platform. The system operates on an **action-oriented paradigm**: the moment a risk score escalates across a statutory threshold, the system synthesizes machine-readable CAP v1.2 XML for national authorities (NDMA SACHET), formats single-line plain-text alerts for degraded Himalayan cellular networks, embeds real-time dynamic evacuation routes, and triggers physical community sirens.

---

## 1. Statutory Dispatch Hierarchy & Anti-Alert-Fatigue Rules

To prevent alert fatigue and cry-wolf degradation among district authorities and villagers, the platform enforces strict trigger conditions:

```
[Risk Evaluation Tick]
         │
         ▼
[Is Severity Level Increasing?]
  ├── NO  (Unchanged or Decreasing) ──► Suppress Dispatch (Prevent Fatigue)
  └── YES (Escalation Detected)
         │
         ├── Low / Medium (Green/Yellow) ──► Dashboard Advisory Flag Only (No SMS)
         │
         ├── High (Orange) ───────────────► Dashboard + SMS / WhatsApp to DDMA Control Room
         │                                  + Dijkstra Evacuation Route Embedded
         │
         └── Critical (Red) ──────────────► Dashboard + SMS / WhatsApp to DDMA
                                            + SMS to Village Field Contacts
                                            + Physical 120dB Siren Relays Actuated (ESP32)
                                            + National CAP v1.2 XML Broadcast
```

---

## 2. Common Alerting Protocol (CAP v1.2) Specification

The system constructs OASIS CAP v1.2 XML payloads compliant with the **National Disaster Management Authority (NDMA SACHET)** portal and the **Department of Telecommunications (DoT) Cell Broadcast Emergency System**.

### XML Schema Example (`POST /api/v1/mountain/bulletin/generate`)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<alert xmlns="urn:oasis:names:tc:emergency:cap:1.2">
  <identifier>USDMA-UKIS-P011-UK-CHAMOLI-01-1789396800</identifier>
  <sender>usdma.eoc@uk.gov.in</sender>
  <sent>2026-09-14T20:15:00+05:30</sent>
  <status>Actual</status>
  <msgType>Alert</msgType>
  <scope>Public</scope>
  <info>
    <category>Geo</category>
    <event>Mountain Multi-Hazard Early Warning</event>
    <urgency>Immediate</urgency>
    <severity>Extreme</severity>
    <certainty>Observed</certainty>
    <eventCode>
      <valueName>UKIS-P011</valueName>
      <value>Landslide Subsidence &amp; GLOF</value>
    </eventCode>
    <headline>Joshimath - Tapovan Hazard Observational Grid - RED Warning</headline>
    <description>
      Multi-hazard index is 84.5/100 (RED). Primary drivers: 48h rainfall 112.0mm (crit: 35.0mm) on 38.5° slope, 
      freezing level at 4850m (16.9°C at 1890m elevation), soil saturation at 86.4%, and recent seismic peak M3.8.
    </description>
    <instruction>
      ACTIVATE EOC RED PROTOCOL. Impose vehicular travel ban on NH-58. 
      Evacuate vulnerable slopes to designated shelter: Joshimath Cantonment High-Ground Shelter via Auli Ascent Road -> NH-58 Upper Bypass.
    </instruction>
    <area>
      <areaDesc>Chamoli District, Uttarakhand</areaDesc>
      <circle>30.5526,79.5632,25.0</circle>
    </area>
  </info>
</alert>
```

### Integration Requirements for Live National SACHET Hand-Off
1. **Digital Signing**: Production hand-off requires an X.509 XML-DSig signature generated with a hardware security module (HSM) certificate authorized by the Ministry of Communications.
2. **Geofenced Polygons**: While the prototype includes circular coordinate bounds (`<circle>`), production integration utilizes Bhuvan village cadastral boundary GeoJSON polygons.
3. **C-DAC Gateway Protocol**: Real delivery pushes to the C-DAC CAP aggregator via mutual TLS (mTLS) with standard OASIS EDXL-DE envelope wrapping.

---

## 3. Plain-Text Single-Line SMS Payload Specification

Cellular connectivity in steep Himalayan river gorges frequently degrades to 2G SMS or single-bar GSM signal. Messages must be **single-line, non-breaking, and self-contained**:

### Plain-Text Template
```
[TIER] [Village/Watershed]. [1-line reason with threshold]. Safe point: [nearest shelter]. Route: via [road]; [road] flagged unsafe.
```

### Production Examples Emitted by Engine

#### Scenario A: High / Orange Escalation
```
[ORANGE] Chamoli_Joshimath_Zone. Rainfall intensity 42mm/hr exceeded IMD Orange criteria (30mm/hr) with river rate-of-rise 1.45m/hr (IMD SOP-01 Orange Criteria / CWC Stage Warning Mark). Safe point: Joshimath Cantonment High-Ground Shelter. Route: via Auli Ascent Road -> NH-58 Upper Bypass -> Cantonment Ridge Approach; Valley Riparian Track flagged unsafe.
```

#### Scenario B: Critical / Red Escalation (GLOF Breach)
```
[RED] Chamoli_Joshimath_Zone. Cloudburst surge detected: 112mm/hr with lake breach wave (IMD SOP-01 Orange Criteria / CWC Stage Warning Mark). Safe point: Joshimath Cantonment High-Ground Shelter. Route: via Auli Ascent Road -> NH-58 Upper Bypass -> Cantonment Ridge Approach; Valley Riparian Track flagged unsafe.
```

---

## 4. WhatsApp Business API Payload Specification

For users with smartphone and data connectivity, the dispatcher duplicates the plain-text advisory through Meta's WhatsApp Cloud API (`POST https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages`):

```json
{
  "messaging_product": "whatsapp",
  "recipient_type": "individual",
  "to": "9198640XXXXX",
  "type": "text",
  "text": {
    "preview_url": false,
    "body": "🚨 *USDMA EMERGENCY ADVISORY: CRITICAL TIER ESCALATION*\n\n*Location:* Joshimath, Chamoli District\n*Reason:* Cloudburst surge 112mm/hr with lake breach wave.\n*Designated Safe Shelter:* Joshimath Cantonment High-Ground Shelter\n*Evacuation Route:* via Auli Ascent Road ➔ NH-58 Upper Bypass.\n⚠️ *Warning:* Valley Riparian Track is SUBMERGED and impassable."
  }
}
```

---

## 5. Physical Siren / Hardware Actuator Webhook Specification

Upon Critical (Red) tier escalation, the platform actuates on-site physical siren towers and strobe lights to alert communities without relying on cellular phones.

### Webhook Endpoint
- **Internal API:** `POST /api/v1/mountain/alerts/siren/trigger`
- **Root Specification Alias:** `POST /alerts/critical/trigger-siren`

### Webhook Request Payload
```json
{
  "action": "TRIGGER_ALARM",
  "station_id": "UK-CHAMOLI-01",
  "district": "Chamoli",
  "alert_level": "CRITICAL",
  "decibels_target": 120,
  "sound_profile": "CONTINUOUS_HIMALAYAN_EVACUATION_WARBLE",
  "timestamp": "2026-09-14T20:15:00Z"
}
```

### Hardware Integration Protocol (ESP32 Micro-Controller)
1. **Relay Actuation**: The ESP32 listens via an encrypted HTTP/MQTT listener. Upon receiving `TRIGGER_ALARM`, GPIO Pin 22 drives an optocoupled solid-state relay (SSR) powering a 120dB industrial motorized siren.
2. **Failsafe Timeout**: The firmware implements a 180-second automatic shutoff timer to prevent hardware overheating if communications drop.
3. **Telemetry Acknowledgment**: The ESP32 returns `{ "status": "HARDWARE_RELAY_ACTIVATED", "battery_voltage": 12.4, "decibel_sensor_feedback": 118.6 }`.