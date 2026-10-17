"""
Compressed Offline State Synchronization Service (Bluetooth Mesh Relay).
UKIS Task 6 (Hardened) Section 6.3.

Ingests field-collected status updates forwarded over one-hop Bluetooth mesh (Section 3.12)
when connectivity is restored.

Pipeline:
1. Base64 Decode + Gzip Decompression of field-compressed telemetry payload.
2. Strict Schema Validation (rejects malformed records with explicit validation errors).
3. Clock-Drift Anomaly Detection (sanity checks packet timestamps vs. server time).
4. Conflict-Resolution Upsert: updates only when incoming report_timestamp > existing.
5. In-Memory & Database Persistence with side-by-side report_timestamp vs. synced_at.
"""

from __future__ import annotations

import base64
import gzip
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)

# Maximum plausible future clock drift (2 hours) before flagging CLOCK_DRIFT_SUSPECT
MAX_FUTURE_CLOCK_DRIFT_HOURS = 2.0


class MeshPacketInput(BaseModel):
    device_id: str = Field(..., min_length=3, description="Originating/Relay field device identifier")
    payload: str = Field(..., description="Base64-encoded, gzip-compressed JSON array")
    packet_timestamp: str = Field(..., description="ISO8601 timestamp set by field device at compression time")


class CitizenStatusRecord(BaseModel):
    village_id: str = Field(..., min_length=1)
    status_code: str = Field(..., min_length=1)  # e.g., 'ROAD_CUT', 'MEDICAL_EMERGENCY', 'SAFE'
    status_code_category: str = Field(default="GENERAL")
    timestamp: str = Field(..., min_length=1)
    field_notes: Optional[str] = None

    @field_validator("village_id", "status_code", "timestamp")
    @classmethod
    def check_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be blank")
        return v.strip()


class SyncedStatusReport(BaseModel):
    id: str
    village_id: str
    status_code: str
    status_code_category: str
    report_timestamp: str  # When field device created it
    device_id: str
    synced_at: str  # When central server received it
    sync_lag_seconds: float
    is_offline_origin: bool
    is_clock_drift_suspect: bool
    field_notes: Optional[str] = None


class MeshSyncResult(BaseModel):
    status: str  # 'SUCCESS' | 'PARTIAL_SUCCESS' | 'VALIDATION_FAILED'
    device_id: str
    packet_timestamp: str
    server_receipt_timestamp: str
    total_records_in_packet: int
    successfully_synced_count: int
    rejected_count: int
    is_clock_drift_detected: bool
    synced_reports: List[SyncedStatusReport]
    validation_errors: List[str]
    engineering_notes: str


