"""DEM-backed terrain feature extraction for Uttarakhand coordinates."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class TerrainFeatures(BaseModel):
    slope_angle_deg: float = Field(ge=0, le=90)
    aspect_deg: float = Field(ge=0, le=360)
    elevation_m: float
    dem_path: str
    source_crs: str


class TerrainSourceUnavailable(RuntimeError):
    """Raised when the configured real DEM cannot be read."""


def extract_terrain_features(dem_path: str, latitude: float, longitude: float) -> TerrainFeatures:
    """Sample a real DEM and derive local slope/aspect in the DEM CRS."""
    path = Path(dem_path)
    if not path.is_file():
        raise TerrainSourceUnavailable(f"DEM artifact does not exist: {dem_path}")
    try:
        import numpy as np
        import rasterio
        from pyproj import Transformer

        with rasterio.open(path) as dataset:
            transformer = Transformer.from_crs("EPSG:4326", dataset.crs, always_xy=True)
            x, y = transformer.transform(longitude, latitude)
            row, column = dataset.index(x, y)
            if row < 1 or column < 1 or row >= dataset.height - 1 or column >= dataset.width - 1:
                raise TerrainSourceUnavailable("Coordinate is too close to the DEM edge for a 3x3 slope window")
            window = dataset.read(1, window=rasterio.windows.Window(column - 1, row - 1, 3, 3), masked=True)
            if np.ma.is_masked(window) or np.any(~np.isfinite(window.filled(np.nan))):
                raise TerrainSourceUnavailable("DEM window contains nodata values")
            elevation = float(window[1, 1])
            pixel_x, pixel_y = dataset.res
            dz_dy, dz_dx = np.gradient(window.astype(float), abs(pixel_y), abs(pixel_x))
            slope = float(np.degrees(np.arctan(np.hypot(dz_dx[1, 1], dz_dy[1, 1]))))
            aspect = float((np.degrees(np.arctan2(-dz_dx[1, 1], dz_dy[1, 1])) + 360.0) % 360.0)
            return TerrainFeatures(
                slope_angle_deg=slope,
                aspect_deg=aspect,
                elevation_m=elevation,
                dem_path=str(path),
                source_crs=str(dataset.crs),
            )
    except TerrainSourceUnavailable:
        raise
    except Exception as error:
        raise TerrainSourceUnavailable(f"Unable to read DEM with rasterio: {type(error).__name__}") from error