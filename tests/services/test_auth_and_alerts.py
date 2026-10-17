"""
Tests for Auth Service, UNet Segmentation, and Alert Dispatching Subsystems
"""

import pytest
from backend.services.auth import (
    auth_service,
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)
from backend.services.unet_segmentation import (
    unet_segmentation_service,
    SegmentationRequest,
)
from backend.services.alert_dispatch import (
    alert_dispatch_service,
    AlertPayload,
)


class TestAuthService:
    def test_password_hashing_and_verification(self):
        pwd = "SecurePassword2024!"
        hashed = hash_password(pwd)
        assert hashed != pwd
        assert verify_password(pwd, hashed) is True
        assert verify_password("WrongPassword!", hashed) is False

    def test_jwt_token_flow(self):
        token = create_access_token("usr-123", "test_user", "OPERATOR")
        assert token is not None
        payload = decode_access_token(token)
        assert payload["sub"] == "usr-123"
        assert payload["username"] == "test_user"
        assert payload["role"] == "OPERATOR"

    def test_user_authentication(self):
        user = auth_service.authenticate_user("admin", "AdminSecure2024!")
        assert user is not None
        assert user.role == "ADMIN"

        wrong_user = auth_service.authenticate_user("admin", "BadPassword")
        assert wrong_user is None


class TestUNetSegmentationService:
    def test_segmentation_pipeline(self):
        req = SegmentationRequest(
            center_lat=26.02,
            center_lon=89.98,
            rainfall_intensity_mm_hr=45.0,
            river_stage_meters=29.5,
            soil_saturation_index=0.92,
        )
        res = unet_segmentation_service.segment_inundation_grid(req)
        assert res.model_name == "UNet-HydroSegmentation-DeepNetwork"
        assert res.inundated_cells_count > 0
        assert res.max_estimated_depth_meters > 0.0
        assert "features" in res.geojson_extent


class TestAlertDispatchService:
    def test_alert_dispatch_and_cap_xml(self):
        payload = AlertPayload(
            risk_level="CRITICAL",
            region="Chamoli Town Center",
            latitude=30.5564,
            longitude=79.5670,
            reason="Convective cloudburst surge exceeded +1.4m/hr rate of rise.",
            prediction_horizon_minutes=45,
        )
        record = alert_dispatch_service.dispatch_alert(payload)
        assert record.status == "ACTIVE"
        assert len(record.dispatch_logs) > 0

        # Verify CAP v1.2 XML output
        xml = alert_dispatch_service.generate_cap_xml(record.alert_id)
        assert "urn:oasis:names:tc:emergency:cap:1.2" in xml
        assert "Chamoli Town Center" in xml
        assert "<severity>Extreme</severity>" in xml
