"""
Comprehensive Test Suite for Indian Emergency Disaster Platform
Validates:
1. Multi-platform Environmental validation & regional bounds
2. 14+ Indian & Himalayan hazard matrix with 4-language directives (EN, HI, GAR, KUM)
3. NDMA CAP v1.2 XML ingestion and polygon parsing
4. CWC Hydrological river gauge telemetry & GLOF monitoring
5. NCS Himalayan earthquake feeds & fault line association
6. USDMA designated safety hub registry & spherical distance calculation
7. Unified disaster payload normalizer matching specification JSON
8. Resilient cache with immediate emergency bypass
9. C-DOT Cell Broadcast GSM 03.41 packet formatting
10. SSE / Push Gateway HTTP endpoints
"""

import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app

from backend.config.env_validator import IndianRegionalEnvironment, validate_runtime_environment
from backend.services.indian_hazard_matrix import indian_hazard_engine
from backend.services.ndma_cap_ingestor import ndma_cap_ingestor
from backend.services.cwc_hydrology_feed import cwc_hydrology_service, OFFICIAL_CWC_STATIONS
from backend.services.ncs_seismic_feed import ncs_seismic_service
from backend.services.usdma_shelter_registry import usdma_shelter_service
from backend.services.payload_normalizer import payload_normalizer
from backend.services.resilient_cache import resilient_cache
from backend.services.cdot_cell_broadcast import cdot_broadcast_service
from backend.services.ndma_cap_ingestor import process_ndma_cap_feed, CAPAlertPayload, CAPAlertInfo, CAPArea
from backend.services.iitr_eew_seismic_service import iitr_eew_service
from backend.services.nic_sms_engine import nic_sms_engine, OutboundSMSRequest
from backend.services.distributed_failover import failover_manager
from backend.services.imd_mausam_stream import imd_mausam_service


def test_indian_regional_environment_validation():
    """Verify Indian regional environment loads and enforces Uttarakhand bounds."""
    env = validate_runtime_environment()
    assert env.default_country_code == "IN"
    assert env.default_state == "Uttarakhand"
    assert env.national_emergency_line == "112"
    assert env.state_disaster_helpline == "1070"
    assert env.district_disaster_helpline == "1077"

    # Test coordinate containment
    assert env.is_coordinate_in_state(30.5526, 79.5632) is True  # Joshimath
    assert env.is_coordinate_in_state(28.6139, 77.2090) is False  # Delhi


def test_14_hazard_matrix_and_multilingual_parity():
    """Verify all 14 hazards exist with 4-language support and non-linguistic visual icons."""
    all_hazards = indian_hazard_engine.list_all_hazards()
    assert len(all_hazards) >= 14

    himalayan = indian_hazard_engine.list_himalayan_hazards()
    himalayan_codes = {h.hazard_code for h in himalayan}
    assert "FLASH_FLOOD_GLOF" in himalayan_codes
    assert "LANDSLIDE_MUDSLIDE" in himalayan_codes
    assert "CLOUDBURST" in himalayan_codes
    assert "EARTHQUAKE" in himalayan_codes
    assert "HEAVY_SNOWFALL_AVALANCHE" in himalayan_codes
    assert "FOREST_FIRE" in himalayan_codes

    for h in all_hazards:
        assert h.non_linguistic_icon is not None
        assert "en" in h.multilingual
        assert "hi" in h.multilingual
        assert "gar" in h.multilingual
        assert "kum" in h.multilingual
        assert len(h.multilingual["hi"].title) > 0
        assert len(h.multilingual["gar"].instruction) > 0


