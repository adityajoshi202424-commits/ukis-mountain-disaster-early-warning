"""
Comprehensive Test Suite for Uttarakhand AI Mountain Disaster Early-Warning Intelligence Platform.
UKIS Problem Statement P-011.

Validates all 4 Core Tasks:
Task 1: PostGIS Schema (geoalchemy2), Authentic Settlements, Weather 72h Stream, Satellite Fetcher
Task 2: Monsoonal Landslide Predictor (RF active inference), DEM rasterio/pyproj parsing, OpenCV NDWI GLOF Sentinel, Downslope Vector RED_ALERT Escalation
Task 3: Hyper-Localized SHAP TreeExplainer, Top 2 Feature Drivers, Exact Template String Rendering
Task 4: OASIS CAP v1.2 XML Serialization, Minimal Minified Sync Vector Endpoint
"""

import math
import numpy as np
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.spatial_models import (
    Village,
    Lifeline,
    HazardZone,
    UTTARAKHAND_SETTLEMENTS,
    UTTARAKHAND_LIFELINES,
)
from backend.services.environmental_streams import (
    UTTARAKHAND_BBOX,
    is_within_uttarakhand,
    weather_stream_service,
    satellite_fetcher_service,
)
from backend.services.landslide_ml_engine import (
    landslide_predictor,
    dem_parser,
    LandslideInputVector,
    FEATURE_NAMES,
)
from backend.services.landslide_xai_explainer import (
    landslide_xai_engine,
)
from backend.services.glof_sentinel import (
    glof_sentinel_service,
    GLACIAL_LAKE_REGISTRY,
)
from backend.services.geospatial_action import (
    compute_downslope_vector,
)
from backend.services.cap_serializer import (
    OASISCAPSerializer,
    CAPAlertInput,
    CAP_NS,
)


client = TestClient(app)


# ---------------------------------------------------------------------------
# Task 1: PostGIS Schema & Operational Bounds Tests
# ---------------------------------------------------------------------------

def test_operational_bounds_and_settlements():
    """Verify target bounding box [77.57, 28.72, 81.04, 31.46] and authentic Uttarakhand settlements."""
    # Bounding box limits
    assert UTTARAKHAND_BBOX["min_lon"] == 77.57
    assert UTTARAKHAND_BBOX["min_lat"] == 28.72
    assert UTTARAKHAND_BBOX["max_lon"] == 81.04
    assert UTTARAKHAND_BBOX["max_lat"] == 31.46

    # Test settlement coordinates
    for village in UTTARAKHAND_SETTLEMENTS:
        assert is_within_uttarakhand(village["latitude"], village["longitude"]) is True
        assert village["elevation_m"] >= 600

    # Test out-of-bounds rejection
    assert is_within_uttarakhand(26.14, 91.73) is False  # Outside Uttarakhand (Guwahati)
    assert is_within_uttarakhand(28.61, 77.20) is False  # Delhi


def test_critical_transit_corridors_registered():
    """Verify lifelines contain NH-58, NH-94, NH-107, NH-34."""
    corridor_names = " ".join([l["name"] for l in UTTARAKHAND_LIFELINES])
    assert "NH-58" in corridor_names
    assert "NH-107" in corridor_names
    assert "NH-94" in corridor_names
    assert "NH-34" in corridor_names


# ---------------------------------------------------------------------------
# Task 2: Monsoonal Landslide Predictor & DEM Parsing Tests
# ---------------------------------------------------------------------------

def test_landslide_active_inference():
    """Active inference wrapper expects [72hr_cumulative_rainfall, slope_angle, aspect, soil_type_index, elevation]."""
    # High risk input: steep slope (42 deg) + heavy monsoonal rain (150mm) on weathered colluvium
    vector = LandslideInputVector(
        rainfall_72h_mm=150.0,
        slope_angle_deg=42.0,
        aspect_deg=190.0,
        soil_type_index=4.0,
        elevation_m=2300.0,
    )
    result = landslide_predictor.predict(vector)

    assert result.risk_score >= 0.70
    assert result.risk_percentage >= 70.0
    assert result.risk_level in ["HIGH", "CRITICAL"]
    assert 0.0 <= result.confidence_interval[0] <= result.confidence_interval[1] <= 1.0
    assert len(result.input_features) == 5


def test_dem_rasterio_pyproj_parsing():
    """Slope and aspect must be parsed directly from DEM data using rasterio and pyproj."""
    metrics = dem_parser.parse_terrain(30.5574, 79.5658)  # Joshimath
    assert metrics.elevation_m > 1000.0
    assert 0.0 <= metrics.slope_angle_deg <= 89.0
    assert 0.0 <= metrics.aspect_deg <= 360.0
    assert "4326" in metrics.crs or "EPSG" in metrics.crs


# ---------------------------------------------------------------------------
# Task 2: Proactive GLOF Sentinel (OpenCV NDWI & >15% Area Delta) Tests
# ---------------------------------------------------------------------------

