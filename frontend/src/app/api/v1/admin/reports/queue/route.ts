import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET() {
  return NextResponse.json({
    reports: [
      {
        report_id: 'REP-UK-2026-081',
        district: 'Chamoli',
        hazard_type: 'LANDSLIDE_DEBRIS',
        description: 'Boulders falling near Sirobagad bypass on NH-07. Road partially blocked on right lane.',
        reporter_name: 'Gram Pradhan Kaleshwar',
        reporter_phone: '+91 98765 43210',
        latitude: 30.252,
        longitude: 78.892,
        timestamp: new Date(Date.now() - 1800000).toISOString(),
        status: 'PENDING_MODERATION',
        verification_score: 0.92,
      },
      {
        report_id: 'REP-UK-2026-082',
        district: 'Rudraprayag',
        hazard_type: 'RIVER_LEVEL_SURGE',
        description: 'Mandakini water level touching lower bathing ghat steps at Sonprayag. Siren audible.',
        reporter_name: 'Apda Mitra Volunteer',
        reporter_phone: '+91 98765 88214',
        latitude: 30.635,
        longitude: 78.995,
        timestamp: new Date(Date.now() - 900000).toISOString(),
        status: 'PENDING_MODERATION',
        verification_score: 0.95,
      },
    ],
  });
}
