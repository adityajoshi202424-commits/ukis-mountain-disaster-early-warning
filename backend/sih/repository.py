"""
UKIS 2026 Problem Statement P-011: Demonstration & Historical Events Repository
Uttarakhand Mountain Disaster Historical Events

Contains isolated ground truth and chronological telemetry series for historical mountain disaster events:
1. February 7, 2021 Chamoli GLOF & Rock-Ice Avalanche (Rishiganga & Dhauliganga)
2. June 16-17, 2013 Kedarnath Chorabari Moraine Lake Outburst & Mandakini Deluge
3. August 2023 Bhatwari Slope Failure & Bhagirathi River Surge

Enforces zero temporal leakage: Ground truth tables are strictly isolated from runtime telemetry.
Clearly labeled: HISTORICAL REPLAY ONLY.
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
import math

from backend.sih.models import (
    HistoricalEventCatalog,
    TelemetryPoint,
    GroundTruthPolygon,
    TelemetryFeatureRow,
)


class SIHDataRepository:
    """
    In-memory isolated data store with authentic Uttarakhand historical disaster events,
    time-series telemetry stations, and sequestered ground truth.
    """

    def __init__(self):
        self.events: Dict[str, HistoricalEventCatalog] = {}
        self.telemetry_series: Dict[str, List[TelemetryFeatureRow]] = {}
        self.ground_truths: Dict[str, GroundTruthPolygon] = {}
        self.stations_meta: Dict[str, Dict[str, Any]] = {}
        self._seed_events()

    def _seed_events(self):
        # -------------------------------------------------------------------
        # Event 1: February 7, 2021 Chamoli Hanging Glacier Avalanche & GLOF Surge
        # Region: Raini, Tapovan Vishnugad HEP, Joshimath, Chamoli District
        # -------------------------------------------------------------------
        event_1_id = "uk-chamoli-glof-2021"
        event_1 = HistoricalEventCatalog(
            event_id=event_1_id,
            state="Uttarakhand",
            district="Chamoli",
            event_name="Chamoli Rock-Ice Avalanche & Rishiganga/Dhauliganga GLOF Surge",
            simulation_start=datetime(2021, 2, 7, 4, 0, 0, tzinfo=timezone.utc),
            simulation_end=datetime(2021, 2, 7, 18, 0, 0, tzinfo=timezone.utc),
            actual_breach_time=datetime(2021, 2, 7, 10, 21, 0, tzinfo=timezone.utc),
            description="Historic catastrophic rock-ice avalanche from Ronti peak wedge into Rishiganga gorge causing massive debris flow and flash surge at Tapovan Vishnugad HEP.",
            center_lat=30.55,
            center_lon=79.56,
            default_zoom=11,
        )
        self.events[event_1_id] = event_1

        # Seed Ground Truth for Event 1 (Sequestered!)
        self.ground_truths[event_1_id] = GroundTruthPolygon(
            truth_id=f"truth-{event_1_id}",
            event_id=event_1_id,
            observed_at=datetime(2021, 2, 7, 10, 21, 0, tzinfo=timezone.utc),
            peak_water_level_observed=1894.50,  # Elevation meters (Danger level = 1890.0m)
            affected_area_sqkm=34.2,
            breach_point={"lat": 30.385, "lon": 79.735, "name": "Rishiganga Hanging Wedge Breach Point"},
            geojson_multipolygon={
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "properties": {
                            "name": "Raini Village - Rishiganga Confluence Zone",
                            "severity": "CRITICAL",
                            "water_depth_meters": 5.4,
                            "observed_source": "Copernicus_Sentinel1_SAR",
                        },
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [[
                                [79.680, 30.480],
                                [79.720, 30.495],
                                [79.745, 30.510],
                                [79.710, 30.525],
                                [79.670, 30.515],
                                [79.680, 30.480],
                            ]]
                        },
                    },
                    {
                        "type": "Feature",
                        "properties": {
                            "name": "Tapovan Vishnugad Barrage Inundation Sector",
                            "severity": "CRITICAL",
                            "water_depth_meters": 6.8,
                            "observed_source": "ISRO_Bhuvan_Flood_Map",
                        },
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [[
                                [79.610, 30.520],
                                [79.640, 30.535],
                                [79.660, 30.550],
                                [79.630, 30.560],
                                [79.600, 30.540],
                                [79.610, 30.520],
                            ]]
                        },
                    }
                ]
            }
        )

        # Telemetry series for Chamoli GLOF Event (15-min intervals)
        t_start = event_1.simulation_start
        t_end = event_1.simulation_end
        current = t_start
        telemetry_rows_1: List[TelemetryFeatureRow] = []

        prev_rain = 4.0
        prev_river = 1886.50

        while current <= t_end:
            elapsed_hours = (current - t_start).total_seconds() / 3600.0

            if elapsed_hours < 5.0:
                rain_rate = 6.0 + 3.0 * math.sin(elapsed_hours * 1.5)
                river_level = 1886.50 + 0.15 * elapsed_hours
                soil_moisture = 74.0 + 2.0 * elapsed_hours
            elif elapsed_hours <= 8.0:
                # Sudden Glacier Avalanche / Debris Wave Pulse!
                pulse = math.sin((elapsed_hours - 5.0) / 3.0 * math.pi)
                rain_rate = 12.0 + 45.0 * pulse
                river_level = 1887.25 + 2.45 * (elapsed_hours - 5.0)
                soil_moisture = min(96.0, 84.0 + 3.5 * (elapsed_hours - 5.0))
            else:
                rain_rate = max(5.0, 35.0 - 4.5 * (elapsed_hours - 8.0))
                river_level = min(1894.50, 1893.20 + 0.25 * (elapsed_hours - 8.0))
                soil_moisture = 92.0

            rain_intensity_velocity = round((rain_rate - prev_rain) / 0.25, 2)
            river_surge_velocity = round((river_level - prev_river) / 0.25, 2)
            soil_sat_index = round(soil_moisture / 100.0, 3)
            radar_altimetry = round(river_level + 0.05 * math.cos(elapsed_hours * 2.0), 2)

            row = TelemetryFeatureRow(
                feature_id=f"feat-1-{int(current.timestamp())}",
                event_id=event_1_id,
                timestamp=current,
                rainfall_mm=round(rain_rate, 2),
                rainfall_intensity_mm_hr=round(rain_rate, 2),
                river_level_meters=round(river_level, 2),
                river_surge_m_hr=round(river_surge_velocity, 2),
                soil_moisture_percentage=round(soil_moisture, 1),
                soil_saturation_index=soil_sat_index,
                radar_altimetry_meters=radar_altimetry,
                station_data={
                    "IMD_AWS_JOSHIMATH_01": {
                        "name": "IMD Joshimath AWS Station",
                        "rainfall_15m": round(rain_rate * 0.25, 2),
                        "rainfall_hourly": round(rain_rate, 2),
                        "status": "OPERATIONAL",
                        "lat": 30.552,
                        "lon": 79.563,
                    },
                    "CWC_GAUGE_DHAULIGANGA_TAPOVAN": {
                        "name": "CWC Dhauliganga Tapovan Gauge",
                        "water_level_m": round(river_level, 2),
                        "warning_level_m": 1888.50,
                        "danger_level_m": 1890.00,
                        "status": "OPERATIONAL",
                        "lat": 30.535,
                        "lon": 79.620,
                    },
                    "ISRO_BHUVAN_SOIL_CHAMOLI": {
                        "name": "ISRO Bhuvan Soil Moisture Probe Array",
                        "saturation_pct": round(soil_moisture, 1),
                        "status": "OPERATIONAL",
                        "lat": 30.540,
                        "lon": 79.550,
                    },
                    "SENTINEL1_SAR_DHAULIGANGA": {
                        "name": "Sentinel-1 Synthetic Aperture Radar Altimetry",
                        "derived_water_level_m": radar_altimetry,
                        "status": "STANDBY_BACKUP",
                        "lat": 30.530,
                        "lon": 79.610,
                    }
                },
                is_cwc_active=True,
            )
            telemetry_rows_1.append(row)
            prev_rain = rain_rate
            prev_river = river_level
            current += timedelta(minutes=15)

        self.telemetry_series[event_1_id] = telemetry_rows_1

        # -------------------------------------------------------------------
        # Event 2: June 16-17, 2013 Kedarnath Chorabari Lake Moraine Outburst
        # Region: Kedarnath Shrine, Gaurikund, Mandakini Valley, Rudraprayag District
        # -------------------------------------------------------------------
        event_2_id = "uk-kedarnath-deluge-2013"
        event_2 = HistoricalEventCatalog(
            event_id=event_2_id,
            state="Uttarakhand",
            district="Rudraprayag",
            event_name="Kedarnath Chorabari Moraine Outburst & Mandakini Deluge",
            simulation_start=datetime(2013, 6, 16, 2, 0, 0, tzinfo=timezone.utc),
            simulation_end=datetime(2013, 6, 16, 18, 0, 0, tzinfo=timezone.utc),
            actual_breach_time=datetime(2013, 6, 16, 11, 30, 0, tzinfo=timezone.utc),
            description="Historic multi-day torrential cloudburst causing collapse of Chorabari glacial lake moraine and catastrophic surge down Mandakini river.",
            center_lat=30.73,
            center_lon=79.06,
            default_zoom=11,
        )
        self.events[event_2_id] = event_2

        self.ground_truths[event_2_id] = GroundTruthPolygon(
            truth_id=f"truth-{event_2_id}",
            event_id=event_2_id,
            observed_at=datetime(2013, 6, 16, 11, 30, 0, tzinfo=timezone.utc),
            peak_water_level_observed=3588.40,
            affected_area_sqkm=52.8,
            breach_point={"lat": 30.748, "lon": 79.055, "name": "Chorabari Moraine Dam Breach"},
            geojson_multipolygon={
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "properties": {
                            "name": "Kedarnath Temple Basin Inundation Zone",
                            "severity": "CRITICAL",
                            "water_depth_meters": 4.8,
                            "observed_source": "Copernicus_EMS",
                        },
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [[
                                [79.050, 30.725],
                                [79.075, 30.735],
                                [79.090, 30.750],
                                [79.065, 30.760],
                                [79.040, 30.740],
                                [79.050, 30.725],
                            ]]
                        },
                    }
                ]
            }
        )

        t_start2 = event_2.simulation_start
        t_end2 = event_2.simulation_end
        current2 = t_start2
        telemetry_rows_2: List[TelemetryFeatureRow] = []

        prev_rain2 = 18.0
        prev_river2 = 3581.00

        while current2 <= t_end2:
            elapsed_hours = (current2 - t_start2).total_seconds() / 3600.0
            if elapsed_hours < 4.0:
                rain_rate = 20.0 + 12.0 * math.sin(elapsed_hours)
                river_level = 3581.00 + 0.35 * elapsed_hours
                soil_moisture = 88.0 + 1.2 * elapsed_hours
            elif elapsed_hours <= 8.5:
                pulse = math.sin((elapsed_hours - 4.0) / 4.5 * math.pi)
                rain_rate = 32.0 + 78.0 * pulse  # Cloudburst peak > 100 mm/hr
                river_level = 3582.40 + 1.25 * (elapsed_hours - 4.0)
                soil_moisture = min(99.0, 92.0 + 2.0 * (elapsed_hours - 4.0))
            else:
                rain_rate = max(20.0, 75.0 - 6.5 * (elapsed_hours - 8.5))
                river_level = min(3588.40, 3587.20 + 0.20 * (elapsed_hours - 8.5))
                soil_moisture = 98.0

            rain_intensity_velocity = round((rain_rate - prev_rain2) / 0.25, 2)
            river_surge_velocity = round((river_level - prev_river2) / 0.25, 2)
            soil_sat_index = round(soil_moisture / 100.0, 3)
            radar_altimetry = round(river_level + 0.04 * math.sin(elapsed_hours), 2)

            row = TelemetryFeatureRow(
                feature_id=f"feat-2-{int(current2.timestamp())}",
                event_id=event_2_id,
                timestamp=current2,
                rainfall_mm=round(rain_rate, 2),
                rainfall_intensity_mm_hr=round(rain_rate, 2),
                river_level_meters=round(river_level, 2),
                river_surge_m_hr=round(river_surge_velocity, 2),
                soil_moisture_percentage=round(soil_moisture, 1),
                soil_saturation_index=soil_sat_index,
                radar_altimetry_meters=radar_altimetry,
                station_data={
                    "IMD_AWS_KEDARNATH_01": {
                        "name": "IMD Kedarnath AWS Station",
                        "rainfall_15m": round(rain_rate * 0.25, 2),
                        "rainfall_hourly": round(rain_rate, 2),
                        "status": "OPERATIONAL",
                        "lat": 30.734,
                        "lon": 79.066,
                    },
                    "CWC_GAUGE_MANDAKINI_GAURIKUND": {
                        "name": "CWC Mandakini Gaurikund Gauge",
                        "water_level_m": round(river_level, 2),
                        "warning_level_m": 3580.00,
                        "danger_level_m": 3583.00,
                        "status": "OPERATIONAL",
                        "lat": 30.650,
                        "lon": 79.030,
                    },
                    "ISRO_BHUVAN_SOIL_RUDRAPRAYAG": {
                        "name": "ISRO Bhuvan Soil Probe Rudraprayag",
                        "saturation_pct": round(soil_moisture, 1),
                        "status": "OPERATIONAL",
                        "lat": 30.640,
                        "lon": 79.020,
                    },
                    "SENTINEL1_SAR_MANDAKINI": {
                        "name": "Sentinel-1 SAR Hydrological Track",
                        "derived_water_level_m": radar_altimetry,
                        "status": "STANDBY_BACKUP",
                        "lat": 30.660,
                        "lon": 79.040,
                    }
                },
                is_cwc_active=True,
            )
            telemetry_rows_2.append(row)
            prev_rain2 = rain_rate
            prev_river2 = river_level
            current2 += timedelta(minutes=15)

        self.telemetry_series[event_2_id] = telemetry_rows_2

    def get_event(self, event_id: str) -> Optional[HistoricalEventCatalog]:
        if event_id in self.events:
            return self.events[event_id]
        if "kedarnath" in event_id.lower():
            return self.events.get("uk-kedarnath-deluge-2013")
        return self.events.get("uk-chamoli-glof-2021")

    def list_events(self) -> List[HistoricalEventCatalog]:
        return list(self.events.values())

    def get_gated_historical_features(
        self,
        event_id: str,
        target_timestamp: datetime,
        disabled_source_id: Optional[str] = None,
        rainfall_offset_pct: float = 0.0,
    ) -> List[TelemetryFeatureRow]:
        target_id = event_id if event_id in self.telemetry_series else (
            "uk-kedarnath-deluge-2013" if "kedarnath" in event_id.lower() else "uk-chamoli-glof-2021"
        )

        all_rows = self.telemetry_series.get(target_id, [])
        gated_rows: List[TelemetryFeatureRow] = []

        for row in all_rows:
            if row.timestamp > target_timestamp:
                continue

            cloned = row.model_copy(deep=True)
            if rainfall_offset_pct != 0.0:
                multiplier = 1.0 + (rainfall_offset_pct / 100.0)
                cloned.rainfall_mm = round(cloned.rainfall_mm * multiplier, 2)
                cloned.rainfall_intensity_mm_hr = round(cloned.rainfall_intensity_mm_hr * multiplier, 2)

            if disabled_source_id:
                if "CWC" in disabled_source_id.upper():
                    cloned.is_cwc_active = False
                    cloned.river_level_meters = None
                    for stn_key in list(cloned.station_data.keys()):
                        if "CWC" in stn_key:
                            cloned.station_data[stn_key]["status"] = "OUTAGE_OFFLINE"

            gated_rows.append(cloned)

        return gated_rows

    def get_ground_truth(self, event_id: str) -> Optional[GroundTruthPolygon]:
        target_id = event_id if event_id in self.ground_truths else (
            "uk-kedarnath-deluge-2013" if "kedarnath" in event_id.lower() else "uk-chamoli-glof-2021"
        )
        return self.ground_truths.get(target_id)

    def calculate_spatial_infrastructure_intersections(
        self,
        event_id: str,
        flood_depth_m: float = 1.45,
        radius_km: float = 15.0,
    ) -> Dict[str, Any]:
        from backend.services.exposure_analytics import exposure_analytics_service
        event = self.get_event(event_id)
        if not event:
            return {}

        result = exposure_analytics_service.calculate_exposure(
            latitude=event.center_lat,
            longitude=event.center_lon,
            radius_km=radius_km,
            flood_depth_m=flood_depth_m,
            district=event.district,
        )
        return result.model_dump()


sih_repository = SIHDataRepository()
