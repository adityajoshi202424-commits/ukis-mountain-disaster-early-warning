"""
Canonical CAP 1.2 & DMMC Disaster Early Warning Pydantic Schema.
Strict weather.gov/alerts functional feature parity adapted for Uttarakhand, India.
Shared type alignment with frontend/src/types/shared_cap.ts.
Includes Crowdsourced Hazard Reports, Citizen Mark-Safe Check-in, Shelter Live Occupancy,
and Admin Audit Logs.
"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional, Dict, Tuple, Any
from datetime import datetime
from pydantic import BaseModel, Field


class UttarakhandDistrict(str, Enum):
    DEHRADUN = "Dehradun"
    UTTARKASHI = "Uttarkashi"
    CHAMOLI = "Chamoli"
    RUDRAPRAYAG = "Rudraprayag"
    TEHRI_GARHWAL = "Tehri Garhwal"
    PAURI_GARHWAL = "Pauri Garhwal"
    PITHORAGARH = "Pithoragarh"
    BAGESHWAR = "Bageshwar"
    ALMORA = "Almora"
    CHAMPAWAT = "Champawat"
    NAINITAL = "Nainital"
    HARIDWAR = "Haridwar"
    UDHAM_SINGH_NAGAR = "Udham Singh Nagar"


class HimalayanHazardType(str, Enum):
    FLASH_FLOOD_GLOF = "FLASH_FLOOD_GLOF"
    LANDSLIDE_SLOPE_FAILURE = "LANDSLIDE_SLOPE_FAILURE"
    CLOUDBURST_SEVERE_STORM = "CLOUDBURST_SEVERE_STORM"
    EARTHQUAKE_SEISMIC = "EARTHQUAKE_SEISMIC"
    FOREST_FIRE = "FOREST_FIRE"
    AVALANCHE_SNOWFALL = "AVALANCHE_SNOWFALL"


class AlertSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    SEVERE = "SEVERE"
    ADVISORY = "ADVISORY"


class CapUrgency(str, Enum):
    IMMEDIATE = "Immediate"
    EXPECTED = "Expected"
    FUTURE = "Future"
    PAST = "Past"
    UNKNOWN = "Unknown"


class CapCertainty(str, Enum):
    OBSERVED = "Observed"
    LIKELY = "Likely"
    POSSIBLE = "Possible"
    UNLIKELY = "Unlikely"
    UNKNOWN = "Unknown"


class CapStatus(str, Enum):
    ACTUAL = "Actual"
    EXERCISE = "Exercise"
    SYSTEM = "System"
    TEST = "Test"
    DRAFT = "Draft"


class CapMsgType(str, Enum):
    ALERT = "Alert"
    UPDATE = "Update"
    CANCEL = "Cancel"
    ACK = "Ack"
    ERROR = "Error"


class SupportedLocale(str, Enum):
    EN_IN = "en-IN"
    HI_IN = "hi-IN"
    GBM_IN = "gbm-IN"
    KFY_IN = "kfy-IN"


class DeliveryChannelType(str, Enum):
    CELL_BROADCAST = "CELL_BROADCAST"
    SMS = "SMS"
    IVR_VOICE = "IVR_VOICE"
    WHATSAPP = "WHATSAPP"
    FCM_PUSH = "FCM_PUSH"


class CapArea(BaseModel):
    areaDesc: str
    polygon: Optional[List[Tuple[float, float]]] = None  # [(lat, lon), ...]
    circle: Optional[str] = None
    altitude: Optional[float] = None
    ceiling: Optional[float] = None


class LocalizedCapInfo(BaseModel):
    language: SupportedLocale
    headline: str
    description: str
    instruction: str
    senderName: str
    event: str


class CapAlertItem(BaseModel):
    identifier: str
    sender: str
    senderName: str
    sent: str  # ISO-8601
    status: CapStatus = CapStatus.ACTUAL
    msgType: CapMsgType = CapMsgType.ALERT
    scope: str = "Public"

    # Hazard Classification
    hazardType: HimalayanHazardType
    severity: AlertSeverity
    urgency: CapUrgency = CapUrgency.EXPECTED
    certainty: CapCertainty = CapCertainty.LIKELY

    # Geographic Scope
    districts: List[str]
    area: CapArea

    # Timestamps
    effective: str
    onset: Optional[str] = None
    expires: str
    ends: Optional[str] = None

    # Localized Content
    localized: Dict[str, LocalizedCapInfo] = Field(default_factory=dict)

    # Source & Telemetry Metadata
    sourceFeed: str  # NDMA_CAP, NDMA_SACHET, CWC_GAUGE, IMD_NOWCAST, IITR_EEW, FOREST_FIRE_TRACK, AVALANCHE_MONITOR, DMMC_SEOC_OVERRIDE
    sourceLastUpdated: str
    isFailClosedFallback: bool = False


class HazardFeedStatus(BaseModel):
    hazardType: HimalayanHazardType
    adapterName: str
    isConfigured: bool
    status: str  # ONLINE, DATA_UNAVAILABLE, ERROR, CIRCUIT_OPEN, STALE_WARNING
    lastChecked: str
    errorMessage: Optional[str] = None
    endpointMasked: Optional[str] = None
    latencyMs: Optional[float] = None
    isStale: bool = False


# Crowdsourced Citizen Hazard Report Models
class HazardReportStatus(str, Enum):
    UNVERIFIED = "UNVERIFIED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    MERGED = "MERGED"


class HazardReportCategory(str, Enum):
    ROAD_BLOCKED = "ROAD_BLOCKED"
    LANDSLIDE_OBSERVED = "LANDSLIDE_OBSERVED"
    RIVER_SURGE = "RIVER_SURGE"
    STRUCTURE_DAMAGE = "STRUCTURE_DAMAGE"
    SNOW_AVALANCHE_DRIFT = "SNOW_AVALANCHE_DRIFT"
    OTHER = "OTHER"


class CrowdsourcedHazardReport(BaseModel):
    report_id: str
    reporter_phone_hash: str
    district: str
    hazardType: HimalayanHazardType
    category: HazardReportCategory
    description: str
    photo_url: Optional[str] = None
    lat: float
    lon: float
    submitted_at: str
    status: HazardReportStatus = HazardReportStatus.UNVERIFIED
    verification_notes: Optional[str] = None
    verified_by: Optional[str] = None
    is_unverified: bool = True


# Citizen "Mark Safe" Check-In Models
class CitizenSafetyStatus(str, Enum):
    SAFE = "SAFE"
    NEEDS_ASSISTANCE = "NEEDS_ASSISTANCE"
    EVACUATED = "EVACUATED"


class CitizenCheckInRecord(BaseModel):
    checkin_id: str
    phone_hash: str
    status: CitizenSafetyStatus = CitizenSafetyStatus.SAFE
    district: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    message: Optional[str] = None
    timestamp: str
    linked_contacts: List[str] = Field(default_factory=list)


# Shelter Live Occupancy Models
class ShelterOccupancyItem(BaseModel):
    shelter_id: str
    name: str
    district: str
    elevation_m: float
    capacity: int
    current_occupancy: int
    is_live: bool = False
    last_updated: str
    helpline: str
    address: Optional[str] = None


# Admin Action Audit Trail Log
class AdminAuditRecord(BaseModel):
    audit_id: str
    action_type: str
    admin_user: str
    target_id: str
    details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str


def map_cap_severity(severity_str: str, urgency_str: str = "", certainty_str: str = "") -> AlertSeverity:
    """
    Maps standard CAP v1.2 severity/urgency/certainty to 3 DMMC Uttarakhand tiers:
    CRITICAL: Extreme + Immediate + Observed/Likely
    SEVERE: Severe / Extreme
    ADVISORY: Moderate / Minor / Advisory
    """
    sev = (severity_str or "").strip().lower()
    urg = (urgency_str or "").strip().lower()
    cer = (certainty_str or "").strip().lower()

    if sev == "extreme" or (urg == "immediate" and cer in ("observed", "likely")):
        return AlertSeverity.CRITICAL
    elif sev in ("severe", "high"):
        return AlertSeverity.SEVERE
    else:
        return AlertSeverity.ADVISORY
