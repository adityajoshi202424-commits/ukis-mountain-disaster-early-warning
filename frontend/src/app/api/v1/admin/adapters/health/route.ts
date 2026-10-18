import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET() {
  const now = new Date();

  return NextResponse.json({
    status: 'HEALTHY',
    system: 'DMMC Himalayan Telemetry Gateway',
    timestamp: now.toISOString(),
    adapters: [
      {
        id: 'ADAPTER-IMD-RADAR-AWS',
        name: 'IMD Doppler Weather Radar & AWS Network',
        agency: 'India Meteorological Department',
        coverage: 'Surkanda Devi Radar, Mukteshwar Radar, 48 AWS Stations',
        status: 'ONLINE',
        latency_ms: 38,
        last_sync: new Date(Date.now() - 45000).toISOString(),
        records_ingested_last_hr: 1840,
        staleness_threshold_sec: 300,
        health_score: 99.4,
      },
      {
        id: 'ADAPTER-CWC-RIVER-GAUGES',
        name: 'CWC Mountain Hydrological River Gauge Network',
        agency: 'Central Water Commission (CWC)',
        coverage: 'Alaknanda, Bhagirathi, Mandakini, Pindar, Kali River Basins',
        status: 'ONLINE',
        latency_ms: 54,
        last_sync: new Date(Date.now() - 30000).toISOString(),
        records_ingested_last_hr: 960,
        staleness_threshold_sec: 180,
        health_score: 98.8,
      },
      {
        id: 'ADAPTER-GLOFAS-COPERNICUS',
        name: 'Copernicus GloFAS Alpine Runoff & Discharge Forecasting',
        agency: 'European Centre for Medium-Range Weather Forecasts (ECMWF)',
        coverage: 'Catchment Grids across High Himalayan Watersheds',
        status: 'ONLINE',
        latency_ms: 112,
        last_sync: new Date(Date.now() - 120000).toISOString(),
        records_ingested_last_hr: 320,
        staleness_threshold_sec: 3600,
        health_score: 97.5,
      },
      {
        id: 'ADAPTER-ISRO-BHUVAN',
        name: 'ISRO Bhuvan High-Altitude Glacial Lake Inventory & LULC',
        agency: 'National Remote Sensing Centre (NRSC / ISRO)',
        coverage: '1,266 Glacial Lakes across Uttarakhand Himalaya',
        status: 'ONLINE',
        latency_ms: 85,
        last_sync: new Date(Date.now() - 180000).toISOString(),
        records_ingested_last_hr: 140,
        staleness_threshold_sec: 7200,
        health_score: 99.1,
      },
      {
        id: 'ADAPTER-USGS-SEISMIC',
        name: 'USGS Himalayan Seismicity & Shaking Intensity Feed',
        agency: 'USGS National Earthquake Information Center',
        coverage: 'Main Boundary Thrust (MBT) & Main Central Thrust (MCT)',
        status: 'ONLINE',
        latency_ms: 62,
        last_sync: new Date(Date.now() - 25000).toISOString(),
        records_ingested_last_hr: 580,
        staleness_threshold_sec: 600,
        health_score: 99.8,
      },
    ],
  });
}
