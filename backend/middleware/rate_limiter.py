"""
Rate Limiting & Storm Ingestion Protection Middleware

Protects the API Gateway from server overload during peak storm telemetry bursts
using a high-throughput sliding window rate limiter.
"""

from __future__ import annotations

import os
import time
from typing import Dict, List
from fastapi import Request, HTTPException, status


class SlidingWindowRateLimiter:
    def __init__(self, max_requests_per_window: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests_per_window
        self.window_seconds = window_seconds
        self.request_history: Dict[str, List[float]] = {}

    def check_rate_limit(self, client_key: str) -> bool:
        """
        Returns True if the request is allowed, False if rate limited.
        """
        now = time.time()
        cutoff = now - self.window_seconds

        if client_key not in self.request_history:
            self.request_history[client_key] = []

        # Filter out timestamps outside active window
        self.request_history[client_key] = [
            t for t in self.request_history[client_key] if t > cutoff
        ]

        if len(self.request_history[client_key]) >= self.max_requests:
            return False

        self.request_history[client_key].append(now)
        return True

    def reset(self):
        self.request_history.clear()


# Default to 60 req/min per .env.production
_public_limit = int(os.getenv("PUBLIC_API_RATE_LIMIT_PER_MIN", "60"))
rate_limiter = SlidingWindowRateLimiter(max_requests_per_window=_public_limit, window_seconds=60)
public_rate_limiter = SlidingWindowRateLimiter(max_requests_per_window=_public_limit, window_seconds=60)


async def rate_limit_dependency(request: Request):
    """FastAPI dependency for rate limiting telemetry ingestion endpoints."""
    client_ip = request.client.host if request.client else "anonymous"
    if not rate_limiter.check_rate_limit(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Disaster API throttle active (Max {_public_limit} req/min).",
        )
    return True


async def public_rate_limit_dependency(request: Request):
    """FastAPI dependency for public endpoints (alerts, maps, crowdsourced submissions)."""
    client_ip = request.client.host if request.client else "anonymous"
    if not public_rate_limiter.check_rate_limit(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Max {_public_limit} requests per minute for public endpoints.",
        )
    return True
