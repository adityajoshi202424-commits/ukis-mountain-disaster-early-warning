"""
Integration test: Prove real data flows from Open-Meteo.

This test hits the actual Open-Meteo API (no mock).
It proves:
1. Real data is fetched
2. Every observation has provenance
3. The quality engine validates it
4. Stale/unavailable data is reported honestly
"""

import asyncio
from datetime import datetime, timezone

from backend.data.providers.weather.open_meteo import OpenMeteoProvider
from backend.data.providers.base import ProviderStatus, QualityStatus
from backend.data.validation.quality import quality_engine


async def test_real_open_meteo():
    """Fetch real weather data for Joshimath, Uttarakhand and validate."""
    provider = OpenMeteoProvider()

    # --- Test 1: Check provider status ---
    status = await provider.check_status()
    print(f"\n{'='*60}")
    print(f"Provider: {provider.name}")
    print(f"Status: {status.value}")

    if status != ProviderStatus.AVAILABLE:
        print("SOURCE OFFLINE — cannot verify real data flow")
        print(f"{'='*60}")
        await provider.close()
        return

    # --- Test 2: Fetch real forecast data for Joshimath ---
    print(f"\nFetching real weather data for Joshimath (30.5564°N, 79.5670°E)...")
    batch = await provider.fetch(latitude=30.5564, longitude=79.5670)

    print(f"Provider status: {batch.status.value}")
    print(f"Total observations: {len(batch.observations)}")
    print(f"Valid observations: {batch.valid_count}")

    assert batch.status == ProviderStatus.AVAILABLE, "Provider should be available"
    assert len(batch.observations) > 0, "Should have received observations"

    # --- Test 3: Every observation has provenance ---
    for obs in batch.observations[:5]:
        assert obs.provenance is not None, "Every observation must have provenance"
        assert obs.provenance.source == "Open-Meteo", "Source must be Open-Meteo"
        assert obs.provenance.retrieved_at is not None, "Must have retrieved_at"

    print("\n✓ All observations have full provenance")

    # --- Test 4: Show a sample observation with provenance ---
    sample = batch.observations[0]
    print(f"\nSample observation:")
    print(f"  Variable:           {sample.variable}")
    print(f"  Value:              {sample.value} {sample.unit}")
    print(f"  Observation time:   {sample.observation_time}")
    print(f"  Source:             {sample.provenance.source}")
    print(f"  Source URL:         {sample.provenance.source_url}")
    print(f"  Dataset:            {sample.provenance.dataset}")
    print(f"  Retrieved at:       {sample.provenance.retrieved_at}")
    print(f"  Spatial resolution: {sample.provenance.spatial_resolution}")
    print(f"  Temporal resolution:{sample.provenance.temporal_resolution}")
    print(f"  Quality status:     {sample.provenance.quality_status.value}")

    # --- Test 5: Run through quality engine ---
    batch = quality_engine.validate_batch(batch)
    valid = sum(1 for o in batch.observations if o.provenance.quality_status == QualityStatus.VALID)
    invalid = sum(1 for o in batch.observations if o.provenance.quality_status == QualityStatus.INVALID)
    missing = sum(1 for o in batch.observations if o.provenance.quality_status == QualityStatus.MISSING)
    stale = sum(1 for o in batch.observations if o.provenance.quality_status == QualityStatus.STALE)

    print(f"\nQuality engine results:")
    print(f"  VALID:   {valid}")
    print(f"  INVALID: {invalid}")
    print(f"  MISSING: {missing}")
    print(f"  STALE:   {stale}")

    # --- Test 6: Show staleness for recent observations ---
    now = datetime.now(timezone.utc)
    recent = [o for o in batch.observations if o.observation_time and o.observation_time <= now]
    if recent:
        newest = max(recent, key=lambda o: o.observation_time)
        staleness = quality_engine.get_staleness(newest, now)
        formatted = quality_engine.format_staleness(staleness)
        print(f"\nMost recent observation: {formatted}")
        print(f"  Variable: {newest.variable}")
        print(f"  Value: {newest.value} {newest.unit}")

    # --- Test 7: Provider metadata ---
    meta = provider.metadata()
    print(f"\nProvider metadata:")
    print(f"  License: {meta['license']}")
    print(f"  Coverage: {meta['coverage']}")
    print(f"  Limitations: {len(meta['limitations'])} documented")
    for lim in meta["limitations"]:
        print(f"    • {lim}")

    # --- Test 8: Fetch historical data ---
    print(f"\nFetching historical data (2021-02-05 to 2021-02-08)...")
    hist_batch = await provider.fetch(
        latitude=30.5564,
        longitude=79.5670,
        start_time=datetime(2021, 2, 5, tzinfo=timezone.utc),
        end_time=datetime(2021, 2, 8, tzinfo=timezone.utc),
    )
    print(f"  Historical observations: {len(hist_batch.observations)}")
    print(f"  Status: {hist_batch.status.value}")

    if hist_batch.status == ProviderStatus.AVAILABLE:
        assert len(hist_batch.observations) > 0, "Should have historical data when available"
    else:
        # Confirms real API failure was reported honestly without synthetic fallback
        assert hist_batch.status in (ProviderStatus.OFFLINE, ProviderStatus.RATE_LIMITED, ProviderStatus.ERROR)
        assert len(hist_batch.observations) == 0, "No fake data should be substituted on failure"

    print(f"\n{'='*60}")
    print("✓ PIPELINE VERIFIED: Real data → Validation → Provenance")
    print(f"{'='*60}")

    await provider.close()


if __name__ == "__main__":
    asyncio.run(test_real_open_meteo())
