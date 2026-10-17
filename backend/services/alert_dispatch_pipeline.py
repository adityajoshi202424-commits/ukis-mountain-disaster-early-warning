"""
DMMC Uttarakhand Unified Alert Dispatch Pipeline.
Coordinates Geofencing, Multilingual CAP Resolution (EN, HI, GBM, KFY),
Dual-Channel FCM Push + NIC SMS + C-DOT Cell Broadcast Fallback,
Delivery Logging, and Post-Incident Ops Audit.
"""

from __future__ import annotations

import time
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import structlog

from backend.cap_schema import CapAlertItem, AlertSeverity, SupportedLocale
from backend.services.dpdp_user_registry import user_registry, RegisteredSubscriber
from backend.services.push_sms_pipeline import (
    nic_sms_adapter,
    nic_ivr_adapter,
    whatsapp_adapter,
    cdot_broadcast_adapter,
    fcm_push_adapter,
    GatewayDispatchResult,
)

logger = structlog.get_logger("dmmc_alert_dispatch")


class DeliveryAuditRecord:
    def __init__(
        self,
        alert_id: str,
        hazard_type: str,
        severity: str,
        districts: List[str],
        matched_subscribers: int,
        sms_sent: int,
        push_sent: int,
        cell_broadcast_fired: bool,
        gateway_statuses: Dict[str, str],
        latency_ms: float,
        ivr_calls_placed: int = 0,
        whatsapp_sent: int = 0,
    ):
        self.audit_id = f"aud_{int(time.time()*1000)}_{alert_id}"
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.alert_id = alert_id
        self.hazard_type = hazard_type
        self.severity = severity
        self.districts = districts
        self.matched_subscribers = matched_subscribers
        self.sms_sent = sms_sent
        self.push_sent = push_sent
        self.ivr_calls_placed = ivr_calls_placed
        self.whatsapp_sent = whatsapp_sent
        self.cell_broadcast_fired = cell_broadcast_fired
        self.gateway_statuses = gateway_statuses
        self.latency_ms = latency_ms

    def to_dict(self) -> Dict[str, Any]:
        return {
            "audit_id": self.audit_id,
            "timestamp": self.timestamp,
            "alert_id": self.alert_id,
            "hazard_type": self.hazard_type,
            "severity": self.severity,
            "districts": self.districts,
            "matched_subscribers": self.matched_subscribers,
            "sms_sent": self.sms_sent,
            "push_sent": self.push_sent,
            "ivr_calls_placed": self.ivr_calls_placed,
            "whatsapp_sent": self.whatsapp_sent,
            "cell_broadcast_fired": self.cell_broadcast_fired,
            "gateway_statuses": self.gateway_statuses,
            "latency_ms": self.latency_ms,
        }


