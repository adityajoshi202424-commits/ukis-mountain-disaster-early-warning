"""Sentinel search and NDWI change analysis with explicit source failures."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

import httpx
from pydantic import BaseModel, Field


class SentinelSearchRequest(BaseModel):
    min_lon: float = Field(ge=77.57, le=81.04)
    min_lat: float = Field(ge=28.72, le=31.46)
    max_lon: float = Field(ge=77.57, le=81.04)
    max_lat: float = Field(ge=28.72, le=31.46)
    start_date: str
    end_date: str
    collection: str = "SENTINEL-2"


class NdwiChange(BaseModel):
    previous_area_m2: float = Field(ge=0)
    current_area_m2: float = Field(ge=0)
    change_percent: float
    threshold_percent: float
    alert: bool
    source: str


class SentinelCatalogService:
    """Queries the Copernicus Data Space catalog; no imagery means no result."""

    catalog_url = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"

    async def search(self, request: SentinelSearchRequest) -> Dict[str, Any]:
        if request.min_lon >= request.max_lon or request.min_lat >= request.max_lat:
            raise ValueError("Sentinel search bounds must have positive area")
        footprint = (
            f"POLYGON(({request.min_lon} {request.min_lat},{request.max_lon} {request.min_lat},"
            f"{request.max_lon} {request.max_lat},{request.min_lon} {request.max_lat},{request.min_lon} {request.min_lat}))"
        )
        query = (
            f"Collection/Name eq '{request.collection}' and "
            f"ContentDate/Start ge {request.start_date}T00:00:00.000Z and "
            f"ContentDate/End le {request.end_date}T23:59:59.999Z and "
            f"OData.CSC.Intersects(area=geography'SRID=4326;{footprint}')"
        )
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.catalog_url, params={"$filter": query, "$top": 100})
                response.raise_for_status()
                return {"status": "AVAILABLE", "source": self.catalog_url, "products": response.json().get("value", [])}
        except (httpx.HTTPError, ValueError) as error:
            return {"status": "SOURCE_UNAVAILABLE", "source": self.catalog_url, "error": str(error), "products": []}

    @staticmethod
    def ndwi_change(previous_green: float, previous_nir: float, current_green: float, current_nir: float, previous_pixel_area_m2: float, current_pixel_area_m2: float, threshold_percent: float = 15.0) -> NdwiChange:
        """Compute NDWI-derived areas supplied by verified Sentinel-2 band processing."""
        def ndwi(green: float, nir: float) -> float:
            denominator = green + nir
            if denominator == 0:
                raise ValueError("NDWI is undefined when Green + NIR is zero")
            return (green - nir) / denominator

        previous_index = ndwi(previous_green, previous_nir)
        current_index = ndwi(current_green, current_nir)
        previous_area = previous_pixel_area_m2 if previous_index > 0 else 0.0
        current_area = current_pixel_area_m2 if current_index > 0 else 0.0
        if previous_area == 0:
            raise ValueError("Cannot calculate lake-area change without a non-zero previous water area")
        change_percent = ((current_area - previous_area) / previous_area) * 100.0
        return NdwiChange(
            previous_area_m2=previous_area,
            current_area_m2=current_area,
            change_percent=change_percent,
            threshold_percent=threshold_percent,
            alert=abs(change_percent) > threshold_percent,
            source="Sentinel-2 Green (B3) / NIR (B8) NDWI",
        )


sentinel_catalog_service = SentinelCatalogService()