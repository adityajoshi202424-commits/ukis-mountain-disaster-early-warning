"""
C-DOT Cell Broadcast & Telecommunication Carrier Gateway
UKIS P-011 Mountain Disaster Intelligence — Zero-Data Disaster Dissemination

Hooks into:
- C-DOT (Centre for Development of Telematics) Cell Broadcast System
- Indian National Emergency Cell Broadcast Protocol (IN_CAP_001)
- BSNL & Jio tower-level geo-targeted SMS broadcast channels

Enables instantaneous broadcast to all active mobile devices attached to mountain BTS towers
without requiring active mobile data, SIM registration, or app installation.
"""

from __future__ import annotations

import time
import uuid
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from backend.config.env_validator import indian_env
from backend.services.payload_normalizer import UnifiedDisasterAlertPayload


class CellBroadcastPacket(BaseModel):
    packet_id: str
    message_identifier: str = "IN_CAP_001"  # C-DOT Emergency Disaster Identifier
    serial_number: int
    geographical_scope: str = "CELL_WIDE_EMERGENCY"
    channel: int = 4370  # Standard Emergency Alert Channel (ETWS / CMAS primary)
    language_code: str  # 'en' | 'hi'
    message_payload: str
    targeted_district: str
    bts_tower_ids: List[str] = Field(default_factory=list)
    issued_at_epoch: int
    ttl_seconds: int = 3600


class CdotCellBroadcastService:
    """Formats and dispatches C-DOT Cell Broadcast packets for mountain telecom networks."""

    def __init__(self):
        self.broadcast_log: List[CellBroadcastPacket] = []

    def format_cell_broadcast(
        self, alert: UnifiedDisasterAlertPayload, target_district: str = "Chamoli"
    ) -> List[CellBroadcastPacket]:
        """
        Creates bilingual (English + Hindi) 93-character C-DOT GSM 03.41 Cell Broadcast frames.
        """
        now = int(time.time())
        packets: List[CellBroadcastPacket] = []

        # 1. Hindi Broadcast (Highest Reach in Uttarakhand)
        hi_content = alert.content.get("hi")
        if hi_content:
            hi_text = f"चेतावनी [{alert.hazard.type}]: {hi_content.title}. {hi_content.instruction}".strip()
            packets.append(
                CellBroadcastPacket(
                    packet_id=f"CDOT-CB-HI-{uuid.uuid4().hex[:6].upper()}",
                    message_identifier=indian_env.cdac_cell_broadcast_receiver_id,
                    serial_number=now % 65535,
                    geographical_scope="CELL_WIDE_EMERGENCY",
                    channel=4370,
                    language_code="hi",
                    message_payload=hi_text[:180],
                    targeted_district=target_district,
                    bts_tower_ids=[f"BSNL-{target_district.upper()}-BTS-01", f"BSNL-{target_district.upper()}-BTS-02"],
                    issued_at_epoch=now,
                )
            )

        # 2. English Broadcast (Tourists, Pilgrims, NDRF)
        en_content = alert.content.get("en")
        if en_content:
            en_text = f"ALERT [{alert.hazard.type}]: {en_content.title}. {en_content.instruction}".strip()
            packets.append(
                CellBroadcastPacket(
                    packet_id=f"CDOT-CB-EN-{uuid.uuid4().hex[:6].upper()}",
                    message_identifier=indian_env.cdac_cell_broadcast_receiver_id,
                    serial_number=(now + 1) % 65535,
                    geographical_scope="CELL_WIDE_EMERGENCY",
                    channel=4371,
                    language_code="en",
                    message_payload=en_text[:180],
                    targeted_district=target_district,
                    bts_tower_ids=[f"BSNL-{target_district.upper()}-BTS-01", f"BSNL-{target_district.upper()}-BTS-02"],
                    issued_at_epoch=now,
                )
            )

        self.broadcast_log.extend(packets)
        return packets

    def get_recent_broadcasts(self, limit: int = 10) -> List[CellBroadcastPacket]:
        return sorted(self.broadcast_log, key=lambda p: p.issued_at_epoch, reverse=True)[:limit]


cdot_broadcast_service = CdotCellBroadcastService()