class AlertDispatchPipeline:
    def __init__(self):
        self._audit_records: List[DeliveryAuditRecord] = []

    def resolve_alert_text_for_user(self, alert: CapAlertItem, user_locale: str) -> Dict[str, str]:
        """
        Language Resolution Rule:
        Pull matching-language info block from CAP payload per user's selected locale;
        fall back to Hindi ('hi-IN') if that locale isn't present in payload.
        """
        # Map abbreviations if needed
        norm_locale = user_locale
        if norm_locale in ("gb", "gb-IN"):
            norm_locale = "gbm-IN"
        elif norm_locale in ("ku", "ku-IN"):
            norm_locale = "kfy-IN"
        elif norm_locale == "en":
            norm_locale = "en-IN"
        elif norm_locale == "hi":
            norm_locale = "hi-IN"

        localized_map = alert.localized

        # 1. Exact user locale match
        if norm_locale in localized_map:
            info = localized_map[norm_locale]
            return {"title": info.headline, "instruction": info.instruction}

        # 2. Fallback to Hindi ('hi-IN')
        if "hi-IN" in localized_map:
            info = localized_map["hi-IN"]
            return {"title": info.headline, "instruction": info.instruction}

        # 3. Fallback to English ('en-IN')
        if "en-IN" in localized_map:
            info = localized_map["en-IN"]
            return {"title": info.headline, "instruction": info.instruction}

        # 4. Canonical headline fallback
        return {
            "title": f"DMMC Alert: {alert.hazardType} ({alert.severity})",
            "instruction": "Follow official USDMA directives and proceed to high ground.",
        }

    async def process_and_dispatch_cap_alert(self, alert: CapAlertItem) -> Dict[str, Any]:
        """
        End-to-end CAP alert dispatch execution across 5 channels in priority order:
        - For CRITICAL:
          1. C-DOT Cell Broadcast (mass zero-data warning to affected polygon)
          2. NIC SMS Gateway (batch per language)
          3. NIC IVR Voice Call (in user's regional language/dialect)
          4. WhatsApp Business API (batched per language)
          5. FCM Push (for app-open Android users)
        - For SEVERE / ADVISORY:
          1. NIC SMS Gateway (primary channel)
          2. WhatsApp Business API (additional reliability channel)
          3. FCM Push (app users)
          4. NIC IVR Voice Call (fallback if SMS unavailable or per preference)
        """
        start_time = time.time()
        logger.info(
            "Processing incoming CAP alert for 5-channel dispatch",
            alert_id=alert.identifier,
            severity=alert.severity,
            hazard=alert.hazardType,
        )

        # 1. Geofence match against registered subscribers
        polygon_coords = alert.area.polygon if alert.area else None
        target_districts = alert.districts
        subscribers = user_registry.find_subscribers_for_geofence(
            districts=target_districts,
            polygon=polygon_coords,
        )

        # 2. Batch subscribers by language
        lang_batches: Dict[str, List[RegisteredSubscriber]] = {}
        for sub in subscribers:
            loc = sub.locale or "hi-IN"
            lang_batches.setdefault(loc, []).append(sub)

        gateway_statuses: Dict[str, str] = {}
        total_sms_sent = 0
        total_push_sent = 0
        total_ivr_placed = 0
        total_whatsapp_sent = 0
        cell_broadcast_fired = False

        is_critical = alert.severity == AlertSeverity.CRITICAL

        # =========================================================================
        # CHANNEL 1: C-DOT Cell Broadcast (Triggered first for mass CRITICAL alerts)
        # =========================================================================
        if is_critical:
            hi_text = self.resolve_alert_text_for_user(alert, "hi-IN")
            broadcast_msg = f"EMERGENCY DMMC: {hi_text['title']} - {hi_text['instruction']}"
            poly_points = polygon_coords or [[30.3, 78.5], [30.8, 79.5]]
            try:
                cdot_res = await cdot_broadcast_adapter.broadcast_polygon(
                    polygon_coords=poly_points,
                    alert_text=broadcast_msg,
                    severity=alert.severity.value,
                )
                gateway_statuses["CDOT_CELL_BROADCAST"] = cdot_res.status
                if cdot_res.status == "SUCCESS":
                    cell_broadcast_fired = True
            except Exception as ex:
                logger.error("C-DOT Cell Broadcast dispatch exception", error=str(ex))
                gateway_statuses["CDOT_CELL_BROADCAST"] = "FAILED"

        # =========================================================================
        # CHANNEL 2: NIC SMS Gateway (Batched per user language)
        # =========================================================================
        for loc, batch in lang_batches.items():
            phones = [user_registry.decrypt_phone(s.encrypted_phone) for s in batch if s.encrypted_phone]
            if not phones:
                continue

            text_obj = self.resolve_alert_text_for_user(alert, loc)
            sms_text = f"🚨 DMMC UKIS ALERT: {text_obj['title']}\n{text_obj['instruction']}\nHelpline: 112 / 1070"

            try:
                sms_res = await nic_sms_adapter.dispatch_sms_batch(phone_numbers=phones, text_content=sms_text)
                gateway_statuses[f"NIC_SMS_{loc}"] = sms_res.status
                if sms_res.status == "SUCCESS":
                    total_sms_sent += len(phones)
            except Exception as ex:
                logger.error("NIC SMS Gateway exception", locale=loc, error=str(ex))
                gateway_statuses[f"NIC_SMS_{loc}"] = "FAILED"

        # =========================================================================
        # CHANNEL 3: NIC IVR Voice Call (Voice alert in user's dialect for accessibility)
        # Triggered for CRITICAL tier, or when SMS fails, or as fallback
        # =========================================================================
        if is_critical or any("FAILED" in st for k, st in gateway_statuses.items() if "NIC_SMS" in k):
            for loc, batch in lang_batches.items():
                phones = [user_registry.decrypt_phone(s.encrypted_phone) for s in batch if s.encrypted_phone]
                if not phones:
                    continue

                prompt_url = f"https://usdma.uk.gov.in/audio/prompts/{alert.hazardType.value.lower()}_{loc}.wav"
                try:
                    ivr_res = await nic_ivr_adapter.dispatch_voice_call_batch(
                        phone_numbers=phones,
                        audio_prompt_url=prompt_url,
                        language_code=loc,
                    )
                    gateway_statuses[f"NIC_IVR_{loc}"] = ivr_res.status
                    if ivr_res.status == "SUCCESS":
                        total_ivr_placed += len(phones)
                except Exception as ex:
                    logger.error("NIC IVR Gateway exception", locale=loc, error=str(ex))
                    gateway_statuses[f"NIC_IVR_{loc}"] = "FAILED"

        # =========================================================================
        # CHANNEL 4: WhatsApp Business API (High-reliability multimedia channel)
        # =========================================================================
        for loc, batch in lang_batches.items():
            phones = [user_registry.decrypt_phone(s.encrypted_phone) for s in batch if s.encrypted_phone]
            if not phones:
                continue

            text_obj = self.resolve_alert_text_for_user(alert, loc)
            try:
                wa_res = await whatsapp_adapter.dispatch_whatsapp_batch(
                    phone_numbers=phones,
                    headline=text_obj["title"],
                    instruction=text_obj["instruction"],
                    severity=alert.severity.value,
                    map_link=f"https://usdma.uk.gov.in/emergency?alert={alert.identifier}",
                )
                gateway_statuses[f"WHATSAPP_{loc}"] = wa_res.status
                if wa_res.status == "SUCCESS":
                    total_whatsapp_sent += len(phones)
            except Exception as ex:
                logger.error("WhatsApp Business API exception", locale=loc, error=str(ex))
                gateway_statuses[f"WHATSAPP_{loc}"] = "FAILED"

        # =========================================================================
        # CHANNEL 5: FCM Push Notification (For app-open Android users)
        # =========================================================================
        push_tokens = [s.device_token for s in subscribers if s.device_token]
        if push_tokens:
            default_text = self.resolve_alert_text_for_user(alert, "hi-IN")
            try:
                push_res = await fcm_push_adapter.send_push_notification(
                    tokens=push_tokens,
                    title=f"🚨 [{alert.severity.value}] {default_text['title']}",
                    body=default_text["instruction"],
                    severity=alert.severity.value,
                )
                gateway_statuses["FCM_PUSH"] = push_res.status
                if push_res.status == "SUCCESS":
                    total_push_sent = len(push_tokens)
            except Exception as ex:
                logger.error("FCM Push exception", error=str(ex))
                gateway_statuses["FCM_PUSH"] = "FAILED"

        # If not critical, but SMS failed, trigger C-DOT Cell Broadcast fallback
        if not is_critical and any("FAILED" in st for k, st in gateway_statuses.items() if "NIC_SMS" in k):
            hi_text = self.resolve_alert_text_for_user(alert, "hi-IN")
            broadcast_msg = f"EMERGENCY DMMC: {hi_text['title']} - {hi_text['instruction']}"
            poly_points = polygon_coords or [[30.3, 78.5], [30.8, 79.5]]
            try:
                cdot_res = await cdot_broadcast_adapter.broadcast_polygon(
                    polygon_coords=poly_points,
                    alert_text=broadcast_msg,
                    severity=alert.severity.value,
                )
                gateway_statuses["CDOT_CELL_BROADCAST"] = cdot_res.status
                if cdot_res.status == "SUCCESS":
                    cell_broadcast_fired = True
            except Exception:
                pass

        duration_ms = round((time.time() - start_time) * 1000, 2)

        # 6. Post-Incident Delivery Audit Record
        audit_record = DeliveryAuditRecord(
            alert_id=alert.identifier,
            hazard_type=alert.hazardType.value,
            severity=alert.severity.value,
            districts=alert.districts,
            matched_subscribers=len(subscribers),
            sms_sent=total_sms_sent,
            push_sent=total_push_sent,
            ivr_calls_placed=total_ivr_placed,
            whatsapp_sent=total_whatsapp_sent,
            cell_broadcast_fired=cell_broadcast_fired,
            gateway_statuses=gateway_statuses,
            latency_ms=duration_ms,
        )
        self._audit_records.append(audit_record)

        return audit_record.to_dict()

    def get_audit_records(self, limit: int = 50) -> List[Dict[str, Any]]:
        return [r.to_dict() for r in reversed(self._audit_records[-limit:])]

    def get_ops_summary(self) -> Dict[str, Any]:
        total = len(self._audit_records)
        if total == 0:
            return {
                "total_dispatches": 0,
                "total_sms_delivered": 0,
                "total_push_delivered": 0,
                "total_ivr_placed": 0,
                "total_whatsapp_delivered": 0,
                "cell_broadcasts_count": 0,
                "success_rate_percent": 100.0,
                "average_latency_ms": 0.0,
            }

        sms_success = sum(r.sms_sent for r in self._audit_records)
        push_success = sum(r.push_sent for r in self._audit_records)
        ivr_success = sum(r.ivr_calls_placed for r in self._audit_records)
        wa_success = sum(r.whatsapp_sent for r in self._audit_records)
        cb_count = sum(1 for r in self._audit_records if r.cell_broadcast_fired)
        avg_lat = sum(r.latency_ms for r in self._audit_records) / total

        return {
            "total_dispatches": total,
            "total_sms_delivered": sms_success,
            "total_push_delivered": push_success,
            "total_ivr_placed": ivr_success,
            "total_whatsapp_delivered": wa_success,
            "cell_broadcasts_count": cb_count,
            "average_latency_ms": round(avg_lat, 2),
            "recent_dispatches": [r.to_dict() for r in self._audit_records[-5:]],
        }


# Global alert dispatch pipeline singleton
alert_dispatch_pipeline = AlertDispatchPipeline()
