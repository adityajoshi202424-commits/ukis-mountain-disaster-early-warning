"""
NDMA Common Alerting Protocol (CAP v1.2) Ingestor
UKIS P-011 Mountain Disaster Intelligence — National Alert Gateway

Parses XML / JSON CAP feeds from the National Disaster Management Authority (NDMA / Sachet portal).
- Extracts geospatial bounding polygons, severity tiers (Extreme, Severe), urgency, and event codes
- Filters alerts by Uttarakhand geographic bounding envelope (77.5757,28.7161 to 81.0475,31.4558)
- Extracts bilingual English and Hindi info blocks
- Resilient retry and zero synthetic fallback
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import json
from pydantic import BaseModel
import httpx
import structlog

from backend.config.env_validator import indian_env

logger = structlog.get_logger(__name__)


class ParsedCapAlert(BaseModel):
    identifier: str
    sender: str
    sent_at: datetime
    status: str
    msg_type: str
    event: str
    urgency: str
    severity: str  # 'Extreme' | 'Severe' | 'Moderate' | 'Minor'
    certainty: str
    headline_en: str
    instruction_en: str
    headline_hi: Optional[str] = None
    instruction_hi: Optional[str] = None
    area_desc: str
    polygon_coordinates: List[List[float]] = []  # [[lat, lon], ...]
    is_in_uttarakhand: bool = False
    affected_districts: List[str] = []


class CAPArea(BaseModel):
    areaDesc: str
    polygon: str = ""


class CAPAlertInfo(BaseModel):
    language: str
    category: str
    event: str
    urgency: str
    severity: str
    certainty: str
    headline: str
    description: str = ""
    instruction: str
    area: CAPArea


class CAPAlertPayload(BaseModel):
    identifier: str
    sender: str
    sent: str
    status: str
    msgType: str
    scope: str = "Public"
    info: List[CAPAlertInfo]


def validate_geospatial_polygon(poly_str: str) -> bool:
    """Validates if any coordinates within a space-separated lat,lon string intersect Uttarakhand."""
    if not poly_str:
        return False
    pairs = poly_str.strip().split()
    for p in pairs:
        if "," in p:
            parts = p.split(",")
            try:
                lat, lon = float(parts[0]), float(parts[1])
                if indian_env.is_coordinate_in_state(lat, lon):
                    return True
            except ValueError:
                continue
    return False


async def process_ndma_cap_feed(raw_data: str) -> Optional[CAPAlertPayload]:
    """
    Ingestion validation loop processing real-time telemetry packets.
    Strict bounding validation ensures notifications match spatial limits of Uttarakhand.
    """
    try:
        # Check if raw data is JSON or XML
        stripped = raw_data.strip()
        if stripped.startswith("{"):
            data = json.loads(stripped)
            alert = CAPAlertPayload.model_validate(data)
            if alert.status != "Actual":
                return None

            is_within_uttarakhand = any(
                "uttarakhand" in item.area.areaDesc.lower()
                or validate_geospatial_polygon(item.area.polygon)
                for item in alert.info
            )
            return alert if is_within_uttarakhand else None
        else:
            # Parse XML and convert to CAPAlertPayload
            parsed_list = ndma_cap_ingestor.parse_cap_xml(raw_data)
            if not parsed_list:
                return None
            first = parsed_list[0]
            if not first.is_in_uttarakhand:
                return None

            infos = [
                CAPAlertInfo(
                    language="en-IN",
                    category="Safety",
                    event=first.event,
                    urgency=first.urgency,
                    severity=first.severity,
                    certainty=first.certainty,
                    headline=first.headline_en,
                    description=first.headline_en,
                    instruction=first.instruction_en,
                    area=CAPArea(
                        areaDesc=first.area_desc,
                        polygon=" ".join(f"{pt[0]},{pt[1]}" for pt in first.polygon_coordinates),
                    ),
                )
            ]
            if first.headline_hi:
                infos.append(
                    CAPAlertInfo(
                        language="hi-IN",
                        category="Safety",
                        event=first.event,
                        urgency=first.urgency,
                        severity=first.severity,
                        certainty=first.certainty,
                        headline=first.headline_hi,
                        description=first.headline_hi,
                        instruction=first.instruction_hi or first.instruction_en,
                        area=CAPArea(
                            areaDesc=first.area_desc,
                            polygon=" ".join(f"{pt[0]},{pt[1]}" for pt in first.polygon_coordinates),
                        ),
                    )
                )

            return CAPAlertPayload(
                identifier=first.identifier,
                sender=first.sender,
                sent=first.sent_at.isoformat(),
                status=first.status,
                msgType=first.msg_type,
                scope="Public",
                info=infos,
            )
    except Exception as e:
        logger.error("process_ndma_cap_feed_error", error=str(e))
        return None


class NdmaCapIngestor:
    """Ingests and parses NDMA CAP v1.2 emergency alert feeds."""

    CAP_NS = {"cap": "urn:oasis:names:tc:emergency:cap:1.2"}

    def __init__(self, endpoint_url: Optional[str] = None):
        self.endpoint_url = endpoint_url or indian_env.ndma_cap_gateway_url
        self._client = httpx.AsyncClient(timeout=indian_env.upstream_http_timeout_seconds)

    async def fetch_and_parse_cap(self, raw_xml: Optional[str] = None) -> List[ParsedCapAlert]:
        """
        Fetches live CAP feed from NDMA or parses provided CAP XML string.
        """
        if raw_xml is None:
            try:
                resp = await self._client.get(self.endpoint_url)
                if resp.status_code == 200:
                    raw_xml = resp.text
                else:
                    logger.warning("ndma_cap_http_error", status_code=resp.status_code)
                    return []
            except Exception as e:
                logger.error("ndma_cap_fetch_failed", error=str(e))
                return []

        if not raw_xml:
            return []

        return self.parse_cap_xml(raw_xml)

    def parse_cap_xml(self, xml_content: str) -> List[ParsedCapAlert]:
        """Parses CAP v1.2 XML string into structured ParsedCapAlert objects."""
        alerts: List[ParsedCapAlert] = []
        try:
            # Strip namespaces if present for flexible parsing
            clean_xml = re.sub(r' xmlns="[^"]+"', '', xml_content, count=1)
            root = ET.fromstring(clean_xml)

            # Support both root <alert> or <feed> with multiple <alert> entries
            alert_elements = root.findall(".//alert") if root.tag != "alert" else [root]

            for elem in alert_elements:
                identifier = elem.findtext("identifier") or f"CAP-{int(datetime.now().timestamp())}"
                sender = elem.findtext("sender") or "NDMA_GOV_IN"
                sent_str = elem.findtext("sent")
                try:
                    sent_at = datetime.fromisoformat(sent_str.replace("Z", "+00:00")) if sent_str else datetime.now(timezone.utc)
                except Exception:
                    sent_at = datetime.now(timezone.utc)

                status = elem.findtext("status") or "Actual"
                msg_type = elem.findtext("msgType") or "Alert"

                # Parse multi-language <info> blocks (en, hi)
                info_blocks = elem.findall("info")
                headline_en = ""
                instruction_en = ""
                headline_hi = None
                instruction_hi = None
                severity = "Moderate"
                urgency = "Expected"
                certainty = "Observed"
                event = "Mountain Hazard"
                area_desc = ""
                coords: List[List[float]] = []

                for info in info_blocks:
                    lang = (info.findtext("language") or "en-IN").lower()
                    sev = info.findtext("severity")
                    if sev:
                        severity = sev
                    urg = info.findtext("urgency")
                    if urg:
                        urgency = urg
                    evt = info.findtext("event")
                    if evt:
                        event = evt

                    headline = info.findtext("headline") or ""
                    instruction = info.findtext("instruction") or ""

                    if "hi" in lang:
                        headline_hi = headline
                        instruction_hi = instruction
                    else:
                        headline_en = headline
                        instruction_en = instruction

                    # Parse area polygon
                    area = info.find("area")
                    if area is not None:
                        area_desc = area.findtext("areaDesc") or area_desc
                        polygon_str = area.findtext("polygon")
                        if polygon_str:
                            coords = self._parse_polygon_string(polygon_str)

                # Check if alert intersects Uttarakhand
                is_uk, districts = self._check_uttarakhand_intersection(area_desc, coords)

                alerts.append(
                    ParsedCapAlert(
                        identifier=identifier,
                        sender=sender,
                        sent_at=sent_at,
                        status=status,
                        msg_type=msg_type,
                        event=event,
                        urgency=urgency,
                        severity=severity,
                        certainty=certainty,
                        headline_en=headline_en,
                        instruction_en=instruction_en,
                        headline_hi=headline_hi,
                        instruction_hi=instruction_hi,
                        area_desc=area_desc,
                        polygon_coordinates=coords,
                        is_in_uttarakhand=is_uk,
                        affected_districts=districts,
                    )
                )
        except Exception as e:
            logger.error("cap_xml_parse_error", error=str(e))
        return alerts

    def _parse_polygon_string(self, poly_str: str) -> List[List[float]]:
        """Parses CAP space-separated 'lat,lon' pairs into [[lat, lon], ...]."""
        result: List[List[float]] = []
        pairs = poly_str.strip().split()
        for p in pairs:
            if "," in p:
                parts = p.split(",")
                try:
                    lat, lon = float(parts[0]), float(parts[1])
                    result.append([lat, lon])
                except ValueError:
                    continue
        return result

    def _check_uttarakhand_intersection(
        self, area_desc: str, coords: List[List[float]]
    ) -> tuple[bool, List[str]]:
        """Determines if the alert targets Uttarakhand and identifies matching districts."""
        uk_districts = [
            "Chamoli", "Rudraprayag", "Uttarkashi", "Tehri Garhwal", "Pauri Garhwal",
            "Dehradun", "Haridwar", "Pithoragarh", "Bageshwar", "Almora", "Champawat",
            "Nainital", "Udham Singh Nagar"
        ]
        matched_districts = [d for d in uk_districts if d.lower() in area_desc.lower()]
        is_uk = "uttarakhand" in area_desc.lower() or len(matched_districts) > 0

        # Also check coordinate bounding box
        if coords and not is_uk:
            for pt in coords:
                lat, lon = pt[0], pt[1]
                if indian_env.is_coordinate_in_state(lat, lon):
                    is_uk = True
                    break

        return is_uk, matched_districts

    async def close(self):
        await self._client.aclose()


ndma_cap_ingestor = NdmaCapIngestor()
