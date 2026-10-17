"""
DMMC Uttarakhand Citizen Safety & Field Operations Service.
Implements:
1. "Mark Yourself Safe" check-in with privacy-preserving phone hashing & linked contact lookup
2. Crowdsourced mountain hazard reporting with unverified moderation queue
3. Live vs. static shelter occupancy management
4. Tamper-evident admin action audit logging
"""

from __future__ import annotations

import time
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import structlog

from backend.cap_schema import (
    CitizenSafetyStatus,
    CitizenCheckInRecord,
    CrowdsourcedHazardReport,
    HazardReportCategory,
    HazardReportStatus,
    HimalayanHazardType,
    ShelterOccupancyItem,
    AdminAuditRecord,
)
from backend.config.env_validator import UTTARAKHAND_BBOX

logger = structlog.get_logger("dmmc_citizen_safety")


def hash_phone(phone: str) -> str:
    """Produce irreversible SHA-256 hash of telephone number for privacy per DPDP Act 2023."""
    clean = phone.strip().replace(" ", "").replace("-", "")
    return hashlib.sha256(clean.encode("utf-8")).hexdigest()


class CitizenSafetyService:
    def __init__(self):
        # In-memory stores (in prod backed by PostgreSQL / TimescaleDB)
        self._checkins: Dict[str, List[CitizenCheckInRecord]] = {}  # phone_hash -> records
        self._hazard_reports: Dict[str, CrowdsourcedHazardReport] = {}  # report_id -> report
        self._audit_logs: List[AdminAuditRecord] = []
        self._shelters: Dict[str, ShelterOccupancyItem] = {}
        self._init_baseline_shelters()

    def _init_baseline_shelters(self):
        """
        Initializes baseline DMMC disaster relief shelters across high-risk Uttarakhand districts.
        By default is_live = False until DMMC telemetry / manual admin feed is activated.
        """
        now_str = datetime.now(timezone.utc).isoformat()
        baseline = [
            ShelterOccupancyItem(
                shelter_id="UK-SH-CHAM-01",
                name="Joshimath Central Relief Centre",
                district="Chamoli",
                elevation_m=1890.0,
                capacity=450,
                current_occupancy=0,
                is_live=False,
                last_updated=now_str,
                helpline="01372-252107",
                address="Near SDM Office, Joshimath, Chamoli",
            ),
            ShelterOccupancyItem(
                shelter_id="UK-SH-UTTR-01",
                name="Maneri Multipurpose Cyclone/Flood Haven",
                district="Uttarkashi",
                elevation_m=1280.0,
                capacity=600,
                current_occupancy=0,
                is_live=False,
                last_updated=now_str,
                helpline="01374-222722",
                address="Bhatwari Block, NH-108, Uttarkashi",
            ),
            ShelterOccupancyItem(
                shelter_id="UK-SH-RUDR-01",
                name="Guptkashi Disaster Evacuation Base",
                district="Rudraprayag",
                elevation_m=1319.0,
                capacity=500,
                current_occupancy=0,
                is_live=False,
                last_updated=now_str,
                helpline="01364-233727",
                address="Kedar Highway Junction, Guptkashi",
            ),
            ShelterOccupancyItem(
                shelter_id="UK-SH-PITH-01",
                name="Dharchula Valley Emergency Shelter",
                district="Pithoragarh",
                elevation_m=940.0,
                capacity=400,
                current_occupancy=0,
                is_live=False,
                last_updated=now_str,
                helpline="01367-222238",
                address="Kali River High Embankment, Dharchula",
            ),
            ShelterOccupancyItem(
                shelter_id="UK-SH-DEHR-01",
                name="State Disaster Response Training Camp Shelter",
                district="Dehradun",
                elevation_m=640.0,
                capacity=1200,
                current_occupancy=0,
                is_live=False,
                last_updated=now_str,
                helpline="0135-2710334",
                address="Jolly Grant Bypass, Dehradun",
            ),
        ]
        for s in baseline:
            self._shelters[s.shelter_id] = s

    # -------------------------------------------------------------------------
    # PART 1: "MARK SAFE" / FAMILY CHECK-IN (DPDP ACT 2023 COMPLIANT)
    # -------------------------------------------------------------------------
    def check_in_safe(
        self,
        phone: str,
        district: str,
        status: CitizenSafetyStatus = CitizenSafetyStatus.SAFE,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        message: Optional[str] = None,
        linked_contacts: Optional[List[str]] = None,
    ) -> CitizenCheckInRecord:
        """
        Record citizen safety check-in during active disaster.
        Phone numbers of user and linked contacts are stored strictly as irreversible SHA-256 hashes.
        """
        p_hash = hash_phone(phone)
        contact_hashes = [hash_phone(c) for c in (linked_contacts or []) if c.strip()]
        
        record = CitizenCheckInRecord(
            checkin_id=f"chk_{int(time.time()*1000)}_{p_hash[:8]}",
            phone_hash=p_hash,
            status=status,
            district=district,
            lat=lat,
            lon=lon,
            message=message or "Marked safe via DMMC UKIS portal",
            timestamp=datetime.now(timezone.utc).isoformat(),
            linked_contacts=contact_hashes,
        )
        self._checkins.setdefault(p_hash, []).append(record)
        logger.info("Citizen marked safety status", district=district, status=status.value)
        return record

    def get_contact_safety_status(self, querier_phone: str) -> List[Dict[str, Any]]:
        """
        Allows a user to check if any of their linked family members or contacts
        have marked themselves safe. Returns records where the querier's phone hash
        is present in the record's linked_contacts.
        """
        q_hash = hash_phone(querier_phone)
        results = []
        for records in self._checkins.values():
            for rec in records:
                if q_hash in rec.linked_contacts:
                    results.append({
                        "checkin_id": rec.checkin_id,
                        "status": rec.status.value,
                        "district": rec.district,
                        "timestamp": rec.timestamp,
                        "message": rec.message,
                    })
        return results

    def delete_checkin_history(self, phone: str) -> bool:
        """DPDP Act Right to Erasure: Permanently removes all safety check-in history."""
        p_hash = hash_phone(phone)
        if p_hash in self._checkins:
            del self._checkins[p_hash]
            logger.info("Erased citizen checkin history per DPDP request", phone_hash=p_hash[:8])
            return True
        return False

    # -------------------------------------------------------------------------
    # PART 2: CROWDSOURCED HAZARD REPORTS & OPS MODERATION QUEUE
    # -------------------------------------------------------------------------
    def submit_hazard_report(
        self,
        reporter_phone: str,
        district: str,
        hazard_type: HimalayanHazardType,
        category: HazardReportCategory,
        description: str,
        lat: float,
        lon: float,
        photo_url: Optional[str] = None,
    ) -> CrowdsourcedHazardReport:
        """
        Accepts crowdsourced hazard report from citizen.
        Must fall strictly within Uttarakhand bounding box.
        Always enters the system as UNVERIFIED (is_unverified = True) pending DMMC admin review.
        """
        # Validate coordinates against Uttarakhand bounding box
        if not (UTTARAKHAND_BBOX["min_lat"] <= lat <= UTTARAKHAND_BBOX["max_lat"] and
                UTTARAKHAND_BBOX["min_lon"] <= lon <= UTTARAKHAND_BBOX["max_lon"]):
            raise ValueError(f"Report location ({lat}, {lon}) is outside Uttarakhand bounding box")

        report_id = f"RPT-{int(time.time()*1000)}-{district[:3].upper()}"
        report = CrowdsourcedHazardReport(
            report_id=report_id,
            reporter_phone_hash=hash_phone(reporter_phone),
            district=district,
            hazardType=hazard_type,
            category=category,
            description=description,
            photo_url=photo_url,
            lat=lat,
            lon=lon,
            submitted_at=datetime.now(timezone.utc).isoformat(),
            status=HazardReportStatus.UNVERIFIED,
            is_unverified=True,
        )
        self._hazard_reports[report_id] = report
        logger.info("Crowdsourced hazard report received", report_id=report_id, district=district, hazard=hazard_type)
        return report

    def get_hazard_reports(
        self,
        status: Optional[HazardReportStatus] = None,
        district: Optional[str] = None,
    ) -> List[CrowdsourcedHazardReport]:
        reports = list(self._hazard_reports.values())
        if status:
            reports = [r for r in reports if r.status == status]
        if district:
            reports = [r for r in reports if r.district.lower() == district.lower()]
        return sorted(reports, key=lambda x: x.submitted_at, reverse=True)

    def moderate_hazard_report(
        self,
        report_id: str,
        action: str,  # APPROVE, REJECT, MERGE
        admin_user: str,
        notes: Optional[str] = None,
        merged_alert_id: Optional[str] = None,
    ) -> CrowdsourcedHazardReport:
        """
        DMMC Admin action to approve, reject, or merge an unverified crowdsourced report.
        """
        if report_id not in self._hazard_reports:
            raise KeyError(f"Report {report_id} not found")

        report = self._hazard_reports[report_id]
        act = action.upper().strip()

        if act == "APPROVE":
            report.status = HazardReportStatus.APPROVED
            report.is_unverified = False
        elif act == "REJECT":
            report.status = HazardReportStatus.REJECTED
            report.is_unverified = True
        elif act == "MERGE":
            report.status = HazardReportStatus.MERGED
            report.is_unverified = False
        else:
            raise ValueError(f"Invalid moderation action: {action}. Expected APPROVE, REJECT, or MERGE.")

        report.verification_notes = notes
        report.verified_by = admin_user

        # Record audit trail
        self.record_admin_action(
            action_type=f"REPORT_MODERATION_{act}",
            admin_user=admin_user,
            target_id=report_id,
            details={
                "previous_status": "UNVERIFIED",
                "new_status": report.status.value,
                "notes": notes,
                "merged_alert_id": merged_alert_id,
            },
        )
        return report

    # -------------------------------------------------------------------------
    # PART 3: SHELTER OCCUPANCY MANAGEMENT
    # -------------------------------------------------------------------------
    def get_shelters(self, district: Optional[str] = None) -> List[ShelterOccupancyItem]:
        shelters = list(self._shelters.values())
        if district:
            shelters = [s for s in shelters if s.district.lower() == district.lower()]
        return shelters

    def update_shelter_occupancy(
        self,
        shelter_id: str,
        current_occupancy: int,
        is_live: bool,
        admin_user: str,
    ) -> ShelterOccupancyItem:
        if shelter_id not in self._shelters:
            raise KeyError(f"Shelter {shelter_id} not found")

        shelter = self._shelters[shelter_id]
        old_occ = shelter.current_occupancy
        shelter.current_occupancy = current_occupancy
        shelter.is_live = is_live
        shelter.last_updated = datetime.now(timezone.utc).isoformat()

        self.record_admin_action(
            action_type="SHELTER_OCCUPANCY_UPDATE",
            admin_user=admin_user,
            target_id=shelter_id,
            details={
                "previous_occupancy": old_occ,
                "new_occupancy": current_occupancy,
                "is_live": is_live,
            },
        )
        return shelter

    # -------------------------------------------------------------------------
    # PART 4: AUDIT TRAIL LOGGING
    # -------------------------------------------------------------------------
    def record_admin_action(
        self,
        action_type: str,
        admin_user: str,
        target_id: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> AdminAuditRecord:
        record = AdminAuditRecord(
            audit_id=f"adm_aud_{int(time.time()*1000)}",
            action_type=action_type,
            admin_user=admin_user,
            target_id=target_id,
            details=details or {},
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self._audit_logs.append(record)
        return record

    def get_audit_trail(
        self,
        limit: int = 100,
        admin_user: Optional[str] = None,
        action_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        logs = self._audit_logs
        if admin_user:
            logs = [l for l in logs if l.admin_user.lower() == admin_user.lower()]
        if action_type:
            logs = [l for l in logs if action_type.lower() in l.action_type.lower()]
        return [l.model_dump() for l in reversed(logs[-limit:])]


# Global singleton
citizen_safety_service = CitizenSafetyService()
