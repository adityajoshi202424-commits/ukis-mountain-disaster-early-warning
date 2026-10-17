"""
SIH Demonstration & Evaluation API Router

Endpoints for:
- Historical event catalog
- Chronological zero-leakage simulation replay
- Step-by-step telemetry clock advancement
- Fault-tolerance outage simulation (e.g. CWC gauge failure)
- Counterfactual Scenario simulation (e.g. +20% rainfall offset)
- Data provenance transparency
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Query

from backend.sih.replay_engine import sih_replay_engine
from backend.sih.repository import sih_repository
from backend.sih.models_registry import model_registry

router = APIRouter(prefix="/sih-demo", tags=["sih-evaluation"])


# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------

class ReplayRequest(BaseModel):
    event_id: str = Field(..., description="Unique event identifier from catalog")
    model_version: str = Field(default="ResNet-UNet-v2.4.1", description="Inference model version")
    time_step_minutes: int = Field(default=15, ge=5, le=60, description="Temporal interval for step loop")
    disabled_source_id: Optional[str] = Field(default=None, description="Simulate source outage (e.g. 'CWC_GAUGE')")
    rainfall_offset_pct: float = Field(default=0.0, ge=-50.0, le=100.0, description="Hypothetical scenario rainfall offset %")


class StepRequest(BaseModel):
    event_id: str
    target_timestamp_epoch: int
    model_version: str = "ResNet-UNet-v2.4.1"
    disabled_source_id: Optional[str] = None
    rainfall_offset_pct: float = 0.0


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------

@router.get("/events")
async def list_historical_events():
    """
    Returns available historical events catalog categorized by State and District.
    """
    events = sih_repository.list_events()
    states = sorted(list(set(e.state for e in events)))
    districts = sorted(list(set(e.district for e in events)))

    return {
        "status": "success",
        "states": states,
        "districts": districts,
        "events": [
            {
                "event_id": e.event_id,
                "state": e.state,
                "district": e.district,
                "event_name": e.event_name,
                "simulation_start": e.simulation_start.isoformat(),
                "simulation_end": e.simulation_end.isoformat(),
                "actual_breach_time": e.actual_breach_time.isoformat(),
                "simulation_start_epoch": int(e.simulation_start.timestamp()),
                "simulation_end_epoch": int(e.simulation_end.timestamp()),
                "actual_breach_epoch": int(e.actual_breach_time.timestamp()),
                "description": e.description,
                "center": {"lat": e.center_lat, "lon": e.center_lon},
                "zoom": e.default_zoom,
            }
            for e in events
        ],
    }


@router.get("/models")
async def list_available_models():
    """
    Lists registered prediction models available for evaluation.
    """
    return {
        "status": "success",
        "models": model_registry.list_models(),
    }


@router.get("/data-sources")
async def get_data_sources_provenance():
    """
    Returns authoritative data source provenance documentation for the judge transparency modal.
    """
    return {
        "status": "success",
        "provenance_registry": sih_replay_engine.get_data_sources_provenance(),
    }


@router.post("/replay")
async def run_chronological_replay(payload: ReplayRequest):
    """
    Executes full chronological simulation replay loop.
    Enforces strict zero temporal leakage.
    Returns complete step timeline, objective metrics, lead time, and post-event ground truth.
    """
    try:
        response = sih_replay_engine.execute_historical_replay(
            event_id=payload.event_id,
            model_version=payload.model_version,
            time_step_minutes=payload.time_step_minutes,
            disabled_source_id=payload.disabled_source_id,
            rainfall_offset_pct=payload.rainfall_offset_pct,
        )
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation execution error: {str(e)}")


@router.post("/step")
async def evaluate_single_step(payload: StepRequest):
    """
    Calculates time-gated telemetry features and prediction output at a specific timestamp tick.
    """
    try:
        response = sih_replay_engine.get_single_step(
            event_id=payload.event_id,
            target_timestamp_epoch=payload.target_timestamp_epoch,
            model_version=payload.model_version,
            disabled_source_id=payload.disabled_source_id,
            rainfall_offset_pct=payload.rainfall_offset_pct,
        )
        return {"status": "success", "step_data": response}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Step evaluation error: {str(e)}")
