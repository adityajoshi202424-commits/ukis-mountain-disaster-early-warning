# Dijkstra Profile-Aware Mountain Evacuation Routing & Shelter Logistics
## UKIS Problem Statement P-011: Uttarakhand Mountain Safe Corridor Routing

---

## 1. Dijkstra Pathfinding Algorithm

The evacuation engine (`calculate_safest_evacuation_path`) implements a profile-aware Dijkstra graph search over the real OSM road network in steep Himalayan valley corridors:

* **Profiles**:
  * `CITIZEN_EVAC`: Prioritizes shortest paved paths to ridge lines; strictly avoids roads with flood depth $\ge 0.20\text{ m}$ or slope instability zones.
  * `RESCUE_NDRF`: Permits 4x4 heavy all-terrain vehicles to traverse water depths up to $0.80\text{ m}$ and negotiate moderate debris gradients.
  * `LOGISTICS_SUPPLY`: Enforces heavy vehicle clearance limits ($\ge 5.0\text{ m}$ width, avoiding bridge load caps $< 40\text{ tons}$).

---

## 2. High-Ground Relief Shelter Verification

All candidate relief shelters are filtered by ground elevation, distance from active debris paths, and dynamic bed capacity:

* **Safe Mountain Elevation Criteria**: Station Elevation $\ge 1950\text{ m}$ above MSL (well above valley flood wave crest).
* **Primary Designated Shelter**: *Joshimath Cantonment High-Ground Shelter* (Elevation $2050\text{ m}$, Lat $30.5650^\circ\text{N}$, Lon $79.5780^\circ\text{E}$).
* **Secondary Overflow Shelter**: *Govt Inter College Joshimath Elevated Campus* (Elevation $1980\text{ m}$, Lat $30.5630^\circ\text{N}$, Lon $79.5740^\circ\text{E}$).
* **Dynamic Capacity Rerouting**: When a shelter reaches $100\%$ capacity, its inbound edge weight is set to $\infty$, causing Dijkstra to dynamically reroute civilian evacuees to the next nearest unsaturated facility.
