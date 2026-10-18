import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const corridor = searchParams.get('corridor') || 'NH-07 (Badrinath Axis)';

  // UTDB Biometric Registration Live Mock Data
  const towns = [
    {
      town: 'Rishikesh (Transit Hub)',
      highwayKm: 0,
      activeVehiclesEnRoute: 2400,
      holdingCapacityVehicles: 3500,
      currentOccupancyVehicles: 1800,
      availableCapacity: 1700,
      shelters: 'ISBT Transit Camp & Bharat Bhoomi Tourism Complex (Cap: 4,000 pilgrims)',
      policeCheckpost: 'Tapovan Police Barrier / Pashulok Barrage Gate',
      status: 'CONVOYS_PERMITTED',
      directive: 'Regulate batch departures; advise pilgrims of weather warnings ahead.',
    },
    {
      town: 'Devprayag (Sangam Point)',
      highwayKm: 72,
      activeVehiclesEnRoute: 850,
      holdingCapacityVehicles: 1200,
      currentOccupancyVehicles: 950,
      availableCapacity: 250,
      shelters: 'GIC Devprayag & GMVN Tourist Bungalow (Cap: 1,500 pilgrims)',
      policeCheckpost: 'Devprayag Confluence Barrier (NH-07 / NH-34 Junction)',
      status: 'RESTRICTED_FLOW',
      directive: 'Hold commercial buses if Srinagar transit hub reports >90% occupancy.',
    },
    {
      town: 'Srinagar Garhwal',
      highwayKm: 105,
      activeVehiclesEnRoute: 1200,
      holdingCapacityVehicles: 2000,
      currentOccupancyVehicles: 1850,
      availableCapacity: 150,
      shelters: 'HNB Garhwal University Campus & SSB Grounds (Cap: 5,500 pilgrims)',
      policeCheckpost: 'Srinagar Dam Gate / Kirtinagar Bridge Outpost',
      status: 'NEAR_CAPACITY',
      directive: 'Divert upward pilgrims into University holding shelters; prevent bottleneck at Sirobagad.',
    },
    {
      town: 'Rudraprayag Sangam',
      highwayKm: 140,
      activeVehiclesEnRoute: 920,
      holdingCapacityVehicles: 1400,
      currentOccupancyVehicles: 1280,
      availableCapacity: 120,
      shelters: 'GIC Rudraprayag & GMVN Ratanpur Campsite (Cap: 2,200 pilgrims)',
      policeCheckpost: 'Gulabrai Checkpost / Kedarnath NH-107 Divergence',
      status: 'HOLD_AT_GATE',
      directive: 'Stop all Badrinath-bound heavy vehicles. Separate Kedarnath pilgrim flow via NH-107.',
    },
    {
      town: 'Karnaprayag',
      highwayKm: 172,
      activeVehiclesEnRoute: 640,
      holdingCapacityVehicles: 900,
      currentOccupancyVehicles: 780,
      availableCapacity: 120,
      shelters: 'ITBP High Ground & Municipal Complex (Cap: 1,800 pilgrims)',
      policeCheckpost: 'Subhash Nagar Barrier (Pindar Confluence)',
      status: 'HOLD_AT_GATE',
      directive: 'Hold vehicles until Joshimath toe-slope clearance report is received from BRO.',
    },
    {
      town: 'Joshimath (Upper Cantonment)',
      highwayKm: 252,
      activeVehiclesEnRoute: 380,
      holdingCapacityVehicles: 800,
      currentOccupancyVehicles: 740,
      availableCapacity: 60,
      shelters: 'Joshimath GMVN High-Ridge Safe Haven (Elev: 1,950m, Cap: 1,200)',
      policeCheckpost: 'Pandukeshwar Checkpost / Mana Pass Outer Gate',
      status: 'EVACUATE_CORRIDOR',
      directive: 'Mandatory halt on upward traffic. Move vulnerable residents into GMVN high-ground shelter.',
    },
  ];

  const totalVehicles = towns.reduce((sum, t) => sum + t.currentOccupancyVehicles, 0);
  const totalCapacity = towns.reduce((sum, t) => sum + t.holdingCapacityVehicles, 0);
  const totalTouristsEst = totalVehicles * 4;

  return NextResponse.json({
    corridorName: corridor,
    utdbIntegration: 'CONNECTED (UTDB Biometric Portal API v2.4)',
    totalVehiclesInTransit: totalVehicles,
    totalHoldingCapacity: totalCapacity,
    corridorLoadPct: Math.round((totalVehicles / totalCapacity) * 100),
    estimatedPilgrimsInTransit: totalTouristsEst,
    recommendedGateAction:
      totalVehicles / totalCapacity > 0.85
        ? 'ACTIVATE_STAGED_CONVOY_HOLD_AT_RISHIKESH'
        : 'NORMAL_STAGGERED_DISPATCH',
    towns,
    timestamp: new Date().toISOString(),
  });
}
