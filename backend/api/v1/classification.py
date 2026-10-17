"""
AI / Classification API Router (UNet Spatiotemporal Segmentation)

Endpoints:
- POST /api/v1/classification/segment (Runs UNet inference on catchment grid)
"""

from __future__ import annotations

from fastapi import APIRouter
from backend.services.unet_segmentation import (
    unet_segmentation_service,
    SegmentationRequest,
    SegmentationResult,
)

router = APIRouter(prefix="/classification", tags=["classification"])


@router.post("/segment", response_model=SegmentationResult)
async def segment_inundation_extent(payload: SegmentationRequest):
    """
    Executes UNet spatiotemporal flood segmentation on a localized catchment matrix.
    Returns raster cell probabilities, estimated water depths, and GeoJSON boundary.
    """
    return unet_segmentation_service.segment_inundation_grid(payload)
