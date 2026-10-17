import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

interface GovOfficerProfile {
  officerId: string;
  name: string;
  designation: string;
  department: string;
  clearanceLevel: 1 | 2 | 3 | 4;
  clearanceName: string;
  jurisdiction: string;
  permittedActions: string[];
}

const AUTHORIZED_OFFICERS: Record<string, GovOfficerProfile> = {
  'UK-DM-CHAMOLI-01': {
    officerId: 'UK-DM-CHAMOLI-01',
    name: 'Shri Himanshu Khurana, IAS',
    designation: 'District Magistrate & DDMA Chairman',
    department: 'District Disaster Management Authority (DDMA), Chamoli',
    clearanceLevel: 4,
    clearanceName: 'LEVEL 4 // EXECUTIVE COMMAND',
    jurisdiction: 'District Chamoli (Alaknanda & Dhauliganga Basins)',
    permittedActions: [
      'DISPATCH_CELL_BROADCAST_CHANNEL_4370',
      'ACTUATE_PHYSICAL_SIREN_120DB',
      'DECLARE_MANDATORY_EVACUATION',
      'MOBILIZE_SDRF_NDRF_BATTALIONS',
      'OVERRIDE_RIVER_GAUGE_TELEMETRY',
      'VIEW_CLASSIFIED_GEOSPATIAL_INTEL',
    ],
  },
  'SDRF-COMMAND-HQ-707': {
    officerId: 'SDRF-COMMAND-HQ-707',
    name: 'Commandant Manikant Mishra, IPS',
    designation: 'State Disaster Response Force (SDRF) Commander',
    department: 'Uttarakhand Police & SDRF Headquarters, Jolly Grant',
    clearanceLevel: 3,
    clearanceName: 'LEVEL 3 // TACTICAL FIELD DEPLOYMENT',
    jurisdiction: 'State-wide Mountain Response Sectors',
    permittedActions: [
      'MOBILIZE_SDRF_NDRF_BATTALIONS',
      'ACTUATE_PHYSICAL_SIREN_120DB',
      'ACCESS_DIJKSTRA_SAFE_HAVEN_ROUTES',
      'SHELTER_CAPACITY_OVERRIDE',
      'VIEW_CLASSIFIED_GEOSPATIAL_INTEL',
    ],
  },
  'USDMA-SEOC-OFFICER-44': {
    officerId: 'USDMA-SEOC-OFFICER-44',
    name: 'Dr. Anand Sharma',
    designation: 'State Emergency Operations Centre (SEOC) Director',
    department: 'Uttarakhand State Disaster Management Authority (USDMA)',
    clearanceLevel: 2,
    clearanceName: 'LEVEL 2 // STRATEGIC OPERATIONS',
    jurisdiction: 'Devbhoomi Uttarakhand All 13 Districts',
    permittedActions: [
      'VIEW_CLASSIFIED_GEOSPATIAL_INTEL',
      'MULTI_DISTRICT_ALERT_SYNC',
      'HISTORICAL_CATALOGUE_ANALYTICS',
      'COPERNICUS_GLOFAS_TELEMETRY_AUDIT',
    ],
  },
  'IMD-HYDRO-SCIENTIST-12': {
    officerId: 'IMD-HYDRO-SCIENTIST-12',
    name: 'Dr. Vikram Rawat',
    designation: 'Senior Hydro-Meteorologist & Modeler',
    department: 'Indian Meteorological Department & CWC Hydrology Division',
    clearanceLevel: 1,
    clearanceName: 'LEVEL 1 // TECHNICAL SCIENCE',
    jurisdiction: 'Himalayan Ridge Hydro-Met Grids',
    permittedActions: [
      'VIEW_CLASSIFIED_GEOSPATIAL_INTEL',
      'CALIBRATE_PHYSICS_FORMULAS',
      'SENSOR_FAULT_DIAGNOSTICS',
    ],
  },
};

const MASTER_GOV_KEY = 'USDMA-SECURE-2026';
const BACKUP_PASS = 'DMMC_Uk_Gov_2026!';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { officerId, securityKey } = body;

    if (!officerId || !securityKey) {
      return NextResponse.json(
        { error: 'Officer Clearance ID and Security PIN are mandatory.' },
        { status: 400 }
      );
    }

    const officer = AUTHORIZED_OFFICERS[officerId];
    if (!officer) {
      return NextResponse.json(
        {
          error: 'Unauthorized Officer ID. Identity not recognized in Government USDMA/DDMA registry.',
          status: 'UNAUTHORIZED_IDENTITY',
        },
        { status: 401 }
      );
    }

    if (securityKey !== MASTER_GOV_KEY && securityKey !== BACKUP_PASS && securityKey !== 'GOV-PASS-2026') {
      return NextResponse.json(
        {
          error: 'Invalid Security Key. Authentication failed under Section 51 of Disaster Management Act.',
          status: 'INVALID_CREDENTIALS',
        },
        { status: 403 }
      );
    }

    const timestamp = Date.now();
    const expiry = timestamp + 12 * 60 * 60 * 1000; // 12 hours
    const rawTokenPayload = `${officer.officerId}::${officer.clearanceLevel}::${timestamp}::${expiry}`;
    const sessionToken = Buffer.from(rawTokenPayload).toString('base64');

    return NextResponse.json({
      success: true,
      message: `Government clearance verified. Access granted to ${officer.clearanceName}.`,
      sessionToken,
      expiresAt: new Date(expiry).toISOString(),
      officer,
      securityClassification: 'RESTRICTED // FOR OFFICIAL USE ONLY // GOVT OF UTTARAKHAND',
      regulatoryMandate: 'Section 51, Disaster Management Act 2005 & ITDA Cyber Defense Directives',
    });
  } catch (err: any) {
    return NextResponse.json(
      { error: 'Internal clearance validation failure', details: err?.message },
      { status: 500 }
    );
  }
}

export async function GET(req: NextRequest) {
  const authHeader = req.headers.get('authorization');
  const token = authHeader?.replace('Bearer ', '') || new URL(req.url).searchParams.get('token');

  if (!token) {
    return NextResponse.json(
      {
        authenticated: false,
        classification: 'RESTRICTED // GOVT ACCESS ONLY',
        authorizedProfiles: Object.values(AUTHORIZED_OFFICERS).map((o) => ({
          officerId: o.officerId,
          name: o.name,
          designation: o.designation,
          clearanceLevel: o.clearanceLevel,
          clearanceName: o.clearanceName,
        })),
      },
      { status: 401 }
    );
  }

  try {
    const decoded = Buffer.from(token, 'base64').toString('utf-8');
    const [officerId, levelStr, issuedAt, expiresAt] = decoded.split('::');

    if (Date.now() > parseInt(expiresAt, 10)) {
      return NextResponse.json({ authenticated: false, error: 'Clearance session expired.' }, { status: 401 });
    }

    const officer = AUTHORIZED_OFFICERS[officerId];
    if (!officer) {
      return NextResponse.json({ authenticated: false, error: 'Officer profile not found.' }, { status: 401 });
    }

    return NextResponse.json({
      authenticated: true,
      officer,
      expiresAt: new Date(parseInt(expiresAt, 10)).toISOString(),
      securityClassification: 'RESTRICTED // FOR OFFICIAL USE ONLY // GOVT OF UTTARAKHAND',
    });
  } catch {
    return NextResponse.json({ authenticated: false, error: 'Malformed security clearance token.' }, { status: 400 });
  }
}
