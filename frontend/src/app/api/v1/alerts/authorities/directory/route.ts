import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const districtFilter = searchParams.get('district');

  const authorities = [
    {
      authority_id: 'AUTH-SEOC-01',
      name: 'State Duty Officer',
      designation: 'Joint CEO, State Emergency Operations Centre (SEOC)',
      agency: 'SEOC',
      district: 'Statewide',
      phone_primary: '+91-135-2710334',
      phone_mobile: '+91-9412052100',
      radio_channel: 'VHF 156.800 MHz (Disaster Command Net)',
      escalation_priority: 1,
      is_active_duty: true,
    },
    {
      authority_id: 'AUTH-SDRF-01',
      name: 'Commandant, SDRF Uttarakhand',
      designation: 'Senior Superintendent of Police / Commandant',
      agency: 'SDRF',
      district: 'Statewide',
      phone_primary: '+91-135-2761800',
      phone_mobile: '+91-9456598888',
      radio_channel: 'SDRF Tactical Net 162.125 MHz',
      escalation_priority: 1,
      is_active_duty: true,
    },
    {
      authority_id: 'AUTH-NDRF-01',
      name: 'Commandant, 8th Bn NDRF',
      designation: 'Battalion Commander, Northern Sector',
      agency: 'NDRF',
      district: 'Statewide',
      phone_primary: '+91-120-2766013',
      phone_mobile: '+91-9412052112',
      radio_channel: 'NDRF Inter-Agency UHF 412.350 MHz',
      escalation_priority: 2,
      is_active_duty: true,
    },
    {
      authority_id: 'AUTH-DM-CHAMOLI-01',
      name: 'District Magistrate Chamoli',
      designation: 'District Collector & DDMA Chairman',
      agency: 'DDMA',
      district: 'Chamoli',
      phone_primary: '+91-1372-252101',
      phone_mobile: '+91-9412055666',
      radio_channel: 'Chamoli EOC Link 152.050 MHz',
      escalation_priority: 1,
      is_active_duty: true,
    },
    {
      authority_id: 'AUTH-SP-CHAMOLI-01',
      name: 'Superintendent of Police Chamoli',
      designation: 'District Police Chief',
      agency: 'POLICE',
      district: 'Chamoli',
      phone_primary: '+91-1372-252134',
      phone_mobile: '+91-9412052134',
      radio_channel: 'Chamoli Police Net CH-3',
      escalation_priority: 2,
      is_active_duty: true,
    },
    {
      authority_id: 'AUTH-CWC-CHAMOLI-01',
      name: 'Executive Engineer, CWC Chamoli',
      designation: 'Executive Engineer, Upper Ganga Division',
      agency: 'CWC',
      district: 'Chamoli',
      phone_primary: '+91-1372-252200',
      phone_mobile: '+91-9412052200',
      radio_channel: 'CWC Hydrology Link',
      escalation_priority: 2,
      is_active_duty: true,
    },
    {
      authority_id: 'AUTH-DM-RUDRAPRAYAG-01',
      name: 'District Magistrate Rudraprayag',
      designation: 'District Collector & DDMA Chairman',
      agency: 'DDMA',
      district: 'Rudraprayag',
      phone_primary: '+91-1364-233300',
      phone_mobile: '+91-9412055777',
      radio_channel: 'Rudraprayag EOC 153.125 MHz',
      escalation_priority: 1,
      is_active_duty: true,
    },
    {
      authority_id: 'AUTH-DM-UTTARKASHI-01',
      name: 'District Magistrate Uttarkashi',
      designation: 'District Collector & DDMA Chairman',
      agency: 'DDMA',
      district: 'Uttarkashi',
      phone_primary: '+91-1374-222102',
      phone_mobile: '+91-9412055888',
      radio_channel: 'Bhagirathi Net 151.750 MHz',
      escalation_priority: 1,
      is_active_duty: true,
    },
    {
      authority_id: 'AUTH-DM-PAURI-01',
      name: 'District Magistrate Pauri Garhwal',
      designation: 'District Collector & DDMA Chairman',
      agency: 'DDMA',
      district: 'Pauri Garhwal',
      phone_primary: '+91-1368-222101',
      phone_mobile: '+91-9412055999',
      radio_channel: 'Pauri District Net',
      escalation_priority: 1,
      is_active_duty: true,
    },
  ];

  let filtered = authorities;
  if (districtFilter) {
    const target = districtFilter.toLowerCase();
    filtered = authorities.filter(
      (a) => a.district.toLowerCase() === target || a.district.toLowerCase() === 'statewide'
    );
  }

  return NextResponse.json(filtered);
}
