"""
DMMC Uttarakhand Adapter Staleness & System Self-Monitoring Engine.
Periodically audits all 6 hazard telemetry feeds and 5 alert delivery gateways.
If a feed goes stale beyond its expected refresh cadence, generates an internal
DMMC Operations Alert (surfaced strictly to DMMC staff in the Admin Dashboard,
never to citizens, to avoid panic while alerting field engineers).
"""

from __future__ import annotations

import os
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import structlog

logger = structlog.get_logger("dmmc_health_monitor")


class AdapterHealthStatus:
    def __init__(
        self,
        adapter_id: str,
        display_name: str,
        category: str,  # HAZARD_FEED, DELIVERY_GATEWAY, NATIONAL_INTEGRATION
        expected_interval_sec: int,
        is_configured: bool,
        endpoint_url: Optional[str] = None,
        last_success: Optional[str] = None,
    ):
        self.adapter_id = adapter_id
        self.display_name = display_name
        self.category = category
        self.expected_interval_sec = expected_interval_sec
        self.is_configured = is_configured
        self.endpoint_url = endpoint_url
        self.last_success = last_success
        self.is_stale = False
        self.status = "ONLINE" if (is_configured and last_success) else ("UNCONFIGURED" if not is_configured else "STALE")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "adapter_id": self.adapter_id,
            "display_name": self.display_name,
            "category": self.category,
            "expected_interval_sec": self.expected_interval_sec,
            "is_configured": self.is_configured,
            "endpoint_url": self.endpoint_url or "NOT_CONFIGURED",
            "last_success": self.last_success,
            "is_stale": self.is_stale,
            "status": self.status,
        }


