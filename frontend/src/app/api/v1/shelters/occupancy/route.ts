import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET() {
  return NextResponse.json({
    timestamp: new Date().toISOString(),
    total_shelters: 5,
    shelters: [
      {
        shelter_id: 'SHL-CHAMOLI-01',
        name: 'Joshimath GMVN High-Ground Complex',
        district: 'Chamoli',
        capacity: 1200,
        current_occupancy: 340,
        elevation_m: 1950,
        is_live: true,
        contact_person: 'GMVN Manager Joshimath',
        contact_phone: '+91 94120 12345',
        supplies_status: 'ADEQUATE',
      },
      {
        shelter_id: 'SHL-RUDRAPRAYAG-02',
        name: 'Guptkashi GIC Inter College Safe Ground',
        district: 'Rudraprayag',
        capacity: 800,
        current_occupancy: 180,
        elevation_m: 1480,
        is_live: true,
        contact_person: 'Principal GIC Guptkashi',
        contact_phone: '+91 94120 54321',
        supplies_status: 'ADEQUATE',
      },
      {
        shelter_id: 'SHL-UTTARKASHI-03',
        name: 'Bhatwari Emergency Relief Camp',
        district: 'Uttarkashi',
        capacity: 650,
        current_occupancy: 95,
        elevation_m: 1250,
        is_live: true,
        contact_person: 'Tehsildar Bhatwari',
        contact_phone: '+91 94120 67890',
        supplies_status: 'ADEQUATE',
      },
      {
        shelter_id: 'SHL-PAURI-04',
        name: 'HNB Garhwal University Srinagar Auditorium',
        district: 'Pauri Garhwal',
        capacity: 1500,
        current_occupancy: 220,
        elevation_m: 560,
        is_live: true,
        contact_person: 'Camp Commander SDRF Srinagar',
        contact_phone: '+91 94120 98765',
        supplies_status: 'ADEQUATE',
      },
      {
        shelter_id: 'SHL-NAINITAL-05',
        name: 'Nainital Club High-Ridge Pavilion',
        district: 'Nainital',
        capacity: 500,
        current_occupancy: 60,
        elevation_m: 2080,
        is_live: true,
        contact_person: 'SDM Nainital Control Room',
        contact_phone: '+91 94120 11223',
        supplies_status: 'ADEQUATE',
      },
    ],
  });
}
