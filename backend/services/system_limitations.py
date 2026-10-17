"""
System Limitations, Operational Boundaries, and "What This System Does Not Claim" Registry.
UKIS Addendum v2 Section 3.17 (Tier 2).

Provides transparent, uncompromised honesty regarding:
1. Spatial coverage of watersheds, corridors, and villages (Full vs. Partial vs. None).
2. Feature maturity classification across Tiers 1 through 4.
3. Explicit probabilistic decision-support disclaimer (not an IMD/NDMA replacement).
4. Data latency specifications per telemetry and satellite source.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List
from pydantic import BaseModel, Field


class WatershedCoverage(BaseModel):
    watershed_or_corridor: str
    district: str
    coverage_level: str  # 'FULL_TELEMETRY', 'PARTIAL_SATELLITE_ONLY', 'UNMONITORED_GAP'
    ground_sensors: str
    satellite_layers: str
    operational_notes: str


class FeatureMaturityItem(BaseModel):
    item_number: int
    name: str
    tier: str  # 'TIER_1', 'TIER_2', 'TIER_3', 'TIER_4'
    operational_maturity: str  # 'LIVE_OPERATIONAL', 'PROTOTYPE_SCOPE', 'ROADMAP_DESIGN_ONLY'
    scope_statement: str


class DataLatencySpecification(BaseModel):
    source_name: str
    provider: str
    update_cadence: str
    typical_latency: str
    operational_implication: str


class SystemLimitationsReport(BaseModel):
    system_name: str
    specification: str
    published_at: datetime
    probabilistic_disclaimer: str
    what_this_system_does_not_claim: List[str]
    watershed_coverage_matrix: List[WatershedCoverage]
    feature_maturity_tiers: List[FeatureMaturityItem]
    data_latency_matrix: List[DataLatencySpecification]
    honest_hackathon_positioning: str


# ---------------------------------------------------------------------------
# Authoritative Limitations & Boundaries Catalog
# ---------------------------------------------------------------------------

WATERSHED_COVERAGE_CATALOG: List[WatershedCoverage] = [
    WatershedCoverage(
        watershed_or_corridor="Upper Alaknanda Basin (Joshimath - Badrinath Corridor)",
        district="Chamoli",
        coverage_level="FULL_TELEMETRY",
        ground_sensors="CWC River Gauge (Pipalkoti/Tapovan), IMD AWS, High-Altitude Ultrasonic",
        satellite_layers="Sentinel-1 InSAR Pilot Slope, Sentinel-2 NDWI Glacial Lake, GPM IMERG Precipitation",
        operational_notes="Comprehensive dual-layer telemetry with verified route graph and shelter coordinates.",
    ),
    WatershedCoverage(
        watershed_or_corridor="Mandakini Valley (Kedarnath - Sonprayag Corridor)",
        district="Rudraprayag",
        coverage_level="FULL_TELEMETRY",
        ground_sensors="CWC Gaurikund Gauge, IMD Kedarnath AWS",
        satellite_layers="Sentinel-1 InSAR Pilot Flank, Sentinel-2 Chorabari Tarn Monitoring, GPM IMERG",
        operational_notes="Full coverage of the pilgrimage corridor with downslope proximity escalation.",
    ),
    WatershedCoverage(
        watershed_or_corridor="Bhagirathi Gorge (Harshil - Bhatwari Corridor)",
        district="Uttarkashi",
        coverage_level="PARTIAL_SATELLITE_ONLY",
        ground_sensors="CWC Bhatwari Gauge (Intermittent 4G uplink)",
        satellite_layers="GPM IMERG 0.1° grid, Cartosat DEM 30m terrain model",
        operational_notes="No ground InSAR pilot station; risk estimated via satellite rainfall and slope angles.",
    ),
    WatershedCoverage(
        watershed_or_corridor="Kali & Goriganga Basins (Dharchula - Munsyari)",
        district="Pithoragarh",
        coverage_level="PARTIAL_SATELLITE_ONLY",
        ground_sensors="Regional IMD Dharchula AWS only",
        satellite_layers="GPM IMERG gap-fill, Copernicus Landcover",
        operational_notes="Sparse sensor density. Model treats this as moderate-uncertainty sector.",
    ),
    WatershedCoverage(
        watershed_or_corridor="Upper Tons / Har Ki Dun Catchment",
        district="Uttarkashi",
        coverage_level="UNMONITORED_GAP",
        ground_sensors="None (No active CWC/IMD stations)",
        satellite_layers="GPM IMERG coarse satellite grid only",
        operational_notes="Monitored via regional extrapolation. Relies on Tier 4 LoRa proposal for gap closure.",
    ),
    WatershedCoverage(
        watershed_or_corridor="Pindar River Headwaters (Sundardhunga / Pindari)",
        district="Bageshwar",
        coverage_level="UNMONITORED_GAP",
        ground_sensors="None (Telemetry void zone)",
        satellite_layers="Sentinel-2 periodic optical passes only",
        operational_notes="Glacial lake expansion tracked when cloud-free; zero real-time river stage telemetry.",
    ),
]


FEATURE_MATURITY_REGISTRY: List[FeatureMaturityItem] = [
    # Tier 1 — Core Action Pipeline
    FeatureMaturityItem(
        item_number=1,
        name="Automatic Tiered SMS Dispatch",
        tier="TIER_1",
        operational_maturity="LIVE_OPERATIONAL",
        scope_statement="Active Fast2SMS and Twilio REST integration with delivery audit receipts.",
    ),
    FeatureMaturityItem(
        item_number=2,
        name="Nearest-Safe-Haven & Dynamic Route Recomputation",
        tier="TIER_1",
        operational_maturity="LIVE_OPERATIONAL",
        scope_statement="A* NetworkX highway graph with blocked-edge bypass embedded in SMS payload.",
    ),
    FeatureMaturityItem(
        item_number=3,
        name="Village-Proximity Escalation & Lifeline Isolation Flagging",
        tier="TIER_1",
        operational_maturity="LIVE_OPERATIONAL",
        scope_statement="Downslope topographic vector + graph reachability; isolates uninhabited slips from settlements.",
    ),
    # Tier 2 — High-Impact Differentiators
    FeatureMaturityItem(
        item_number=4,
        name="Alert Calibration & Historical Track-Record Engine",
        tier="TIER_2",
        operational_maturity="LIVE_OPERATIONAL",
        scope_statement="Confusion matrix, Brier score, and Lead-Time benchmark against 2021 Chamoli replay.",
    ),
    FeatureMaturityItem(
        item_number=5,
        name="OASIS CAP v1.2 Compliant Alert Schema",
        tier="TIER_2",
        operational_maturity="LIVE_OPERATIONAL",
        scope_statement="Full XML serialization matching NDMA SACHET disaster protocol.",
    ),
    FeatureMaturityItem(
        item_number=6,
        name="Cascading Catchment Hazard Modeling",
        tier="TIER_2",
        operational_maturity="LIVE_OPERATIONAL",
        scope_statement="Hydraulic surge propagation with exponential attenuation (decay lambda = 0.08/hr).",
    ),
    FeatureMaturityItem(
        item_number=7,
        name="Economic & Critical Infrastructure Exposure Weighting",
        tier="TIER_2",
        operational_maturity="LIVE_OPERATIONAL",
        scope_statement="Intersecting bridges, substations, schools, and hospitals from OpenStreetMap / NIC layers.",
    ),
    FeatureMaturityItem(
        item_number=8,
        name="GPM IMERG Satellite Rainfall Gap-Fill",
        tier="TIER_2",
        operational_maturity="LIVE_OPERATIONAL",
        scope_statement="0.1 deg NASA precipitation grid auto-calibrated to ground AWS stations.",
    ),
    FeatureMaturityItem(
        item_number=9,
        name="SHAP Localized Explainability & Hindi/Garhwali Templates",
        tier="TIER_2",
        operational_maturity="LIVE_OPERATIONAL",
        scope_statement="TreeExplainer computing exact mathematical feature attributions with localized strings.",
    ),
    FeatureMaturityItem(
        item_number=10,
        name="WhatsApp Multi-Channel Emergency Dispatch",
        tier="TIER_2",
        operational_maturity="LIVE_OPERATIONAL",
        scope_statement="Twilio WhatsApp Sandbox REST gateway with structured evacuation cards.",
    ),
    FeatureMaturityItem(
        item_number=11,
        name="Automated Glacial Lake (GLOF) Area Expansion Monitoring",
        tier="TIER_2",
        operational_maturity="LIVE_OPERATIONAL",
        scope_statement="10m Sentinel-2 NDWI multi-temporal expansion rate over 4 named high-risk tarns; cloud fail-visibly.",
    ),
    FeatureMaturityItem(
        item_number=12,
        name="System Limitations & Operational Scope Panel",
        tier="TIER_2",
        operational_maturity="LIVE_OPERATIONAL",
        scope_statement="Visible dashboard panel and public API exposing exact coverage boundaries and source latencies.",
    ),
    # Tier 3 — Physical & Prototype Demonstrators
    FeatureMaturityItem(
        item_number=13,
        name="Bluetooth / Mesh Offline One-Hop Rebroadcast",
        tier="TIER_3",
        operational_maturity="PROTOTYPE_SCOPE",
        scope_statement="BLE broadcast beacon payload for zero-cellular relay between peer smartphones.",
    ),
    FeatureMaturityItem(
        item_number=14,
        name="Physical Siren / Relay Trigger (ESP32)",
        tier="TIER_3",
        operational_maturity="PROTOTYPE_SCOPE",
        scope_statement="Hardware HTTP webhook firing GPIO relay on ESP32 microcontroller with piezoelectric buzzer.",
    ),
    FeatureMaturityItem(
        item_number=15,
        name="Simulated Edge-AI Geotechnical Sensor Node",
        tier="TIER_3",
        operational_maturity="PROTOTYPE_SCOPE",
        scope_statement="Sub-second pore pressure and tilt anomaly detector running lightweight decision logic.",
    ),
    FeatureMaturityItem(
        item_number=16,
        name="Generative AI Incident Commander Assistant",
        tier="TIER_3",
        operational_maturity="PROTOTYPE_SCOPE",
        scope_statement="Context-grounded operational briefing generator synthesizing catchment metrics into SDRF actions.",
    ),
    FeatureMaturityItem(
        item_number=17,
        name="Sentinel-1 InSAR Coherence Precursor Tracking (Pilot Slopes)",
        tier="TIER_3",
        operational_maturity="PROTOTYPE_SCOPE",
        scope_statement="Millimeter creep detection over 3 named pilot slopes (Joshimath, Kedarnath, Raini). Narrow pilot scope only.",
    ),
    # Tier 4 — Strategic Roadmap Only
    FeatureMaturityItem(
        item_number=18,
        name="Community LoRa Sensor Ingestion Mesh",
        tier="TIER_4",
        operational_maturity="ROADMAP_DESIGN_ONLY",
        scope_statement="865-867 MHz ISM Sub-GHz community rain gauges. Ingestion schema published in /docs/roadmap.md.",
    ),
    FeatureMaturityItem(
        item_number=19,
        name="Offline-First Progressive Web App (PWA) for DDMA",
        tier="TIER_4",
        operational_maturity="ROADMAP_DESIGN_ONLY",
        scope_statement="Local vector tile caching & IndexedDB synchronization for isolated district emergency operations.",
    ),
    FeatureMaturityItem(
        item_number=20,
        name="Automated Voice / IVR Fallback Calling",
        tier="TIER_4",
        operational_maturity="ROADMAP_DESIGN_ONLY",
        scope_statement="Outbound telephony calls synthesized in Garhwali and Kumaoni dialects with DTMF confirmation.",
    ),
    FeatureMaturityItem(
        item_number=21,
        name="Post-Event Drone Orthomosaic Ingestion Hook",
        tier="TIER_4",
        operational_maturity="ROADMAP_DESIGN_ONLY",
        scope_statement="API endpoint for SDRF quadcopter GeoTIFF rapid dam-breach photogrammetry.",
    ),
    FeatureMaturityItem(
        item_number=22,
        name="Structured Inter-Agency Handoff (EDXL-DE / Army / ITBP)",
        tier="TIER_4",
        operational_maturity="ROADMAP_DESIGN_ONLY",
        scope_statement="Tactical situational push to military cantonments with designated helicopter landing coordinates.",
    ),
    FeatureMaturityItem(
        item_number=23,
        name="3D Tactical Command Visualization (CesiumJS / Deck.gl)",
        tier="TIER_4",
        operational_maturity="ROADMAP_DESIGN_ONLY",
        scope_statement="Volumetric 3D flood canyon simulation using Cartosat 30m DEM elevation meshes.",
    ),
    FeatureMaturityItem(
        item_number=24,
        name="State-Wide Real-Time InSAR Coherence Monitoring",
        tier="TIER_4",
        operational_maturity="ROADMAP_DESIGN_ONLY",
        scope_statement="Continuous state-wide interferogram unwrapping across 53,483 km² of rugged Himalayan terrain; compute-cost prohibitive for live hackathon feed.",
    ),
]


DATA_LATENCY_CATALOG: List[DataLatencySpecification] = [
    DataLatencySpecification(
        source_name="SMS Alert Dispatch (Fast2SMS / Twilio)",
        provider="Commercial Cellular Gateway",
        update_cadence="Event-driven (sub-second trigger)",
        typical_latency="5 to 45 seconds (subject to telecom tower congestion)",
        operational_implication="Delivery confirmation receipts logged; not guaranteed during total cell-tower blackout.",
    ),
    DataLatencySpecification(
        source_name="Sentinel-1 SAR Radar Imagery (InSAR Coherence)",
        provider="Copernicus / ESA / ASF Vertex",
        update_cadence="6 to 12 days per orbital track",
        typical_latency="12 to 24 hours from satellite acquisition to processed interferogram",
        operational_implication="Slow ground creep precursor tool only. Cannot detect cloudburst flash floods in real-time.",
    ),
    DataLatencySpecification(
        source_name="Sentinel-2 Optical Multispectral (GLOF NDWI)",
        provider="Copernicus Open Access Hub",
        update_cadence="5 days (Sentinel-2A & 2B combined)",
        typical_latency="4 to 8 hours post-pass (contingent on <30% cloud cover)",
        operational_implication="Zero optical visibility during heavy monsoon cloud cover; triggers visible observation gap.",
    ),
    DataLatencySpecification(
        source_name="GPM IMERG Early Precipitation Estimates",
        provider="NASA Earth Observing System",
        update_cadence="Every 30 minutes",
        typical_latency="~4 hours from observation to public gridded product",
        operational_implication="Coarse 0.1° resolution (~10 km); used for regional gap-fill, not micro-ridge cloudbursts.",
    ),
    DataLatencySpecification(
        source_name="IMD Automatic Weather Station (AWS) Grid",
        provider="India Meteorological Department",
        update_cadence="Hourly observational telemetry",
        typical_latency="15 to 45 minutes reporting lag",
        operational_implication="Ground-truth baseline; subject to occasional telemetry dropouts during extreme weather.",
    ),
    DataLatencySpecification(
        source_name="CWC River Stage Telemetry",
        provider="Central Water Commission",
        update_cadence="15-minute sensor ping during monsoon season",
        typical_latency="10 to 20 minutes ingestion lag",
        operational_implication="Primary metric for rate-of-rise (ΔH/Δt); sensor destruction during debris flows stops reporting.",
    ),
    DataLatencySpecification(
        source_name="Char Dham Yatra Registration & Transient Population Load (Task 6.2)",
        provider="Uttarakhand Tourism Development Board (UTDB) & Devasthanam Board",
        update_cadence="Daily portal refresh / Season baseline multiplier (demo-mode fallback)",
        typical_latency="6 to 24 hours portal aggregation lag",
        operational_implication="Replaces fabricated cellular tower simulations. Dynamic load augments baseline provisioning and is capped at MAX_LOAD_MULTIPLIER = 4.5.",
    ),
    DataLatencySpecification(
        source_name="Offline Field Mesh Relay Synchronization (Section 3.12 / 6.3)",
        provider="SDRF Bluetooth Relay / Citizen Mesh Handheld",
        update_cadence="Opportunistic upon physical device connectivity restoration",
        typical_latency="1 to 6 hours field relay transit lag",
        operational_implication="Field device clocks may drift during network blackouts; records timestamped >2h ahead are flagged CLOCK_DRIFT_SUSPECT; latest timestamp wins.",
    ),
]


class SystemLimitationsService:
    """
    Central service providing authoritative system limitations and boundaries.
    """

    @staticmethod
    def get_limitations_report() -> SystemLimitationsReport:
        return SystemLimitationsReport(
            system_name="AI Mountain Disaster Early-Warning Intelligence Platform (Uttarakhand)",
            specification="UKIS Problem Statement P-011 / Addendum v2 Section 3.17",
            published_at=datetime.now(timezone.utc),
            probabilistic_disclaimer=(
                "LEGAL & OPERATIONAL DISCLAIMER: All hazard risk scores, cascading flood arrival times, "
                "and evacuation route recommendations generated by this platform are probabilistic computational estimates "
                "intended strictly for decision support by certified emergency managers (SDMA/DDMA/SDRF). "
                "They DO NOT constitute guarantees of safety and are NOT a replacement for official warning bulletins "
                "issued by the India Meteorological Department (IMD), National Disaster Management Authority (NDMA), "
                "or the Central Water Commission (CWC). Final emergency response actions rest with incident commanders."
            ),
            what_this_system_does_not_claim=[
                "Does NOT claim state-wide real-time InSAR slope monitoring (Sentinel-1 coherence is strictly prototype-scoped to 3 pilot slopes).",
                "Does NOT claim real-time optical lake monitoring during monsoonal cloud overcast (optical NDWI fails visibly when cloud cover > 30%).",
                "Does NOT claim instantaneous satellite rainfall (NASA GPM IMERG has a 4-hour product latency and 0.1° coarse resolution).",
                "Does NOT claim guaranteed public SMS delivery during fiber cuts or cellular tower power collapse (voice/satellite fallback is Tier 4).",
                "Does NOT claim deterministic certainty for slope failures (all outputs express calibrated probabilities with SHAP feature attributions).",
                "Does NOT claim simulated cell-tower tracking for population surges (dynamic load relies strictly on published Char Dham Yatra registration figures and cited seasonal multipliers, capped at 4.5x).",
                "Does NOT claim authoritative absolute timestamps for offline mesh reports without clock drift disclosure (field devices offline without NTP sync may exhibit RTC drift; reports timestamped >2h ahead are flagged CLOCK_DRIFT_SUSPECT).",
            ],
            watershed_coverage_matrix=WATERSHED_COVERAGE_CATALOG,
            feature_maturity_tiers=FEATURE_MATURITY_REGISTRY,
            data_latency_matrix=DATA_LATENCY_CATALOG,
            honest_hackathon_positioning=(
                "CORE POSITIONING: Explainability + Real Authoritative Data + Actionable Output + Honest Limitations. "
                "We do not promise technology we did not stand up. Every feature is tier-labeled honestly, "
                "and every gap is surfaced directly on the UI."
            ),
        )


# Global Singleton
system_limitations_service = SystemLimitationsService()
