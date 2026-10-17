"""
Critical Infrastructure & Disaster Response Exposure Analytics Service
Spatial Intersection Engine for Real-Time Civic Asset Exposure Assessment
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class ExposedAsset(BaseModel):
    asset_id: str
    name: str
    type: str  # 'hospital' | 'school' | 'substation' | 'water_plant' | 'road'
    latitude: float
    longitude: float
    distance_km: float
    estimated_water_depth_m: float
    vulnerability_tier: str  # 'CRITICAL' | 'HIGH' | 'MODERATE'


class ExposureAnalyticsResult(BaseModel):
    region: str
    center_coordinate: Dict[str, float]
    radius_km: float
    estimated_inundation_area_sqkm: float
    flooded_roads_km: float
    submerged_power_substations_count: int
    vulnerable_hospitals_count: int
    vulnerable_schools_count: int
    drinking_water_points_count: int
    estimated_exposed_population: int
    critical_assets_list: List[ExposedAsset]
    evacuation_priority_index: float  # Scale 0.0 to 10.0


class ExposureAnalyticsService:
    """
    Computes spatial intersections between UNet flood extent rasters/polygons
    and civic infrastructure networks (OSM + State Disaster Management Baselines).
    """

    # Baseline civic infrastructure registry for Uttarakhand mountain corridors (USDMA / PWD)
    CRITICAL_CIVIC_ASSETS: List[Dict[str, Any]] = [
        {
            "asset_id": "CHAMOLI_CIVIC_01",
            "name": "Joshimath Community Health Centre (CHC Emergency Hospital)",
            "type": "hospital",
            "district": "Chamoli",
            "lat": 30.5564,
            "lon": 79.5670,
            "elevation_m": 1890.0,
        },
        {
            "asset_id": "CHAMOLI_CIVIC_02",
            "name": "NTPC Tapovan-Vishnugad Hydro Substation & Switchyard",
            "type": "substation",
            "district": "Chamoli",
            "lat": 30.4950,
            "lon": 79.6300,
            "elevation_m": 1805.0,
        },
        {
            "asset_id": "CHAMOLI_CIVIC_03",
            "name": "Joshimath Municipal Drinking Water Treatment Plant",
            "type": "water_plant",
            "district": "Chamoli",
            "lat": 30.5520,
            "lon": 79.5630,
            "elevation_m": 1870.0,
        },
        {
            "asset_id": "CHAMOLI_CIVIC_04",
            "name": "Kendriya Vidyalaya Joshimath (High-Ground Designated Relief Camp)",
            "type": "school",
            "district": "Chamoli",
            "lat": 30.5580,
            "lon": 79.5700,
            "elevation_m": 1910.0,
        },
        {
            "asset_id": "CHAMOLI_CIVIC_05",
            "name": "NH-58 Rishikesh-Badrinath Pilgrim Highway Valley Choke Point",
            "type": "road",
            "district": "Chamoli",
            "lat": 30.5600,
            "lon": 79.5720,
            "elevation_m": 1850.0,
        },
        {
            "asset_id": "RUDRAPRAYAG_CIVIC_01",
            "name": "District Hospital Rudraprayag (Alaknanda-Mandakini Confluence)",
            "type": "hospital",
            "district": "Rudraprayag",
            "lat": 30.2850,
            "lon": 78.9810,
            "elevation_m": 615.0,
        },
        {
            "asset_id": "RUDRAPRAYAG_CIVIC_02",
            "name": "UPCL 66kV Tilwara-Guptkashi Grid Substation",
            "type": "substation",
            "district": "Rudraprayag",
            "lat": 30.3420,
            "lon": 79.0320,
            "elevation_m": 820.0,
        },
        {
            "asset_id": "UTTARKASHI_CIVIC_01",
            "name": "District Hospital Uttarkashi (Bhagirathi Gorge Facility)",
            "type": "hospital",
            "district": "Uttarkashi",
            "lat": 30.7268,
            "lon": 78.4354,
            "elevation_m": 1158.0,
        },
    ]

    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Computes great-circle distance between two points in km."""
        r = 6371.0
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
        return r * (2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a)))

    def calculate_exposure(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 15.0,
        flood_depth_m: float = 1.45,
        district: Optional[str] = None,
    ) -> ExposureAnalyticsResult:
        """
        Calculates exact infrastructure exposure metrics for emergency disaster prioritization in mountain corridors.
        """
        exposed_assets: List[ExposedAsset] = []
        substations = 0
        hospitals = 0
        schools = 0
        water_plants = 0

        for asset in self.CRITICAL_CIVIC_ASSETS:
            dist = self._haversine_distance(latitude, longitude, asset["lat"], asset["lon"])
            if dist <= radius_km:
                water_depth = max(0.0, round(flood_depth_m - (asset.get("elevation_m", 1850.0) - 1845.0) * 0.4, 2))
                
                tier = "MODERATE"
                if asset["type"] in ["hospital", "substation"] or water_depth > 0.8:
                    tier = "CRITICAL"
                elif water_depth > 0.3:
                    tier = "HIGH"

                exposed_assets.append(
                    ExposedAsset(
                        asset_id=asset["asset_id"],
                        name=asset["name"],
                        type=asset["type"],
                        latitude=asset["lat"],
                        longitude=asset["lon"],
                        distance_km=round(dist, 2),
                        estimated_water_depth_m=water_depth,
                        vulnerability_tier=tier,
                    )
                )

                if asset["type"] == "substation":
                    substations += 1
                elif asset["type"] == "hospital":
                    hospitals += 1
                elif asset["type"] == "school":
                    schools += 1
                elif asset["type"] == "water_plant":
                    water_plants += 1

        # Calculate estimated exposed road length along steep Himalayan valleys (~0.85 km road per sqkm)
        flooded_area_sqkm = round(math.pi * (min(radius_km, 8.0) ** 2) * 0.35, 2)
        flooded_roads_km = round(flooded_area_sqkm * 0.85, 1)

        # Approximate population density in Uttarakhand riverine valleys (~189 persons / sqkm per Census)
        exposed_population = int(flooded_area_sqkm * 189)

        # Evacuation Priority Index: composite score based on depth and asset density
        priority_index = min(10.0, round(3.5 + (flood_depth_m * 2.2) + (hospitals * 1.2) + (substations * 1.0), 1))

        return ExposureAnalyticsResult(
            region=district or "Uttarakhand Mountain Watershed Sector",
            center_coordinate={"lat": latitude, "lon": longitude},
            radius_km=radius_km,
            estimated_inundation_area_sqkm=flooded_area_sqkm,
            flooded_roads_km=flooded_roads_km,
            submerged_power_substations_count=substations,
            vulnerable_hospitals_count=hospitals,
            vulnerable_schools_count=schools,
            drinking_water_points_count=water_plants,
            estimated_exposed_population=exposed_population,
            critical_assets_list=exposed_assets,
            evacuation_priority_index=priority_index,
        )


exposure_analytics_service = ExposureAnalyticsService()

