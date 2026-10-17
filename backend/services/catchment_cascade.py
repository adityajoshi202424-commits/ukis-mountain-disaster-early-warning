"""
Hydraulic Catchment Cascade Modeler & Upstream Wavefront Attenuation Engine

Calculates downstream cumulative impact metric (I_down) factoring in:
- Upstream river rate-of-rise (ΔH_upstream / Δt)
- Distance weight coefficient (W_weight)
- Exponential time-lag attenuation decay constant: e^(-λ * Δt)

Formula:
I_down = Sum( (ΔH_upstream / Δt) * W_weight * e^(-λ * Δt) )
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class CatchmentNode(BaseModel):
    station_id: str
    station_name: str
    river_name: str
    distance_upstream_km: float
    time_lag_hours: float
    weight_coefficient: float
    current_water_level_m: float
    previous_water_level_m: float
    rate_of_rise_m_hr: float


class CascadeImpactResult(BaseModel):
    target_district: str
    target_basin: str
    cumulative_downstream_impact_index: float  # I_down
    upstream_wavefront_velocity_m_hr: float
    projected_downstream_surge_arrival_minutes: int
    is_downstream_surge_imminent: bool
    upstream_catchment_nodes: List[CatchmentNode]
    decay_constant_lambda: float
    calculated_at: datetime
    engineering_summary: str


class CatchmentCascadeModeler:
    """
    Simulates upstream-to-downstream hydraulic wave cascades across steep Uttarakhand Himalayan catchments.
    """

    def __init__(self, decay_lambda: float = 0.08):
        # λ = 0.08 / hour exponential attenuation decay constant for steep mountain valleys
        self.decay_lambda = decay_lambda

        # Upstream network topology for high-risk Himalayan river corridors (Alaknanda, Mandakini, Bhagirathi)
        self.catchment_topology: Dict[str, List[Dict[str, Any]]] = {
            "Chamoli": [
                {
                    "station_id": "CWC_UPSTREAM_RISHIGANGA",
                    "station_name": "Rishiganga-Dhauliganga Glacial Confluence",
                    "river_name": "Rishiganga / Dhauliganga",
                    "distance_upstream_km": 18.0,
                    "time_lag_hours": 0.65,
                    "weight_coefficient": 0.50,
                    "base_level": 1805.00,
                },
                {
                    "station_id": "CWC_UPSTREAM_PIPALKOTI",
                    "station_name": "Pipalkoti Alaknanda Gauge Station",
                    "river_name": "Alaknanda River",
                    "distance_upstream_km": 34.0,
                    "time_lag_hours": 1.10,
                    "weight_coefficient": 0.35,
                    "base_level": 1260.00,
                },
                {
                    "station_id": "CWC_UPSTREAM_BADRINATH",
                    "station_name": "Mana-Badrinath Headwater Sensor",
                    "river_name": "Alaknanda Upper Headwaters",
                    "distance_upstream_km": 48.0,
                    "time_lag_hours": 1.60,
                    "weight_coefficient": 0.15,
                    "base_level": 3120.00,
                },
            ],
            "Rudraprayag": [
                {
                    "station_id": "CWC_UPSTREAM_GAURIKUND",
                    "station_name": "Gaurikund-Kedarnath Mandakini Gorge",
                    "river_name": "Mandakini River",
                    "distance_upstream_km": 42.0,
                    "time_lag_hours": 1.20,
                    "weight_coefficient": 0.60,
                    "base_level": 1980.00,
                },
                {
                    "station_id": "CWC_UPSTREAM_KUND",
                    "station_name": "Kund Confluence Gauge",
                    "river_name": "Madhmaheshwar Ganga Inflow",
                    "distance_upstream_km": 22.0,
                    "time_lag_hours": 0.70,
                    "weight_coefficient": 0.40,
                    "base_level": 950.00,
                },
            ],
            "Uttarkashi": [
                {
                    "station_id": "CWC_UPSTREAM_HARSHIL",
                    "station_name": "Harshil-Gangotri Valley Gauge",
                    "river_name": "Bhagirathi Upper River",
                    "distance_upstream_km": 72.0,
                    "time_lag_hours": 1.80,
                    "weight_coefficient": 0.65,
                    "base_level": 2500.00,
                },
                {
                    "station_id": "CWC_UPSTREAM_BHATWARI",
                    "station_name": "Bhatwari Landslide Choke Point",
                    "river_name": "Bhagirathi River",
                    "distance_upstream_km": 31.0,
                    "time_lag_hours": 0.80,
                    "weight_coefficient": 0.35,
                    "base_level": 1220.00,
                },
            ],
        }

    def compute_downstream_impact(
        self,
        district: str = "Chamoli",
        local_rate_of_rise: float = 1.45,
        elapsed_storm_hours: float = 1.5,
        upstream_lake_expansion_multiplier: float = 1.0,
        sar_coherence_creep_detected: bool = False,
    ) -> CascadeImpactResult:
        """
        Calculates I_down factoring in upstream surge rates and exponential distance decay:
        I_down = Sum( (ΔH_upstream / Δt) * W_weight * e^(-λ * Δt) )

        UKIS Addendum v2 Integration:
        - upstream_lake_expansion_multiplier: Derived from Sentinel-2 30-day lake expansion rate
        - sar_coherence_creep_detected: Derived from Sentinel-1 InSAR coherence loss on pilot slopes
        """
        topology = self.catchment_topology.get(district, self.catchment_topology["Chamoli"])
        upstream_nodes: List[CatchmentNode] = []
        cumulative_impact = 0.0
        max_upstream_velocity = 0.0

        for item in topology:
            # Derive realistic upstream surges corresponding to storm state and upstream precursor multiplier
            surge_multiplier = 1.15 if "Garo" in item["station_name"] or "Main" in item["station_name"] else 0.85
            effective_surge_mult = surge_multiplier * max(1.0, upstream_lake_expansion_multiplier)
            upstream_rate = round(local_rate_of_rise * effective_surge_mult, 2)
            time_lag = item["time_lag_hours"]
            weight = item["weight_coefficient"]

            # Attenuation factor: e^(-λ * Δt)
            attenuation = math.exp(-self.decay_lambda * time_lag)

            # Node contribution to downstream impact
            node_contribution = upstream_rate * weight * attenuation
            cumulative_impact += node_contribution

            if upstream_rate > max_upstream_velocity:
                max_upstream_velocity = upstream_rate

            current_level = round(item["base_level"] + (upstream_rate * elapsed_storm_hours), 2)
            previous_level = round(item["base_level"] + (upstream_rate * max(0.0, elapsed_storm_hours - 0.5)), 2)

            upstream_nodes.append(
                CatchmentNode(
                    station_id=item["station_id"],
                    station_name=item["station_name"],
                    river_name=item["river_name"],
                    distance_upstream_km=item["distance_upstream_km"],
                    time_lag_hours=time_lag,
                    weight_coefficient=weight,
                    current_water_level_m=current_level,
                    previous_water_level_m=previous_level,
                    rate_of_rise_m_hr=upstream_rate,
                )
            )

        if sar_coherence_creep_detected:
            # Slow slope destabilization precursor elevates cumulative risk index
            cumulative_impact += 0.25

        cumulative_impact = round(cumulative_impact, 3)
        surge_imminent = cumulative_impact > 0.8 or max_upstream_velocity > 1.2 or (upstream_lake_expansion_multiplier >= 1.2 and sar_coherence_creep_detected)
        arrival_minutes = 60 if sar_coherence_creep_detected else (75 if surge_imminent else 180)

        precursor_notes = []
        if upstream_lake_expansion_multiplier > 1.0:
            precursor_notes.append(f"Glacial Lake Expansion ({upstream_lake_expansion_multiplier:.2f}x upstream surge)")
        if sar_coherence_creep_detected:
            precursor_notes.append("InSAR Coherence Loss (Active Slope Creep Precursor)")

        precursor_str = f" [Precursor Inputs: {', '.join(precursor_notes)}]" if precursor_notes else ""

        summary = (
            f"Upstream catchment cascade analysis active. Cumulative downstream impact index: {cumulative_impact:.2f}. "
            f"Wavefront propagation detected from {upstream_nodes[0].station_name} with arrival estimated in {arrival_minutes} mins.{precursor_str}"
        )

        return CascadeImpactResult(
            target_district=district,
            target_basin=f"{district} Catchment Drainage Basin",
            cumulative_downstream_impact_index=cumulative_impact,
            upstream_wavefront_velocity_m_hr=max_upstream_velocity,
            projected_downstream_surge_arrival_minutes=arrival_minutes,
            is_downstream_surge_imminent=surge_imminent,
            upstream_catchment_nodes=upstream_nodes,
            decay_constant_lambda=self.decay_lambda,
            calculated_at=datetime.now(timezone.utc),
            engineering_summary=summary,
        )


catchment_cascade_modeler = CatchmentCascadeModeler()