class MeshSyncService:
    """
    Handles decompression, validation, and conflict resolution for offline field packets.
    """

    def __init__(self):
        # In-memory store keyed by (village_id, status_code_category) for resilience
        self._in_memory_reports: Dict[Tuple[str, str], SyncedStatusReport] = {}
        self._seed_initial_demo_reports()

    def _seed_initial_demo_reports(self):
        """Pre-populates sample offline reports for dashboard visualization."""
        t_base = datetime.now(timezone.utc) - timedelta(hours=3, minutes=15)
        t_sync = datetime.now(timezone.utc) - timedelta(minutes=12)

        demo_report = SyncedStatusReport(
            id="RELAY-CHAMOLI-001",
            village_id="UK_VIL_RAINI",
            status_code="ROAD_CUT",
            status_code_category="INFRASTRUCTURE",
            report_timestamp=t_base.isoformat(),
            device_id="SDRF-MESH-RELAY-04",
            synced_at=t_sync.isoformat(),
            sync_lag_seconds=round((t_sync - t_base).total_seconds(), 1),
            is_offline_origin=True,
            is_clock_drift_suspect=False,
            field_notes="Rishiganga bridge approach washed out. 18 households cut off.",
        )
        self._in_memory_reports[("UK_VIL_RAINI", "INFRASTRUCTURE")] = demo_report

    @staticmethod
    def decode_mesh_packet(payload_b64: str) -> List[Dict[str, Any]]:
        """
        Decompresses base64-encoded, gzip-compressed JSON payload.
        Strictly validates format and throws explicit ValueError on corruption.
        """
        try:
            compressed = base64.b64decode(payload_b64, validate=True)
        except Exception as err:
            raise ValueError(f"Invalid Base64 encoding in mesh packet: {err}") from err

        try:
            raw_json = gzip.decompress(compressed)
        except Exception as err:
            raise ValueError(f"Failed to decompress gzip stream in mesh packet: {err}") from err

        try:
            records = json.loads(raw_json.decode("utf-8"))
        except Exception as err:
            raise ValueError(f"Decompressed stream is not valid JSON: {err}") from err

        if not isinstance(records, list):
            raise ValueError(f"Expected JSON array of records, received {type(records).__name__}")

        return records

    @staticmethod
    def create_sample_mesh_packet(
        device_id: str,
        records: List[Dict[str, Any]],
        packet_timestamp: Optional[Any] = None,
        packet_timestamp_iso: Optional[str] = None,
    ) -> MeshPacketInput:
        """
        Helper for testing and Bluetooth relay demo:
        Compresses JSON array into base64 gzip payload.
        """
        if packet_timestamp_iso:
            p_time = packet_timestamp_iso
        elif isinstance(packet_timestamp, datetime):
            p_time = packet_timestamp.isoformat()
        elif isinstance(packet_timestamp, str):
            p_time = packet_timestamp
        else:
            p_time = datetime.now(timezone.utc).isoformat()

        raw_bytes = json.dumps(records).encode("utf-8")
        compressed_bytes = gzip.compress(raw_bytes)
        b64_str = base64.b64encode(compressed_bytes).decode("ascii")

        return MeshPacketInput(
            device_id=device_id,
            payload=b64_str,
            packet_timestamp=p_time,
        )

    def process_mesh_packet(self, packet: Any) -> MeshSyncResult:
        """
        End-to-end ingest: decodes, validates, resolves timestamp conflicts, and persists.
        """
        if isinstance(packet, dict):
            packet = MeshPacketInput(**packet)

        server_now = datetime.now(timezone.utc)
        validation_errors: List[str] = []
        synced_reports: List[SyncedStatusReport] = []

        # 1. Sanity check packet timestamp for severe future clock drift
        is_clock_drift = False
        try:
            p_dt = datetime.fromisoformat(packet.packet_timestamp.replace("Z", "+00:00"))
            if p_dt > server_now + timedelta(hours=MAX_FUTURE_CLOCK_DRIFT_HOURS):
                is_clock_drift = True
                validation_errors.append(
                    f"CLOCK_DRIFT_SUSPECT: Device packet timestamp ({packet.packet_timestamp}) "
                    f"is > {MAX_FUTURE_CLOCK_DRIFT_HOURS} hours ahead of server time."
                )
        except Exception:
            is_clock_drift = True
            validation_errors.append("Invalid ISO8601 packet_timestamp format.")

        # 2. Decompress packet
        try:
            raw_records = self.decode_mesh_packet(packet.payload)
        except ValueError as decode_err:
            return MeshSyncResult(
                status="VALIDATION_FAILED",
                device_id=packet.device_id,
                packet_timestamp=packet.packet_timestamp,
                server_receipt_timestamp=server_now.isoformat(),
                total_records_in_packet=0,
                successfully_synced_count=0,
                rejected_count=0,
                is_clock_drift_detected=is_clock_drift,
                synced_reports=[],
                validation_errors=[str(decode_err)],
                engineering_notes="Packet decompression failed. Verify base64 and gzip compression format.",
            )

        # 3. Process and strictly validate each record
        rejected_count = 0
        for idx, rec in enumerate(raw_records):
            try:
                validated = CitizenStatusRecord(**rec)
            except Exception as val_err:
                rejected_count += 1
                validation_errors.append(f"Record #{idx} validation error: {val_err}")
                continue

            # Parse report timestamp
            try:
                r_dt = datetime.fromisoformat(validated.timestamp.replace("Z", "+00:00"))
            except Exception:
                rejected_count += 1
                validation_errors.append(f"Record #{idx} has invalid timestamp: {validated.timestamp}")
                continue

            # Infer category if default
            cat = validated.status_code_category
            if cat == "GENERAL":
                if "MEDIC" in validated.status_code:
                    cat = "HEALTH"
                elif "ROAD" in validated.status_code or "BRIDGE" in validated.status_code:
                    cat = "INFRASTRUCTURE"
                elif "RATION" in validated.status_code or "WATER" in validated.status_code:
                    cat = "LOGISTICS"
                else:
                    cat = "CIVILIAN_SAFETY"

            key = (validated.village_id, cat)
            existing = self._in_memory_reports.get(key)

            # Conflict resolution: update only if incoming report_timestamp > existing
            if existing:
                try:
                    ex_dt = datetime.fromisoformat(existing.report_timestamp.replace("Z", "+00:00"))
                    if r_dt <= ex_dt:
                        # Existing report is newer or identical; discard stale record
                        logger.info(
                            "Discarding stale status report for %s: incoming %s <= existing %s",
                            key, validated.timestamp, existing.report_timestamp
                        )
                        continue
                except Exception:
                    pass

            lag_sec = max(0.0, round((server_now - r_dt).total_seconds(), 1))
            import uuid
            report_obj = SyncedStatusReport(
                id=f"SYNC-{uuid.uuid4().hex[:8].upper()}",
                village_id=validated.village_id,
                status_code=validated.status_code,
                status_code_category=cat,
                report_timestamp=validated.timestamp,
                device_id=packet.device_id,
                synced_at=server_now.isoformat(),
                sync_lag_seconds=lag_sec,
                is_offline_origin=True,
                is_clock_drift_suspect=is_clock_drift,
                field_notes=validated.field_notes or f"Offline relay report from {packet.device_id}",
            )

            # Persist in memory
            self._in_memory_reports[key] = report_obj
            synced_reports.append(report_obj)

        status_result = "SUCCESS" if rejected_count == 0 else "PARTIAL_SUCCESS" if synced_reports else "VALIDATION_FAILED"

        return MeshSyncResult(
            status=status_result,
            device_id=packet.device_id,
            packet_timestamp=packet.packet_timestamp,
            server_receipt_timestamp=server_now.isoformat(),
            total_records_in_packet=len(raw_records),
            successfully_synced_count=len(synced_reports),
            rejected_count=rejected_count,
            is_clock_drift_detected=is_clock_drift,
            synced_reports=synced_reports,
            validation_errors=validation_errors,
            engineering_notes=(
                f"Ingested {len(synced_reports)} valid records via Bluetooth mesh synchronization. "
                f"Conflict resolution: latest field timestamp wins. Offline origin flag preserved."
            ),
        )

    def list_recent_synced_reports(self, limit: int = 50) -> List[SyncedStatusReport]:
        """Returns recent synchronized offline status reports sorted by synced_at descending."""
        reports = list(self._in_memory_reports.values())
        reports.sort(key=lambda r: r.synced_at, reverse=True)
        return reports[:limit]


# Global Singleton
mesh_sync_service = MeshSyncService()
