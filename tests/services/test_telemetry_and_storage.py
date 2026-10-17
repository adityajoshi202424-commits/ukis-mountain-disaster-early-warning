"""
Tests for Telemetry Ingestion, Rate Limiting, Memory Cache, Blob Storage, and Human Fallback Verification
"""

import pytest
from backend.services.cache import telemetry_cache
from backend.services.storage import storage_service
from backend.middleware.rate_limiter import SlidingWindowRateLimiter
from backend.api.v1.telemetry import TelemetryIngestPayload, ingest_telemetry_stream, validation_queue


class TestCacheAndStorage:
    def test_telemetry_cache_buffering(self):
        telemetry_cache.set_telemetry("STN_01", {"rainfall": 15.0, "time": "2024-07-14T10:00:00Z"})
        latest = telemetry_cache.get_latest_telemetry("STN_01")
        assert latest is not None
        assert latest["rainfall"] == 15.0

        hist = telemetry_cache.get_station_history("STN_01")
        assert len(hist) > 0

    def test_blob_storage_file_routing(self):
        sample_bytes = b"GEOTIFF_FAKE_RASTER_BAND_ELEVATION_BYTES"
        meta = storage_service.store_file("radar_01", "sentinel1_radar.tif", sample_bytes, "image/tiff")
        assert meta.size_bytes == len(sample_bytes)
        assert meta.storage_tier == "LOCAL_BLOB"

        retrieved = storage_service.get_file_bytes("radar_01")
        assert retrieved == sample_bytes


class TestRateLimiter:
    def test_sliding_window_throttle(self):
        limiter = SlidingWindowRateLimiter(max_requests_per_window=5, window_seconds=10)
        # 5 requests pass
        for _ in range(5):
            assert limiter.check_rate_limit("192.168.1.50") is True
        # 6th request is throttled
        assert limiter.check_rate_limit("192.168.1.50") is False


class TestHumanFallbackIngestion:
    @pytest.mark.asyncio
    async def test_low_confidence_routes_to_human_queue(self):
        # Trigger condition with missing hydrology (confidence < 70%)
        payload = TelemetryIngestPayload(
            station_id="IMD_AWS_TEST_99",
            station_name="IMD Test Outlier AWS",
            latitude=26.02,
            longitude=89.98,
            rainfall_15m_mm=55.0,  # Extreme rain velocity
            river_water_level_m=None,  # Missing river gauge -> drops confidence
            soil_saturation_pct=92.0,
        )

        res = await ingest_telemetry_stream(payload)
        assert res["status"] == "PENDING_HUMAN_VALIDATION"
        assert "validation_id" in res
        val_id = res["validation_id"]
        assert val_id in validation_queue
        assert validation_queue[val_id].status == "PENDING_HUMAN_VALIDATION"