class AdapterHealthMonitor:
    def __init__(self):
        self._internal_ops_alerts: List[Dict[str, Any]] = []
        self._adapters: Dict[str, AdapterHealthStatus] = {}
        self.refresh_adapter_registry()

    def refresh_adapter_registry(self):
        """Initializes and checks configuration status for all feeds and delivery gateways."""
        now_str = datetime.now(timezone.utc).isoformat()
        
        # 6 Hazard Telemetry Feeds
        cwc_stream = os.getenv("CWC_RIVER_GAUGE_STREAM")
        cwc_key = os.getenv("CWC_GAUGE_API_KEY")
        self._adapters["CWC_GAUGE"] = AdapterHealthStatus(
            adapter_id="CWC_GAUGE",
            display_name="CWC River Gauges (GLOF & Flash Floods)",
            category="HAZARD_FEED",
            expected_interval_sec=180,
            is_configured=bool(cwc_stream and cwc_key),
            endpoint_url=cwc_stream,
            last_success=None,
        )

        imd_url = os.getenv("IMD_UTTARAKHAND_WARN_URL")
        self._adapters["IMD_NOWCAST"] = AdapterHealthStatus(
            adapter_id="IMD_NOWCAST",
            display_name="IMD Uttarakhand Nowcast (Cloudburst & Storms)",
            category="HAZARD_FEED",
            expected_interval_sec=300,
            is_configured=bool(imd_url),
            endpoint_url=imd_url,
            last_success=None,
        )

        iitr_ws = os.getenv("IITR_EARTHQUAKE_WS")
        iitr_tok = os.getenv("IITR_EEW_AUTH_TOKEN")
        self._adapters["IITR_EEW"] = AdapterHealthStatus(
            adapter_id="IITR_EEW",
            display_name="IIT Roorkee Seismic Early Warning Stream",
            category="HAZARD_FEED",
            expected_interval_sec=60,
            is_configured=bool(iitr_ws and iitr_tok),
            endpoint_url=iitr_ws,
            last_success=None,
        )

        self._adapters["LANDSLIDE_SLOPE"] = AdapterHealthStatus(
            adapter_id="LANDSLIDE_SLOPE",
            display_name="Geological Survey / Slope Stability Monitors",
            category="HAZARD_FEED",
            expected_interval_sec=300,
            is_configured=False,
            endpoint_url=None,
            last_success=None,
        )

        self._adapters["FOREST_FIRE"] = AdapterHealthStatus(
            adapter_id="FOREST_FIRE",
            display_name="FSI / MODIS Dynamic Forest Fire Coordinate Tracker",
            category="HAZARD_FEED",
            expected_interval_sec=600,
            is_configured=False,
            endpoint_url=None,
            last_success=None,
        )

        self._adapters["AVALANCHE_SNOW"] = AdapterHealthStatus(
            adapter_id="AVALANCHE_SNOW",
            display_name="DGRE / High Altitude Avalanche & Snow Monitors",
            category="HAZARD_FEED",
            expected_interval_sec=300,
            is_configured=False,
            endpoint_url=None,
            last_success=None,
        )

        # 5 Alert Delivery Gateways
        cdot_proxy = os.getenv("CDOT_CELL_BROADCAST_PROXY")
        self._adapters["CDOT_CELL_BROADCAST"] = AdapterHealthStatus(
            adapter_id="CDOT_CELL_BROADCAST",
            display_name="C-DOT Cell Broadcast Emergency Gateway",
            category="DELIVERY_GATEWAY",
            expected_interval_sec=3600,
            is_configured=bool(cdot_proxy),
            endpoint_url=cdot_proxy,
            last_success=None,
        )

        nic_sms_url = os.getenv("NIC_SMS_GATEWAY_URL")
        nic_sms_key = os.getenv("NIC_SMS_API_KEY")
        self._adapters["NIC_SMS"] = AdapterHealthStatus(
            adapter_id="NIC_SMS",
            display_name="NIC National SMS Gateway",
            category="DELIVERY_GATEWAY",
            expected_interval_sec=3600,
            is_configured=bool(nic_sms_url and nic_sms_key),
            endpoint_url=nic_sms_url,
            last_success=None,
        )

        nic_ivr_url = os.getenv("NIC_IVR_GATEWAY_URL")
        nic_ivr_key = os.getenv("NIC_IVR_API_KEY")
        self._adapters["NIC_IVR"] = AdapterHealthStatus(
            adapter_id="NIC_IVR",
            display_name="NIC IVR Voice Call Gateway (Garhwali/Kumaoni/Hindi)",
            category="DELIVERY_GATEWAY",
            expected_interval_sec=3600,
            is_configured=bool(nic_ivr_url and nic_ivr_key),
            endpoint_url=nic_ivr_url,
            last_success=None,
        )

        wa_url = os.getenv("WHATSAPP_BUSINESS_API_URL")
        wa_key = os.getenv("WHATSAPP_BUSINESS_API_KEY")
        self._adapters["WHATSAPP_BUSINESS"] = AdapterHealthStatus(
            adapter_id="WHATSAPP_BUSINESS",
            display_name="WhatsApp Business API Gateway",
            category="DELIVERY_GATEWAY",
            expected_interval_sec=3600,
            is_configured=bool(wa_url and wa_key),
            endpoint_url=wa_url,
            last_success=None,
        )

        fcm_key = os.getenv("FCM_SERVER_KEY")
        self._adapters["FCM_PUSH"] = AdapterHealthStatus(
            adapter_id="FCM_PUSH",
            display_name="Firebase Cloud Messaging (FCM Push)",
            category="DELIVERY_GATEWAY",
            expected_interval_sec=3600,
            is_configured=bool(fcm_key),
            endpoint_url="fcm.googleapis.com",
            last_success=None,
        )

        # NDMA National Integrations (ADR-001)
        ndma_cap = os.getenv("NDMA_CAP_FEED_URL")
        sachet_feed = os.getenv("NDMA_SACHET_FEED_URL")
        self._adapters["NDMA_CAP"] = AdapterHealthStatus(
            adapter_id="NDMA_CAP",
            display_name="NDMA CAP National Feed Consumer",
            category="NATIONAL_INTEGRATION",
            expected_interval_sec=300,
            is_configured=bool(ndma_cap),
            endpoint_url=ndma_cap,
            last_success=None,
        )
        self._adapters["NDMA_SACHET"] = AdapterHealthStatus(
            adapter_id="NDMA_SACHET",
            display_name="NDMA Sachet Upstream Warning Publisher",
            category="NATIONAL_INTEGRATION",
            expected_interval_sec=300,
            is_configured=bool(sachet_feed),
            endpoint_url=sachet_feed,
            last_success=None,
        )

    def record_feed_heartbeat(self, adapter_id: str, success: bool, error_msg: Optional[str] = None):
        """Called when a feed completes a polling cycle or WebSocket heartbeat."""
        if adapter_id not in self._adapters:
            return

        adapter = self._adapters[adapter_id]
        now_str = datetime.now(timezone.utc).isoformat()
        if success:
            adapter.last_success = now_str
            adapter.is_stale = False
            adapter.status = "ONLINE"
        else:
            adapter.status = "ERROR"
            self._raise_internal_ops_alert(
                level="WARNING",
                adapter_id=adapter_id,
                message=f"Feed {adapter.display_name} returned error: {error_msg or 'Unknown failure'}",
            )

    def audit_staleness(self) -> List[Dict[str, Any]]:
        """
        Scans all configured adapters. If the time since last_success exceeds expected_interval_sec,
        marks the adapter as STALE and triggers an internal DMMC ops alert.
        """
        now = time.time()
        stale_adapters = []
        for a_id, item in self._adapters.items():
            if not item.is_configured:
                item.status = "UNCONFIGURED"
                item.is_stale = False
                continue

            if not item.last_success:
                item.status = "STALE"
                item.is_stale = True
                stale_adapters.append(item.to_dict())
                self._raise_internal_ops_alert(
                    level="CRITICAL_OPS",
                    adapter_id=a_id,
                    message=f"Institutional feed {item.display_name} has no successful ingest recorded. Verification required.",
                )
                continue

            try:
                last_dt = datetime.fromisoformat(item.last_success.replace("Z", "+00:00"))
                elapsed = now - last_dt.timestamp()
                if elapsed > item.expected_interval_sec:
                    item.status = "STALE"
                    item.is_stale = True
                    stale_adapters.append(item.to_dict())
                    self._raise_internal_ops_alert(
                        level="WARNING",
                        adapter_id=a_id,
                        message=f"Feed {item.display_name} is stale: no updates received for {int(elapsed)}s (expected every {item.expected_interval_sec}s).",
                    )
                else:
                    item.status = "ONLINE"
                    item.is_stale = False
            except Exception:
                pass

        return stale_adapters

    def _raise_internal_ops_alert(self, level: str, adapter_id: str, message: str):
        """Internal operations alert — surfaced to DMMC control room only, not citizens."""
        alert_entry = {
            "alert_id": f"ops_{int(time.time()*1000)}_{adapter_id}",
            "level": level,
            "adapter_id": adapter_id,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        # Deduplicate recent messages for same adapter
        if not any(a["adapter_id"] == adapter_id and a["message"] == message for a in self._internal_ops_alerts[-10:]):
            self._internal_ops_alerts.append(alert_entry)
            logger.warn("Internal DMMC ops alert generated", **alert_entry)

    def get_adapter_statuses(self) -> List[Dict[str, Any]]:
        self.audit_staleness()
        return [a.to_dict() for a in self._adapters.values()]

    def get_internal_ops_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        return list(reversed(self._internal_ops_alerts[-limit:]))


# Global singleton
adapter_health_monitor = AdapterHealthMonitor()
