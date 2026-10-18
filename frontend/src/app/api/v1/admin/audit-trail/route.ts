import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET(req: NextRequest) {
  return NextResponse.json({
    audit_trail: [
      {
        id: 'AUDIT-LOG-101',
        action: 'ISSUED_CAP_ALERT',
        admin_user: 'dmmc_admin',
        district: 'Chamoli',
        details: 'Issued Flash Flood & GLOF Red Warning identifier IN-UK-DMMC-CHAMOLI-01 to state DEOC.',
        timestamp: new Date(Date.now() - 3600000).toISOString(),
        ip_address: '10.244.18.2 (State Secretariat VPN)',
      },
      {
        id: 'AUDIT-LOG-102',
        action: 'TRIGGER_CELL_BROADCAST',
        admin_user: 'dmmc_admin',
        district: 'Rudraprayag',
        details: 'Broadcast 3GPP TS 23.041 Channel 4370 alert to Sonprayag and Gaurikund cells.',
        timestamp: new Date(Date.now() - 7200000).toISOString(),
        ip_address: '10.244.18.2 (State Secretariat VPN)',
      },
      {
        id: 'AUDIT-LOG-103',
        action: 'CHAR_DHAM_HALT_DIRECTIVE',
        admin_user: 'dmmc_admin',
        district: 'Pauri Garhwal',
        details: 'Issued traffic diversion order at Srinagar barrier for NH-07 Sirobagad sector.',
        timestamp: new Date(Date.now() - 14400000).toISOString(),
        ip_address: '10.244.18.2 (State Secretariat VPN)',
      },
    ],
  });
}
