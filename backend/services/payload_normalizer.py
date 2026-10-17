"""
Disaster Payload Normalization Engine
UKIS P-011 — Unified Standardized Alert Schema

Normalizes raw feeds from disparate Indian government agencies:
- NDMA Common Alerting Protocol (CAP)
- IMD Mausam Nowcast & Warnings
- Central Water Commission (CWC) Hydrological Gauges
- National Center for Seismology (NCS) Earthquake Feeds
- USDMA State Emergency Operation Centre Feeds

Outputs a unified, clean, predictable JSON payload format across all client apps.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from backend.services.indian_hazard_matrix import (
    indian_hazard_engine,
    HazardCategory,
    HazardSeverity,
    HazardDefinition,
)


class HazardHeader(BaseModel):
    type: str
    category: str
    icon: str


class AlertLocalization(BaseModel):
    state: str = "Uttarakhand"
    districts: List[str] = Field(default_factory=list)
    bounding_polygon: List[List[float]] = Field(default_factory=list)  # [[lat, lon], ...]


class LanguageContent(BaseModel):
    title: str
    instruction: str


class UnifiedDisasterAlertPayload(BaseModel):
    alert_id: str
    source: str
    timestamp: int  # epoch seconds
    hazard: HazardHeader
    severity: str   # 'CRITICAL' | 'ALERT' | 'WATCH' | 'NORMAL'
    localization: AlertLocalization
    content: Dict[str, LanguageContent]  # 'en', 'hi', 'gar', 'kum'
    nearest_shelter: Optional[Dict[str, Any]] = None
    cell_broadcast_code: Optional[str] = "IN_CAP_001"


class DisasterPayloadNormalizer:
    """Normalizes heterogeneous government disaster feeds into a unified schema."""

    @staticmethod
    def normalize_from_hazard(
        hazard_code: str,
        districts: List[str],
        source: str = "NDMA_CAP_GATEWAY",
        severity_override: Optional[str] = None,
        polygon: Optional[List[List[float]]] = None,
        custom_en_title: Optional[str] = None,
        custom_en_instruction: Optional[str] = None,
        nearest_shelter: Optional[Dict[str, Any]] = None,
    ) -> UnifiedDisasterAlertPayload:
        """Converts hazard definitions and telemetry into the unified payload structure."""
        hazard_def = indian_hazard_engine.get_hazard(hazard_code)
        if not hazard_def:
            hazard_def = indian_hazard_engine.get_hazard("FLASH_FLOOD_GLOF")

        now = datetime.now(timezone.utc)
        epoch_ts = int(now.timestamp())
        sev = severity_override or hazard_def.default_severity.value

        content_dict: Dict[str, LanguageContent] = {}
        for lang_key, text_obj in hazard_def.multilingual.items():
            title = custom_en_title if (lang_key == "en" and custom_en_title) else text_obj.title
            instruction = custom_en_instruction if (lang_key == "en" and custom_en_instruction) else text_obj.instruction
            content_dict[lang_key] = LanguageContent(title=title, instruction=instruction)

        # Default fallback polygon if none provided (Chamoli/Rudraprayag corridor)
        poly = polygon or [[30.55, 79.56], [30.73, 79.06], [30.41, 79.06]]

        return UnifiedDisasterAlertPayload(
            alert_id=f"IN-UK-{source[:4]}-{now.year}-{uuid.uuid4().hex[:4].upper()}",
            source=source,
            timestamp=epoch_ts,
            hazard=HazardHeader(
                type=hazard_def.hazard_code,
                category=hazard_def.category.value,
                icon=hazard_def.non_linguistic_icon,
            ),
            severity=sev,
            localization=AlertLocalization(
                state="Uttarakhand",
                districts=districts or ["Chamoli", "Rudraprayag"],
                bounding_polygon=poly,
            ),
            content=content_dict,
            nearest_shelter=nearest_shelter,
            cell_broadcast_code="IN_CAP_001",
        )

    @classmethod
    def normalize_from_cap(cls, cap_alert: Any) -> UnifiedDisasterAlertPayload:
        """Normalizes a ParsedCapAlert instance."""
        sev = "CRITICAL" if cap_alert.severity.upper() in ("EXTREME", "SEVERE", "CRITICAL") else "ALERT"
        hazard_code = "FLASH_FLOOD_GLOF"
        evt_lower = cap_alert.event.lower() + " " + cap_alert.headline_en.lower()
        if "landslide" in evt_lower:
            hazard_code = "LANDSLIDE_MUDSLIDE"
        elif "cloudburst" in evt_lower:
            hazard_code = "CLOUDBURST"
        elif "earthquake" in evt_lower:
            hazard_code = "EARTHQUAKE"
        elif "avalanche" in evt_lower or "snow" in evt_lower:
            hazard_code = "HEAVY_SNOWFALL_AVALANCHE"
        elif "fire" in evt_lower:
            hazard_code = "FOREST_FIRE"

        return cls.normalize_from_hazard(
            hazard_code=hazard_code,
            districts=cap_alert.affected_districts or ["Chamoli"],
            source=cap_alert.sender or "NDMA_CAP_GATEWAY",
            severity_override=sev,
            polygon=cap_alert.polygon_coordinates,
            custom_en_title=cap_alert.headline_en,
            custom_en_instruction=cap_alert.instruction_en,
        )


payload_normalizer = DisasterPayloadNormalizer()