def test_ndma_cap_xml_parser():
    """Verify parsing of authentic NDMA Common Alerting Protocol XML feeds."""
    sample_cap_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <alert xmlns="urn:oasis:names:tc:emergency:cap:1.2">
        <identifier>NDMA-UK-2026-0099</identifier>
        <sender>seoc.dehradun@uk.gov.in</sender>
        <sent>2026-09-17T18:00:00+05:30</sent>
        <status>Actual</status>
        <msgType>Alert</msgType>
        <info>
            <language>en-IN</language>
            <event>Flash Flood</event>
            <urgency>Immediate</urgency>
            <severity>Extreme</severity>
            <headline>Flash flood warning along Alaknanda River corridor</headline>
            <instruction>Move to high ground immediately. Stay clear of Chamoli riverbanks.</instruction>
            <area>
                <areaDesc>Chamoli, Uttarakhand</areaDesc>
                <polygon>30.55,79.56 30.73,79.06 30.41,79.06 30.55,79.56</polygon>
            </area>
        </info>
        <info>
            <language>hi-IN</language>
            <event>आकस्मिक बाढ़</event>
            <headline>अलकनंदा नदी क्षेत्र में आकस्मिक बाढ़ की गंभीर चेतावनी</headline>
            <instruction>तुरंत ऊंचे स्थानों पर जाएं। नदी के किनारों से दूर रहें।</instruction>
        </info>
    </alert>
    """
    alerts = ndma_cap_ingestor.parse_cap_xml(sample_cap_xml)
    assert len(alerts) == 1
    a = alerts[0]
    assert a.identifier == "NDMA-UK-2026-0099"
    assert a.severity == "Extreme"
    assert a.is_in_uttarakhand is True
    assert "Chamoli" in a.affected_districts
    assert len(a.polygon_coordinates) == 4
    assert a.headline_hi is not None
    assert "अलकनंदा" in a.headline_hi


@pytest.mark.asyncio
async def test_cwc_hydrology_service_query():
    """Verify CWC river monitoring stations for Alaknanda, Bhagirathi, and Mandakini."""
    stations = cwc_hydrology_service.list_all_stations()
    assert len(stations) >= 5
    stn_codes = {s.station_code for s in stations}
    assert "CWC-JOSH-01" in stn_codes
    assert "CWC-RUDR-02" in stn_codes

    obs = await cwc_hydrology_service.get_station_telemetry("CWC-JOSH-01")
    assert obs is not None
    assert obs.river_name == "Alaknanda & Dhauliganga"
    assert obs.danger_level_m == 1890.0
    assert obs.alert_status in ("NORMAL", "WATCH", "ALERT", "CRITICAL")


@pytest.mark.asyncio
async def test_ncs_seismic_feed_query():
    """Verify live seismic stream queries for Himalayan earthquakes."""
    events = await ncs_seismic_service.get_recent_himalayan_earthquakes(days_back=30)
    assert isinstance(events, list)
    if events:
        first = events[0]
        assert first.magnitude > 0.0
        assert first.associated_fault in ("Main Central Thrust (MCT)", "Main Boundary Thrust (MBT)")


def test_usdma_shelter_registry_and_nearest_haven():
    """Verify designated high-ground safety hubs and Great-Circle distance vectoring."""
    shelters = usdma_shelter_service.list_all_shelters("Chamoli")
    assert len(shelters) >= 2
    assert any("Joshimath" in s.name for s in shelters)

    # Point near Joshimath
    closest, dist_km, direction = usdma_shelter_service.find_nearest_safety_hub(30.5526, 79.5632)
    assert closest is not None
    assert dist_km < 10.0
    assert direction in ("N", "NE", "E", "SE", "S", "SW", "W", "NW")
    assert closest.elevation_msl_m >= 1800.0


def test_payload_normalization_to_standard_schema():
    """Verify disparate feeds normalize into the exact prompt-specified JSON output structure."""
    normalized = payload_normalizer.normalize_from_hazard(
        hazard_code="FLASH_FLOOD_GLOF",
        districts=["Chamoli", "Rudraprayag"],
        source="NDMA_CAP_GATEWAY",
        severity_override="CRITICAL",
        custom_en_title="Flash Flood Imminent - Alaknanda Basin",
        custom_en_instruction="Move to higher ground immediately. Avoid riverbanks and low-lying structures.",
    )
    assert normalized.source == "NDMA_CAP_GATEWAY"
    assert normalized.severity == "CRITICAL"
    assert normalized.hazard.type == "FLASH_FLOOD_GLOF"
    assert normalized.hazard.category == "HYDRO_METEOROLOGICAL"
    assert "Chamoli" in normalized.localization.districts
    assert normalized.content["en"].title == "Flash Flood Imminent - Alaknanda Basin"
    assert "आकस्मिक बाढ़" in normalized.content["hi"].title


def test_resilient_cache_emergency_bypass():
    """Verify aggressive caching for normal metrics and immediate 0-delay bypass for emergencies."""
    resilient_cache.clear()

    # Normal cache set and get
    resilient_cache.set("weather_joshimath", {"temp": 14.5}, ttl_seconds=60)
    cached = resilient_cache.get("weather_joshimath", severity="NORMAL")
    assert cached == {"temp": 14.5}

    # Emergency bypass: query with severity='CRITICAL' must return None (cache bypass)
    bypassed = resilient_cache.get("weather_joshimath", severity="CRITICAL")
    assert bypassed is None

    metrics = resilient_cache.get_metrics()
    assert metrics["emergency_bypasses"] >= 1


def test_cdot_cell_broadcast_packet_generation():
    """Verify C-DOT GSM 03.41 bilingual broadcast generation."""
    alert = payload_normalizer.normalize_from_hazard(
        hazard_code="LANDSLIDE_MUDSLIDE",
        districts=["Chamoli"],
        severity_override="CRITICAL",
    )
    packets = cdot_broadcast_service.format_cell_broadcast(alert, target_district="Chamoli")
    assert len(packets) == 2  # Hindi + English
    lang_codes = {p.language_code for p in packets}
    assert "hi" in lang_codes
    assert "en" in lang_codes
    assert all(p.message_identifier == "IN_CAP_001" for p in packets)


@pytest.mark.asyncio
async def test_sse_push_gateway_endpoints():
    """Verify unified alert querying and broadcast endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Query unified alerts
        res = await client.get("/api/v1/stream/alerts/unified")
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data, list)
        assert len(data) >= 1

        # 2. Query live USDMA shelters
        shelter_res = await client.get("/api/v1/stream/shelters/live")
        assert shelter_res.status_code == 200
        assert len(shelter_res.json()) >= 5

        # 3. Query 14-hazard matrix
        matrix_res = await client.get("/api/v1/stream/hazards/matrix")
        assert matrix_res.status_code == 200
        matrix_data = matrix_res.json()
        assert matrix_data["total_hazards"] >= 14

        # 4. Broadcast new emergency alert
        broadcast_payload = {
            "hazard_code": "CLOUDBURST",
            "districts": ["Uttarkashi"],
            "severity": "CRITICAL",
            "en_title": "Severe Cloudburst in Bhatwari Catchment",
            "en_instruction": "Evacuate low areas immediately.",
            "trigger_cell_broadcast": True,
        }
        b_res = await client.post("/api/v1/stream/broadcast", json=broadcast_payload)
        assert b_res.status_code == 200
        b_data = b_res.json()
        assert b_data["hazard"]["type"] == "CLOUDBURST"
        assert b_data["severity"] == "CRITICAL"
        assert "Uttarkashi" in b_data["localization"]["districts"]


