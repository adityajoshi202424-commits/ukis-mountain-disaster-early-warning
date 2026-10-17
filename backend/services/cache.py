"""
Memory Cache Subsystem (Redis & High-Frequency In-Memory Buffer)

Caches high-frequency 15-minute telemetry streams to prevent PostgreSQL database bottlenecks
during peak storm telemetry bursts.
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any


class TelemetryCacheService:
    """
    High-frequency telemetry stream buffer with Redis / in-memory fallback.
    """

    def __init__(self):
        self._memory_cache: Dict[str, Dict[str, Any]] = {}
        self._station_buffers: Dict[str, List[Dict[str, Any]]] = {}

    def set_telemetry(self, station_id: str, payload: Dict[str, Any], ttl_seconds: int = 3600):
        """Buffers the latest incoming station telemetry point."""
        key = f"telemetry:{station_id}"
        self._memory_cache[key] = {
            "payload": payload,
            "cached_at": time.time(),
            "expires_at": time.time() + ttl_seconds,
        }

        # Keep rolling 24-hour buffer for station
        if station_id not in self._station_buffers:
            self._station_buffers[station_id] = []
        self._station_buffers[station_id].append(payload)
        # Trim buffer to max 96 observations (24h * 4 per hour)
        if len(self._station_buffers[station_id]) > 96:
            self._station_buffers[station_id].pop(0)

    def get_latest_telemetry(self, station_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves the latest unexpired telemetry point for a station."""
        key = f"telemetry:{station_id}"
        entry = self._memory_cache.get(key)
        if entry and entry["expires_at"] > time.time():
            return entry["payload"]
        return None

    def get_station_history(self, station_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieves recent rolling observations for velocity calculus."""
        buf = self._station_buffers.get(station_id, [])
        return buf[-limit:]

    def clear_all(self):
        self._memory_cache.clear()
        self._station_buffers.clear()


telemetry_cache = TelemetryCacheService()
