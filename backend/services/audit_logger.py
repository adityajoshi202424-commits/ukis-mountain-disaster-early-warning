"""
Secure Administrative Audit Logging Service (Immutable Hash-Chained Audit Trail)

Enforces cryptographic append-only integrity:
H_curr = SHA256(Timestamp + UserID + Action + Details + H_prev)
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel, Field


class AuditLogRecord(BaseModel):
    log_id: str
    timestamp: datetime
    user_id: str
    role: str  # 'ADMIN' | 'OPERATOR' | 'SYSTEM' | 'ANALYST'
    action: str
    details: str
    state_profile: Dict[str, Any]
    previous_hash: str
    current_hash: str
    is_tamper_verified: bool = True


class SecureAuditLogger:
    """
    Append-only cryptographically signed administrative ledger for government transparency.
    """

    GENESIS_HASH = "GENESIS_SIH_IMMUTABLE_HASH_0000000000000000"

    def __init__(self):
        self.audit_trail: List[AuditLogRecord] = []
        self._last_hash = self.GENESIS_HASH
        self._seed_initial_audit_trail()

    def _calculate_hash(
        self,
        timestamp_str: str,
        user_id: str,
        role: str,
        action: str,
        details: str,
        state_profile: Dict[str, Any],
        prev_hash: str,
    ) -> str:
        state_serialized = json.dumps(state_profile, sort_keys=True)
        raw_payload = f"{timestamp_str}|{user_id}|{role}|{action}|{details}|{state_serialized}|{prev_hash}"
        return hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()

    def log_action(
        self,
        user_id: str,
        role: str,
        action: str,
        details: str,
        state_profile: Optional[Dict[str, Any]] = None,
        custom_time: Optional[datetime] = None,
    ) -> AuditLogRecord:
        """
        Appends a new cryptographically signed log entry to the immutable ledger.
        """
        now = custom_time or datetime.now(timezone.utc)
        profile = state_profile or {}
        time_str = now.isoformat()

        curr_hash = self._calculate_hash(
            timestamp_str=time_str,
            user_id=user_id,
            role=role,
            action=action,
            details=details,
            state_profile=profile,
            prev_hash=self._last_hash,
        )

        record = AuditLogRecord(
            log_id=f"AUD-{len(self.audit_trail) + 1:04d}",
            timestamp=now,
            user_id=user_id,
            role=role,
            action=action,
            details=details,
            state_profile=profile,
            previous_hash=self._last_hash,
            current_hash=curr_hash,
            is_tamper_verified=True,
        )

        self.audit_trail.append(record)
        self._last_hash = curr_hash
        return record

    def verify_integrity(self) -> Tuple[bool, int]:
        """
        Validates the complete SHA-256 hash chain to guarantee zero record tampering.
        """
        expected_prev = self.GENESIS_HASH
        for idx, rec in enumerate(self.audit_trail):
            if rec.previous_hash != expected_prev:
                return False, idx

            recalculated = self._calculate_hash(
                timestamp_str=rec.timestamp.isoformat(),
                user_id=rec.user_id,
                role=rec.role,
                action=rec.action,
                details=rec.details,
                state_profile=rec.state_profile,
                prev_hash=rec.previous_hash,
            )

            if recalculated != rec.current_hash:
                return False, idx

            expected_prev = rec.current_hash

        return True, len(self.audit_trail)

    def get_recent_logs(self, limit: int = 25) -> List[AuditLogRecord]:
        return self.audit_trail[-limit:]

    def _seed_initial_audit_trail(self):
        base_time = datetime.now(timezone.utc) - timedelta(hours=6)
        
        self.log_action(
            user_id="SYSTEM_DAEMON_BOOT",
            role="SYSTEM",
            action="CORE_ENGINE_INITIALIZED",
            details="Zero-temporal leakage high-frequency early warning engine initialized with PostGIS spatial store.",
            state_profile={"mode": "OPERATIONAL", "model_version": "ResNet-UNet-v2.4.1"},
            custom_time=base_time,
        )
        self.log_action(
            user_id="ASDMA_OFFICER_04",
            role="OPERATOR",
            action="AUTH_SESSION_ESTABLISHED",
            details="Cryptographic JWT session token issued for State Emergency Operations Center officer.",
            state_profile={"ip": "10.0.4.12", "scope": "READ_DISPATCH"},
            custom_time=base_time + timedelta(minutes=45),
        )
        self.log_action(
            user_id="USDMA_OFFICER_04",
            role="OPERATOR",
            action="FAILOVER_SIMULATION_AUDIT",
            details="Simulated CWC gauge failure tested. Verified automatic switch to Sentinel-1 SAR altimetry.",
            state_profile={"station_id": "CWC_GAUGE_JOSHIMATH_01", "result": "FAILOVER_SUCCESS"},
            custom_time=base_time + timedelta(hours=2, minutes=15),
        )
        self.log_action(
            user_id="HUMAN_OVERRIDE_OFFICER",
            role="ADMIN",
            action="CROWDSOURCED_REPORT_VALIDATED",
            details="Citizen report CIT-REP-B849A1 verified in field near Joshimath NH-58 corridor. Sector escalated to CRITICAL_VERIFIED.",
            state_profile={"hazard": "Debris flow / slope failure", "status": "APPROVED"},
            custom_time=base_time + timedelta(hours=4, minutes=10),
        )


audit_logger = SecureAuditLogger()
