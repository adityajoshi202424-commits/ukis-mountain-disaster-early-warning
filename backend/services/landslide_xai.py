"""Real-model landslide inference and SHAP explanations.

The model is loaded from a configured artifact. Without that artifact this
service fails visibly instead of producing a default or synthetic score.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


FEATURE_NAMES = [
    "rainfall_72h_mm",
    "slope_angle_deg",
    "aspect_deg",
    "soil_type_index",
    "elevation_m",
]


class LandslideFeatures(BaseModel):
    rainfall_72h_mm: float = Field(ge=0)
    slope_angle_deg: float = Field(ge=0, le=90)
    aspect_deg: float = Field(ge=0, le=360)
    soil_type_index: float
    elevation_m: float = Field(ge=-500, le=9000)


class FeatureContribution(BaseModel):
    feature: str
    value: float
    shap_value: float


class LandslideInference(BaseModel):
    risk_score: float = Field(ge=0, le=1)
    confidence_interval: tuple[float, float]
    contributions: List[FeatureContribution]
    rationale: str
    model_artifact: str


class LandslideModelUnavailable(RuntimeError):
    """Raised when a trained artifact or its runtime dependency is unavailable."""


class LandslideXAIService:
    """Loads a trained tree model and explains inference with SHAP."""

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = Path(model_path or os.getenv("LANDSLIDE_MODEL_PATH", ""))
        self._model = None
        self._explainer = None

    def _load(self):
        if not self.model_path or not self.model_path.is_file():
            from backend.services.landslide_ml_engine import MODEL_FILE, landslide_predictor
            if MODEL_FILE.exists():
                self.model_path = MODEL_FILE
            else:
                try:
                    landslide_predictor.get_model()
                    self.model_path = MODEL_FILE
                except Exception:
                    raise LandslideModelUnavailable(
                        "LANDSLIDE_MODEL_PATH is not configured with an existing trained model artifact"
                    )
        if self._model is None:
            try:
                import joblib
                import shap
                self._model = joblib.load(self.model_path)
                self._explainer = shap.TreeExplainer(self._model)
            except Exception as error:
                raise LandslideModelUnavailable(
                    f"Unable to load landslide model or SHAP explainer: {type(error).__name__}"
                ) from error

    def predict(self, features: LandslideFeatures) -> LandslideInference:
        self._load()
        import numpy as np

        values = np.array([[getattr(features, name) for name in FEATURE_NAMES]], dtype=float)
        probabilities = self._model.predict_proba(values)[0]
        risk_score = float(probabilities[-1])
        shap_values = self._explainer.shap_values(values)
        if isinstance(shap_values, list):
            shap_row = np.asarray(shap_values[-1])[0]
        elif hasattr(shap_values, "shape") and len(shap_values.shape) == 3:
            shap_row = np.asarray(shap_values)[0, :, 1]
        else:
            shap_row = np.asarray(shap_values)[0]
        contributions = sorted(
            [
                FeatureContribution(feature=name, value=float(values[0][index]), shap_value=float(shap_row[index]))
                for index, name in enumerate(FEATURE_NAMES)
            ],
            key=lambda item: abs(item.shap_value),
            reverse=True,
        )
        margin = max(0.0, min(0.5, float(np.std(probabilities))))
        top = contributions[:2]
        rationale = "; ".join(
            f"{item.feature} contributed {item.shap_value:+.3f} (value {item.value:.2f})"
            for item in top
        )
        return LandslideInference(
            risk_score=risk_score,
            confidence_interval=(max(0.0, risk_score - margin), min(1.0, risk_score + margin)),
            contributions=contributions,
            rationale=rationale,
            model_artifact=str(self.model_path),
        )


landslide_xai_service = LandslideXAIService()