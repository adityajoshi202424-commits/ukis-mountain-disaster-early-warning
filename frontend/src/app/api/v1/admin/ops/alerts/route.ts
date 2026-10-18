import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET() {
  return NextResponse.json({
    internal_ops_alerts: [
      {
        id: 'OPS-WARN-01',
        title: 'MCT Fault Micro-Tremor Anomaly',
        severity: 'MEDIUM',
        sector: 'Chamoli - Rudraprayag Boundary',
        details: 'Minor seismic cluster (M2.1-M2.8) detected along MCT zone. Pore pressure tiltmeters in Joshimath flagged for continuous monitoring.',
        created_at: new Date(Date.now() - 3600000).toISOString(),
      },
      {
        id: 'OPS-WARN-02',
        title: 'High-Altitude Isotherm Freezing Level Rise',
        severity: 'HIGH',
        sector: 'Vasundhara Tal & Chorabari Basins',
        details: '0°C isotherm elevated to 4,600m with 45mm/hr localized precipitation; accelerated moraine seepage telemetry active.',
        created_at: new Date(Date.now() - 7200000).toISOString(),
      },
    ],
  });
}
