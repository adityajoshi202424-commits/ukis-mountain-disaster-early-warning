"""
Resilient In-Memory & Distributed Cache with Conditional Emergency Bypass
UKIS P-011 Mountain Disaster Intelligence — Low-Latency Caching Engine

Mandates:
1. Aggressive caching for routine, rate-limited Indian government telemetry (IMD, CWC, NCS).
2. Conditional Bypass: Completely bypasses cache for 'Severe' or 'Extreme' emergency alerts (0 latency).
3. Failsafe Recovery: Protects callers from upstream 5xx outages by returning last known valid state.
"""

from __future__ import annotations

import time
from typing import Dict, Optional, Any, Callable, Awaitable
from pydantic import BaseModel, Field

from backend.config.env_validator import indian_env


class CachedEntry(BaseModel):
    key: str
    value: Any
    expires_at: float
    created_at: float
    is_emergency: bool = False


class ResilientCacheEngine:
    """
    In-memory / Redis-compatible cache with emergency priority bypass.
    """

    def __init__(self, default_ttl_seconds: Optional[int] = None):
        self.default_ttl = default_ttl_seconds or indian_env.cache_ttl_seconds
        self._store: Dict[str, CachedEntry] = {}
        self._hits = 0
        self._misses = 0
        self._bypasses = 0

    def get(
        self,
        key: str,
        severity: Optional[str] = None,
        urgency: Optional[str] = None,
    ) -> Optional[Any]:
        """
        Retrieves cached value unless severity is CRITICAL / EXTREME / SEVERE or urgency is IMMEDIATE,
        in which case cache is conditionally bypassed with zero delay.
        """
        # Conditional Emergency Bypass
        is_emergency = (
            (severity and severity.upper() in ("CRITICAL", "EXTREME", "SEVERE", "RED", "EMERGENCY"))
            or (urgency and urgency.upper() in ("IMMEDIATE", "URGENT"))
        )
        if is_emergency:
            self._bypasses += 1
            return None

        entry = self._store.get(key)
        if not entry:
            self._misses += 1
            return None

        if time.time() > entry.expires_at:
            # Expired
            self._misses += 1
            return None

        self._hits += 1
        return entry.value

    def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None,
        is_emergency: bool = False,
    ):
        """Sets cached value with explicit or default TTL."""
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        now = time.time()
        self._store[key] = CachedEntry(
            key=key,
            value=value,
            expires_at=now + ttl,
            created_at=now,
            is_emergency=is_emergency,
        )

    def invalidate(self, key: str):
        """Evicts a key from cache."""
        self._store.pop(key, None)

    def clear(self):
        """Clears all cached entries."""
        self._store.clear()

    async def get_or_fetch_resilient(
        self,
        key: str,
        fetcher: Callable[[], Awaitable[Any]],
        severity: Optional[str] = None,
        ttl_seconds: Optional[int] = None,
    ) -> Any:
        """
        High-reliability wrapper:
        1. Checks cache unless emergency bypass applies.
        2. If miss or bypass, calls upstream fetcher.
        3. If upstream fails with exception or 5xx, falls back to stale cache entry if available.
        """
        cached = self.get(key, severity=severity)
        if cached is not None:
            return cached

        try:
            val = await fetcher()
            self.set(
                key=key,
                value=val,
                ttl_seconds=ttl_seconds,
                is_emergency=severity in ("CRITICAL", "EXTREME", "SEVERE", "RED"),
            )
            return val
        except Exception:
            # Failsafe recovery: return stale entry if exists
            stale_entry = self._store.get(key)
            if stale_entry:
                return stale_entry.value
            raise

    def get_metrics(self) -> Dict[str, Any]:
        """Returns cache telemetry."""
        return {
            "total_keys": len(self._store),
            "hits": self._hits,
            "misses": self._misses,
            "emergency_bypasses": self._bypasses,
            "default_ttl_seconds": self.default_ttl,
        }


resilient_cache = ResilientCacheEngine()
