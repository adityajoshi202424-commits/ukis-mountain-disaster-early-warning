"""
OASIS Common Alerting Protocol (CAP v1.2) XML Serialization Engine.

Standards Compliance:
- OASIS CAP v1.2 (urn:oasis:names:tc:emergency:cap:1.2)
- Standalone XML serialization using standard library `xml.etree.ElementTree`.
- Generates fully escaped, valid XML payloads containing:
  <alert>, <identifier>, <sender>, <sent>, <status>Actual</status>, <msgType>Alert</msgType>, <scope>Public</scope>,
  <info>: <category>, <event>, <urgency>Immediate</urgency>, <severity>Extreme</severity>, <certainty>,
          <headline>, <description>, <area><areaDesc>, <circle>.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, tostring

from pydantic import BaseModel, Field

CAP_NS = "urn:oasis:names:tc:emergency:cap:1.2"


class CAPAlertInput(BaseModel):
    sender: str = Field(default="usdma-alert-engine@uk.gov.in")
    headline: str
    description: str
    area_description: str
    latitude: float = Field(ge=28.72, le=31.46)
    longitude: float = Field(ge=77.57, le=81.04)
    radius_km: float = Field(default=5.0, ge=0.0)
    urgency: str = Field(default="Immediate")
    severity: str = Field(default="Extreme")  # 'Extreme' | 'Severe' | 'Moderate' | 'Minor'
    certainty: str = Field(default="Observed")  # 'Observed' | 'Likely' | 'Possible'
    status: str = Field(default="Actual")
    msg_type: str = Field(default="Alert")
    scope: str = Field(default="Public")
    identifier: Optional[str] = None
    event_type: str = Field(default="Uttarakhand Mountain Hazard")


class OASISCAPSerializer:
    """
    Standalone OASIS CAP v1.2 XML builder and parser.
    """

    @staticmethod
    def serialize_alert(
        sender: str = "usdma-alert-engine@uk.gov.in",
        headline: str = "Critical Mountain Hazard Alert",
        description: str = "Immediate evacuation warning for downslope settlements.",
        area_description: str = "Chamoli District, Joshimath - Mana Corridor",
        latitude: float = 30.5574,
        longitude: float = 79.5658,
        radius_km: float = 5.0,
        severity: str = "Extreme",
        urgency: str = "Immediate",
        certainty: str = "Observed",
        status: str = "Actual",
        msg_type: str = "Alert",
        scope: str = "Public",
        identifier: Optional[str] = None,
        event_type: str = "Uttarakhand Mountain Hazard",
    ) -> str:
        """
        Builds and serializes a fully valid OASIS CAP v1.2 XML string.
        """
        alert_id = identifier or f"UKIS-CAP-{uuid.uuid4()}"
        sent_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")

        root = Element("alert", {"xmlns": CAP_NS})

        # Core Header Elements
        SubElement(root, "identifier").text = alert_id
        SubElement(root, "sender").text = sender
        SubElement(root, "sent").text = sent_timestamp
        SubElement(root, "status").text = status
        SubElement(root, "msgType").text = msg_type
        SubElement(root, "scope").text = scope

        # Information Container Block
        info = SubElement(root, "info")
        SubElement(info, "category").text = "Geo"
        SubElement(info, "event").text = event_type
        SubElement(info, "urgency").text = urgency
        SubElement(info, "severity").text = severity
        SubElement(info, "certainty").text = certainty
        SubElement(info, "headline").text = headline
        SubElement(info, "description").text = description

        # Geographic Area Specification
        area = SubElement(info, "area")
        SubElement(area, "areaDesc").text = area_description
        # OASIS CAP format for circle: "latitude,longitude,radius_in_km"
        SubElement(area, "circle").text = f"{latitude:.5f},{longitude:.5f},{radius_km:.1f}"

        xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
        raw_xml = tostring(root, encoding="unicode")
        return xml_declaration + raw_xml

    @classmethod
    def serialize_from_model(cls, payload: Union[CAPAlertInput, Dict[str, Any]]) -> str:
        """Helper to serialize directly from Pydantic model or dictionary."""
        if isinstance(payload, dict):
            payload = CAPAlertInput(**payload)
        return cls.serialize_alert(
            sender=payload.sender,
            headline=payload.headline,
            description=payload.description,
            area_description=payload.area_description,
            latitude=payload.latitude,
            longitude=payload.longitude,
            radius_km=payload.radius_km,
            severity=payload.severity,
            urgency=payload.urgency,
            certainty=payload.certainty,
            status=payload.status,
            msg_type=payload.msg_type,
            scope=payload.scope,
            identifier=payload.identifier,
            event_type=payload.event_type,
        )

    @staticmethod
    def parse_cap_xml(xml_content: str) -> Dict[str, Any]:
        """
        Validates and parses a CAP v1.2 XML string into structured key-value elements.
        """
        # Strip xml declaration if present for parsing
        content = xml_content.strip()
        root = ET.fromstring(content)

        ns = {"cap": CAP_NS}
        identifier = root.findtext("cap:identifier", default="", namespaces=ns)
        sender = root.findtext("cap:sender", default="", namespaces=ns)
        status = root.findtext("cap:status", default="", namespaces=ns)
        msg_type = root.findtext("cap:msgType", default="", namespaces=ns)
        scope = root.findtext("cap:scope", default="", namespaces=ns)

        info = root.find("cap:info", namespaces=ns)
        headline = info.findtext("cap:headline", default="", namespaces=ns) if info is not None else ""
        description = info.findtext("cap:description", default="", namespaces=ns) if info is not None else ""
        urgency = info.findtext("cap:urgency", default="", namespaces=ns) if info is not None else ""
        severity = info.findtext("cap:severity", default="", namespaces=ns) if info is not None else ""

        area = info.find("cap:area", namespaces=ns) if info is not None else None
        area_desc = area.findtext("cap:areaDesc", default="", namespaces=ns) if area is not None else ""
        circle = area.findtext("cap:circle", default="", namespaces=ns) if area is not None else ""

        return {
            "identifier": identifier,
            "sender": sender,
            "status": status,
            "msgType": msg_type,
            "scope": scope,
            "headline": headline,
            "description": description,
            "urgency": urgency,
            "severity": severity,
            "areaDesc": area_desc,
            "circle": circle,
        }


# Backwards compatibility function wrapper
def serialize_cap_alert(
    *,
    sender: str,
    headline: str,
    description: str,
    area_description: str,
    latitude: float,
    longitude: float,
    severity: str = "Extreme",
    identifier: Optional[str] = None,
) -> str:
    return OASISCAPSerializer.serialize_alert(
        sender=sender,
        headline=headline,
        description=description,
        area_description=area_description,
        latitude=latitude,
        longitude=longitude,
        severity=severity,
        identifier=identifier,
    )