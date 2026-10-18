import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET() {
  return NextResponse.json([
    {
      call_id: 'CALL-2026-001',
      recipient_name: 'District Magistrate Chamoli',
      phone_number: '+91 94120 XXXXX',
      designation: 'Incident Commander',
      status: 'COMPLETED',
      duration_sec: 48,
      spoken_briefing: 'High-altitude GLOF alert issued for Vasudhara Tal catchment. Water velocity 8.5 m/s. Implement immediate Alaknanda riverbed evacuation.',
      timestamp: new Date(Date.now() - 1800000).toISOString(),
    },
    {
      call_id: 'CALL-2026-002',
      recipient_name: 'SDRF 3rd Battalion Commandant',
      phone_number: '+91 94121 XXXXX',
      designation: 'Rescue Force Commander',
      status: 'COMPLETED',
      duration_sec: 62,
      spoken_briefing: 'Deploy Quick Reaction Teams to Pandukeshwar and Tapovan axis. Prepare mountain rescue rafts.',
      timestamp: new Date(Date.now() - 2400000).toISOString(),
    },
    {
      call_id: 'CALL-2026-003',
      recipient_name: 'Superintendent of Police Rudraprayag',
      phone_number: '+91 94122 XXXXX',
      designation: 'Char Dham Corridor In-charge',
      status: 'COMPLETED',
      duration_sec: 39,
      spoken_briefing: 'Halt all upward pedestrian pilgrimage from Sonprayag. Divert pilgrims to designated GMVN shelters.',
      timestamp: new Date(Date.now() - 3600000).toISOString(),
    },
  ]);
}
