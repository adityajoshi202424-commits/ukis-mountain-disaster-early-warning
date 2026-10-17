# Architectural Decision Record (ADR-001)
## Relationship between DMMC Uttarakhand Early-Warning Platform & NDMA Sachet CAP Pipeline

### Status
**ACCEPTED & ENFORCED** (Approved by DMMC System Architecture Review)

### Context & Problem Statement
The National Disaster Management Authority (NDMA), Government of India, operates **Sachet**, a national Common Alerting Protocol (CAP) platform designed for all-India disaster warning dissemination via telecom operators.

However, the geographic and physical realities of Uttarakhand (Devbhoomi) present unique operational constraints:
1. **Himalayan Micro-Topography & Steep Slopes**: Mountain disasters (such as Glacial Lake Outburst Floods, cloudburst-induced debris flows, flash floods, and active rockfall creep) originate in high-altitude catchments (e.g., Alaknanda, Mandakini, Bhagirathi, Dhauliganga) where warning lead times are compressed to mere minutes.
2. **Vernacular Dialect Specificity**: While Sachet broadcasts in official Scheduled Languages (English, Hindi), substantial rural mountain populations in high-vulnerability upper valleys communicate predominantly in **Garhwali (`gbm-IN`)** and **Kumaoni (`kfy-IN`)**, neither of which has native OS locale support or automated translation within the national portal.
3. **Local Sensor Inundation Gaps**: Early warning in Uttarakhand requires real-time telemetry from state-specific sensor networks:
   - Central Water Commission (CWC) river gauges along narrow gorges.
   - IIT Roorkee Regional Earthquake Early Warning (EEW) 100+ sensor network.
   - Geological Survey of India (GSI) / ISRO Bhuvan slope deformation tracking.
   - Seasonal Snow & Avalanche Study Establishment (DGRE / SASE) pass advisories.

### Decision
The DMMC Uttarakhand Disaster Early-Warning Platform **sits alongside NDMA Sachet as an autonomous State-level Regional Intelligence Layer with a bi-directional upstream/downstream integration**:

```
                  ┌─────────────────────────────────────┐
                  │    NDMA Sachet National Platform    │
                  │   (CAP 1.2 All-India Telephony API) │
                  └───────────────▲───┬─────────────────┘
                                  │   │
        Upstream Alert Publication│   │Downstream Regional Alert Ingestion
        (DMMC as Authorized State │   │(Uttarakhand Bounding Box Filter)
        Alerting Authority)       │   │
                                  │   ▼
                  ┌─────────────────────────────────────┐
                  │     DMMC Uttarakhand State Hub      │
                  │     (Regional Intelligence Layer)   │
                  └───────────────┬─────────────────────┘
                                  │
    ┌─────────────────────────────┼─────────────────────────────┐
    │                             │                             │
┌───▼─────────────────────┐ ┌─────▼─────────────────────┐ ┌─────▼─────────────────────┐
│ 6 Himalayan Sensor Feeds│ │ Multi-Channel Delivery    │ │ Citizen & Ops Surfaces      │
│ - CWC River Gauges      │ │ - C-DOT Cell Broadcast    │ │ - Citizen Web/Android       │
│ - IITR Seismic EEW WS   │ │ - NIC Multilingual SMS    │ │   (4 Locales, 112 SOS)      │
│ - IMD Nowcast Radar     │ │ - NIC IVR Voice Calls     │ │ - DMMC Admin/Ops Dashboard  │
│ - GSI Slope Deformation │ │ - WhatsApp Business API   │ │   (Report Review, Override) │
│ - FSI Forest Fire Track │ │ - FCM Push Notifications  │ │ - "Mark Safe" & Crowd Rep.  │
│ - DGRE Avalanche Alerts │ └───────────────────────────┘ └───────────────────────────┘
└─────────────────────────┘
```

1. **Downstream Ingestion**:
   - DMMC ingests national CAP XML/JSON feeds published by NDMA Sachet and filters alerts matching Uttarakhand's 13 mountain districts and spatial bounding box (`28.7161°N - 31.4558°N, 77.5757°E - 81.0475°E`).
2. **Upstream Publication (Closing the Loop)**:
   - When DMMC State Emergency Operation Centre (SEOC) detects an emergency via regional telemetry or issues a verified warning, it formats a CAP 1.2 payload and dispatches it directly to NDMA Sachet (`NDMA_SACHET_FEED_URL`) as an authorized Sub-State Alerting Authority.
3. **Addressing Genuine Sachet Gaps**:
   - **Hyper-Local Lead Time**: Direct integration with CWC river gauges and IIT Roorkee seismic WebSocket yields sub-minute lead times before national aggregation occurs.
   - **Regional Vernacular Parity**: DMMC maintains authenticated translation dictionaries in Garhwali (`gbm-IN`) and Kumaoni (`kfy-IN`), streaming text and automated IVR voice calls in regional dialects.
   - **Ground-Truth Verification**: Crowdsourced citizen observations ("road blocked", "debris surge") provide rapid visual verification for SEOC operators to elevate sensor alerts to CRITICAL tier.

### Consequences
- **Positive**: Zero blind duplication of telecom infrastructure; full national compliance with NDMA CAP 1.2 standards; provides life-saving mountain-specific lead times and dialect support.
- **Fail-Closed Governance**: If NDMA Sachet or institutional endpoints are unconfigured in `.env.production`, adapters fail closed with explicit logging (`"no credentials configured"`), never synthesizing fake alerts.