def test_glof_sentinel_ndwi_opencv_segmentation():
    """Test OpenCV NDWI computation, thresholding, and surface area measurement."""
    # Synthetic 50x50 Sentinel-2 bands B3 (Green) and B8 (NIR)
    b3_green = np.full((50, 50), 0.1, dtype=np.float32)
    b8_nir = np.full((50, 50), 0.3, dtype=np.float32)

    # Insert a glacial lake in the center: Green high (0.45), NIR low (0.05) -> NDWI = (0.45 - 0.05)/(0.5) = 0.8
    b3_green[15:35, 15:35] = 0.45
    b8_nir[15:35, 15:35] = 0.05

    metrics, mask = glof_sentinel_service.segment_water_body(
        b3_green, b8_nir, lake_name="Chorabari Lake (Gandhi Sarovar)", pixel_resolution_m=10.0
    )

    assert 390 <= metrics.pixel_count <= 400
    assert 39000.0 <= metrics.surface_area_m2 <= 40000.0
    assert metrics.mean_ndwi > 0.50
    assert mask.shape == (50, 50)


def test_glof_consecutive_pass_delta_alerting():
    """Triggers RED_ALERT when surface area changes by > 15%."""
    # Pass 0: 40,000 m²
    # Pass 1: 52,000 m² (+30% rapid expansion)
    alert_expansion = glof_sentinel_service.evaluate_glof_alert(
        previous_area_m2=40000.0,
        current_area_m2=52000.0,
        lake_name="Chorabari Lake (Gandhi Sarovar)",
        threshold_percentage=15.0,
    )
    assert alert_expansion.alert_triggered is True
    assert alert_expansion.severity == "RED_ALERT"
    assert alert_expansion.event_classification == "RAPID_EXPANSION"
    assert alert_expansion.change_percentage == 30.0

    # Pass 2: 12,000 m² (-70% sudden catastrophic moraine breach drainage)
    alert_drainage = glof_sentinel_service.evaluate_glof_alert(
        previous_area_m2=40000.0,
        current_area_m2=12000.0,
        lake_name="Rishiganga Upper Tarn",
        threshold_percentage=15.0,
    )
    assert alert_drainage.alert_triggered is True
    assert alert_drainage.severity == "RED_ALERT"
    assert alert_drainage.event_classification == "SUDDEN_CATASTROPHIC_DRAINAGE"
    assert alert_drainage.change_percentage == -70.0

    # Stable pass: +5% (below 15% threshold)
    alert_stable = glof_sentinel_service.evaluate_glof_alert(
        previous_area_m2=40000.0,
        current_area_m2=42000.0,
        lake_name="Vasudhara Glacial Tarn",
        threshold_percentage=15.0,
    )
    assert alert_stable.alert_triggered is False
    assert alert_stable.severity == "NORMAL"


# ---------------------------------------------------------------------------
# Task 2: Intersection Logic & Downslope Vector Escalation
# ---------------------------------------------------------------------------

def test_downslope_vector_red_alert_escalation():
    """
    If a hazard polygon sits topographically upslope of a populated settlement
    within proximity, immediately compute downslope vector and escalate to RED_ALERT.
    """
    # Hazard centroid (elev 2350m) sitting 475m higher than Village centroid (elev 1875m)
    vector = compute_downslope_vector(
        hazard_lat=30.5630,
        hazard_lon=79.5660,
        hazard_elev_m=2350.0,
        village_lat=30.5574,
        village_lon=79.5658,
        village_elev_m=1875.0,
    )

    assert vector["is_upslope"] is True
    assert vector["elevation_drop_meters"] == 475.0
    assert vector["distance_meters"] > 0
    assert vector["threat_level"] == "RED_ALERT"
    assert "topographically upslope" in vector["downslope_rationale"]


# ---------------------------------------------------------------------------
# Task 3: Hyper-Localized Explainable AI (SHAP & Template Engine)
# ---------------------------------------------------------------------------

def test_shap_explanation_and_exact_human_readable_template():
    """
    SHAP TreeExplainer must extract top 2 feature contributions and format output:
    'Risk score is {risk_score}% because the 72-hour cumulative rainfall ({rain_val}mm)
     has crossed the critical threshold on a {slope_val}-degree unstable slope directly
     outside Village {village_name}.'
    """
    vector = LandslideInputVector(
        rainfall_72h_mm=145.0,
        slope_angle_deg=39.0,
        aspect_deg=195.0,
        soil_type_index=4.0,
        elevation_m=2150.0,
    )
    exp = landslide_xai_engine.explain(vector, village_name="Mana")

    assert len(exp.top_feature_contributions) == 2
    # Verify exact required template elements
    text = exp.human_readable_explanation
    assert "Risk score is " in text
    assert "because the 72-hour cumulative rainfall (145mm) has crossed the critical threshold on a 39-degree unstable slope directly outside Village Mana." in text
    assert "hi" in exp.localized_dialects
    assert "gar" in exp.localized_dialects


# ---------------------------------------------------------------------------
# Task 4: OASIS CAP v1.2 Standard XML Serialization
# ---------------------------------------------------------------------------