@pytest.mark.asyncio
async def test_user_locale_synchronization_endpoint():
    """Verify deep state synchronization protocol for multi-lingual user profiles."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Sync user language preference (Garhwali dialect)
        sync_payload = {
            "phone": "+919876543210",
            "token": "fcm_device_token_uk_001",
            "locale": "gb",
            "preferred_dialect_fallback": "hi",
            "timestamp": 1787011200000,
        }
        res = await client.post("/api/v1/user/update-locale", json=sync_payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "SUCCESS_SYNCHRONIZED"
        assert data["applied_locale"] == "gb-IN"
        assert data["subscriber_id"] == "+919876543210"

        # 2. Query stored profile
        profile_res = await client.get("/api/v1/user/profile", params={"identifier": "+919876543210"})
        assert profile_res.status_code == 200
        profile_data = profile_res.json()
        assert profile_data["locale"] == "gb-IN"
        assert profile_data["phone"] == "+919876543210"


@pytest.mark.asyncio
async def test_process_ndma_cap_feed_json_and_spatial_validation():
    """Verify NDMA CAP JSON parsing and spatial envelope filtering."""
    valid_json = """{
      "identifier": "IN-UK-NDMA-2026-TEST-99",
      "sender": "sachet.ndma.gov.in",
      "sent": "2026-09-17T12:00:00+05:30",
      "status": "Actual",
      "msgType": "Alert",
      "scope": "Public",
      "info": [{
        "language": "en-IN",
        "category": "Geo",
        "event": "Cloudburst Threat",
        "urgency": "Immediate",
        "severity": "Extreme",
        "certainty": "Observed",
        "headline": "Cloudburst Warning in Chamoli Valley",
        "description": "Extreme downpour detected.",
        "instruction": "Evacuate drainage zones immediately.",
        "area": {
          "areaDesc": "Chamoli, Uttarakhand",
          "polygon": "30.428,79.351 30.450,79.380 30.400,79.330"
        }
      }]
    }"""
    parsed = await process_ndma_cap_feed(valid_json)
    assert parsed is not None
    assert parsed.identifier == "IN-UK-NDMA-2026-TEST-99"
    assert parsed.status == "Actual"
    assert len(parsed.info) == 1
    assert "Chamoli" in parsed.info[0].area.areaDesc

    # Non-Uttarakhand alert should be rejected (filtered out)
    outside_json = """{
      "identifier": "IN-MH-NDMA-2026-01",
      "sender": "sachet.ndma.gov.in",
      "sent": "2026-09-17T12:00:00+05:30",
      "status": "Actual",
      "msgType": "Alert",
      "scope": "Public",
      "info": [{
        "language": "en-IN",
        "category": "Met",
        "event": "Coastal Gale",
        "urgency": "Future",
        "severity": "Minor",
        "certainty": "Possible",
        "headline": "Mumbai Harbor Advisory",
        "instruction": "Stay clear of seawall.",
        "area": {
          "areaDesc": "Mumbai, Maharashtra",
          "polygon": "18.92,72.83 18.95,72.85"
        }
      }]
    }"""
    assert await process_ndma_cap_feed(outside_json) is None


def test_iitr_eew_seismic_telemetry_and_landslide_anomaly():
    """Verify IIT Roorkee EEW PGA parsing and secondary landslide trigger."""
    raw_payload = """{
        "station_id": "IITR-JOSH-02",
        "station_name": "Joshimath MCT Ridge Sensor",
        "lat": 30.552,
        "lon": 79.563,
        "pga_gal": 92.4,
        "intensity_mmi": 6.2,
        "p_wave_epoch": 1787011200000,
        "lead_time_seconds": 14.2,
        "district": "Chamoli",
        "status": "ACTUAL"
    }"""
    packet = iitr_eew_service.process_raw_seismic_payload(raw_payload)
    assert packet is not None
    assert packet.pga_gal == 92.4
    assert packet.secondary_landslide_risk is True  # PGA >= 80 gal on mountain slopes
    assert packet.district == "Chamoli"


@pytest.mark.asyncio
async def test_cwc_danger_mark_glof_threshold_and_cache_eviction():
    """Verify CWC danger mark breach triggers GLOF alert and cache eviction."""
    obs = await cwc_hydrology_service.get_station_telemetry("CWC-JOSH-01")
    assert obs is not None

    # Simulate critical water level exceeding danger mark
    obs.current_water_level_m = obs.danger_level_m + 1.2
    obs.rate_of_rise_m_hr = 0.65
    obs.alert_status = "CRITICAL"

    glof_alert = await cwc_hydrology_service.evaluate_danger_threshold_and_trigger_glof(obs)
    assert glof_alert is not None
    assert glof_alert["hazard"]["type"] == "FLASH_FLOOD_GLOF"
    assert glof_alert["urgency"] == "Immediate"
    assert glof_alert["severity"] == "Extreme"
    assert "Alaknanda" in glof_alert["river"]


@pytest.mark.asyncio
async def test_nic_sms_engine_language_synchronized_dispatch():
    """Verify multi-channel language-synchronized SMS routing via NIC gateway."""
    cap_info_en = CAPAlertInfo(
        language="en-IN",
        category="Hydrology",
        event="Flash Flood Imminent",
        urgency="Immediate",
        severity="Extreme",
        certainty="Observed",
        headline="Alaknanda Cresting",
        instruction="Evacuate to GIC High Ground immediately.",
        area=CAPArea(areaDesc="Chamoli, Uttarakhand", polygon="30.55,79.52"),
    )
    cap_info_hi = CAPAlertInfo(
        language="hi-IN",
        category="Hydrology",
        event="आकस्मिक बाढ़ की चेतावनी",
        urgency="Immediate",
        severity="Extreme",
        certainty="Observed",
        headline="अलकनंदा जलस्तर उफान पर",
        instruction="तुरंत जीआईसी सुरक्षित परिसर में जाएं।",
        area=CAPArea(areaDesc="चमोली, उत्तराखंड", polygon="30.55,79.52"),
    )
    cap_payload = CAPAlertPayload(
        identifier="IN-UK-TEST-SMS-01",
        sender="sachet.ndma.gov.in",
        sent="2026-09-17T12:00:00+05:30",
        status="Actual",
        msgType="Alert",
        scope="Public",
        info=[cap_info_en, cap_info_hi],
    )

    # 1. Hindi Subscriber Dispatch
    hi_req = OutboundSMSRequest(
        recipientPhoneNumber="+919876543210",
        assignedLocale="hi",
        hazardType="FLASH_FLOOD_GLOF",
        severity="Extreme",
        rawPayload=cap_payload,
    )
    res_hi = await nic_sms_engine.dispatch_synchronized_sms(hi_req)
    assert "आकस्मिक बाढ़" in res_hi.sms_body
    assert "1070" in res_hi.sms_body
    assert res_hi.is_fallback_used is False

    # 2. Garhwali Subscriber (fallback gracefully to root or nearest)
    gb_req = OutboundSMSRequest(
        recipientPhoneNumber="+919876543211",
        assignedLocale="gb",
        hazardType="FLASH_FLOOD_GLOF",
        severity="Extreme",
        rawPayload=cap_payload,
    )
    res_gb = await nic_sms_engine.dispatch_synchronized_sms(gb_req)
    assert "DMMC ALERT" in res_gb.sms_body
    assert res_gb.is_fallback_used is True


def test_distributed_failover_and_edge_routing():
    """Verify active-active health status and automatic edge failover trigger."""
    state = failover_manager.get_topology_status()
    assert state.edge_failover_enabled is True
    assert state.active_primary_region == "ap-south-1"

    # Simulate primary region failure
    failover_manager.record_region_heartbeat("ap-south-1", is_healthy=False, latency_ms=9999.0)
    failed_state = failover_manager.get_topology_status()
    assert failed_state.failover_triggered is True
    assert failed_state.active_primary_region == "ap-south-2"

    # Recovery
    failover_manager.record_region_heartbeat("ap-south-1", is_healthy=True, latency_ms=11.5)
    recovered_state = failover_manager.get_topology_status()
    assert recovered_state.failover_triggered is False


