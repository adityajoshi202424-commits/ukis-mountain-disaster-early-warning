import { NextRequest, NextResponse } from 'next/server';
import { HIM_KAVACH_SECTORS, CASCADING_SIMULATION_STEPS } from '@/types/him_kavach';

export const dynamic = 'force-dynamic';

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const sectorId = searchParams.get('sector_id');

  if (sectorId) {
    const found = HIM_KAVACH_SECTORS.find((s) => s.id === sectorId);
    if (!found) {
      return NextResponse.json({ error: 'Sector ID not found' }, { status: 404 });
    }
    return NextResponse.json({ sector: found, simulationSteps: CASCADING_SIMULATION_STEPS });
  }

  return NextResponse.json({
    platformName: 'HIM-KAVACH (हिम-कवच)',
    subTitle: 'Explainable Geospatial Multi-Hazard Early-Warning & Cascading-Risk Intelligence Platform',
    institution: 'Government of Uttarakhand • USDMA & ITDA Devbhoomi',
    hackathonProblemStatement: 'UKIS 2026 Problem Statement P-011: Mountain Disaster Early-Warning Intelligence',
    totalSectorsTracked: HIM_KAVACH_SECTORS.length,
    sectors: HIM_KAVACH_SECTORS,
    simulationSteps: CASCADING_SIMULATION_STEPS,
    dataSources: [
      'ISRO Bhuvan Cartosat 10m/30m DEM & Glacial Lake Inventory',
      'GSI Bhukosh Landslide Polygons & Main Central Thrust (MCT) Fault Line Buffer',
      'Copernicus Sentinel-1 SAR Radar & GloFAS River Basin Discharge Forecast',
      'Open-Meteo & IMD AWS Real-Time Precipitation & 0°C Freezing Isotherm',
      'USGS Real-Time Himalayan Seismicity (M4+ Shaking Intensity Contours)',
    ],
    timestamp: new Date().toISOString(),
  });
}