def test_oasis_cap_xml_serialization_and_parsing():
    """
    Serializes into valid OASIS CAP v1.2 XML with all mandatory tags:
    <alert>, <identifier>, <sender>, <sent>, <status>Actual</status>, <msgType>Alert</msgType>, <scope>Public</scope>,
    <info>: <headline>, <description>, <urgency>Immediate</urgency>, <severity>Extreme</severity>,
            <area><areaDesc>, <circle>.
    """
    xml_output = OASISCAPSerializer.serialize_alert(
        sender="usdma-control@uk.gov.in",
        headline="Urgent Mountain Landslide Warning",
        description="High monsoonal slope destabilization threatening Mana access lifeline.",
        area_description="Mana Pass Corridor, Chamoli",
        latitude=30.7674,
        longitude=79.4958,
        radius_km=5.0,
        severity="Extreme",
        urgency="Immediate",
        status="Actual",
        msg_type="Alert",
        scope="Public",
    )

    assert xml_output.startswith('<?xml version="1.0" encoding="UTF-8"?>')
    assert f'xmlns="{CAP_NS}"' in xml_output
    assert "<status>Actual</status>" in xml_output
    assert "<msgType>Alert</msgType>" in xml_output
    assert "<scope>Public</scope>" in xml_output
    assert "<urgency>Immediate</urgency>" in xml_output
    assert "<severity>Extreme</severity>" in xml_output
    assert "<areaDesc>Mana Pass Corridor, Chamoli</areaDesc>" in xml_output
    assert "<circle>30.76740,79.49580,5.0</circle>" in xml_output

    # Roundtrip parsing verification
    parsed = OASISCAPSerializer.parse_cap_xml(xml_output)
    assert parsed["sender"] == "usdma-control@uk.gov.in"
    assert parsed["headline"] == "Urgent Mountain Landslide Warning"
    assert parsed["status"] == "Actual"
    assert parsed["urgency"] == "Immediate"
    assert "30.76740,79.49580,5.0" in parsed["circle"]


# ---------------------------------------------------------------------------
# Task 4: Compact Payload & Offline Optimization (/sync/alerts/minimal)
# ---------------------------------------------------------------------------

def test_minimal_alert_sync_endpoint():
    """
    API route /api/v1/sync/alerts/minimal returns compressed raw JSON array
    for low-bandwidth (2G / Satellite) transmissions and IndexedDB / localStorage caching.
    """
    response = client.get("/api/v1/sync/alerts/minimal")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    # Check structure of vector elements: [alert_id, risk_level, region, lat, lon, created, expires]
    row = data[0]
    assert len(row) == 7
    assert isinstance(row[0], str)  # alert_id
    assert row[1] in ["GREEN", "YELLOW", "ORANGE", "RED", "HIGH", "CRITICAL", "WATCH"]  # risk_level
    assert isinstance(row[2], str)  # region
    assert 28.72 <= row[3] <= 31.46  # latitude
    assert 77.57 <= row[4] <= 81.04  # longitude


# ---------------------------------------------------------------------------
# Full REST API Endpoint Integration Tests
# ---------------------------------------------------------------------------

def test_api_landslide_xai_explain_endpoint():
    """POST /api/v1/risk/landslide/explain endpoint validation."""
    payload = {
        "rainfall_72h_mm": 130.0,
        "slope_angle_deg": 37.0,
        "aspect_deg": 185.0,
        "soil_type_index": 4.0,
        "elevation_m": 2250.0,
        "village_name": "Joshimath",
    }
    response = client.post("/api/v1/risk/landslide/explain", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["village_name"] == "Joshimath"
    assert "Risk score is " in data["human_readable_explanation"]
    assert "outside Village Joshimath." in data["human_readable_explanation"]
    assert len(data["top_feature_contributions"]) == 2


def test_api_glof_sentinel_evaluate_endpoint():
    """POST /api/v1/glof/sentinel/evaluate endpoint validation."""
    payload = {
        "previous_area_m2": 50000.0,
        "current_area_m2": 65000.0,  # +30% expansion
        "lake_name": "Chorabari Lake (Gandhi Sarovar)",
        "threshold_percentage": 15.0,
    }
    response = client.post("/api/v1/glof/sentinel/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["alert_triggered"] is True
    assert data["severity"] == "RED_ALERT"
    assert data["change_percentage"] == 30.0


def test_api_cap_serialize_endpoint():
    """POST /api/v1/cap/serialize endpoint validation."""
    payload = {
        "sender": "usdma-disaster-response@uk.gov.in",
        "headline": "GLOF Flash Flood Red Alert",
        "description": "Glacial lake breach detected. Alaknanda basin evacuate immediately.",
        "area_description": "Raini - Tapovan Corridor",
        "latitude": 30.4905,
        "longitude": 79.6978,
        "radius_km": 10.0,
        "severity": "Extreme",
        "urgency": "Immediate",
    }
    response = client.post("/api/v1/cap/serialize", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert "urn:oasis:names:tc:emergency:cap:1.2" in data["xml_payload"]
    assert data["parsed_metadata"]["urgency"] == "Immediate"
