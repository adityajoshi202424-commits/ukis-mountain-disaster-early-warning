import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { hazardPreset, watershedSector, reporterType, gpsCoordinates } = body;

    // Simulated Vision-Language Model / YOLOv8 Classifier analysis
    let detectedFeatures: string[] = [];
    let primaryHazard = 'UNKNOWN_ANOMALY';
    let confidence = 0.88;
    let baselineRisk = 68;
    let riskBoost = 15;

    switch (hazardPreset) {
      case 'TENSION_CRACK':
        primaryHazard = 'Retaining Wall & Hillside Shear Tension Crack';
        detectedFeatures = [
          'Linear structural fracture width: 14.2 mm (Active Slip Plane)',
          'Subsurface tensile displacement on uphill flank (Krol phyllite)',
          'Roadbed foundation separation along NH-07 shoulder',
        ];
        confidence = 0.942;
        baselineRisk = 72;
        break;
      case 'MURKY_SEEPAGE':
        primaryHazard = 'Turbid Silt Seepage (Matmaila Pani - Pre-Slide Liquefaction)';
        detectedFeatures = [
          'High suspended sediment concentration in toe slope spring',
          'Internal aquifer piping failure / hydrostatic pore pressure breach',
          'Toe erosion scouring toe wall foundation (Alaknanda riverbed)',
        ];
        confidence = 0.915;
        baselineRisk = 76;
        break;
      case 'ROCKFALL_DEBRIS':
        primaryHazard = 'Active Rockfall & Scree Cone Formation';
        detectedFeatures = [
          'Fresh angular talus accumulation on highway carriage-way',
          'Recent crown scarp detachment (>50° slope gradient)',
          'Crushed retaining gabion mesh detected by edge-segmentation',
        ];
        confidence = 0.963;
        baselineRisk = 80;
        break;
      default:
        primaryHazard = 'General Mountain Slope Geotechnical Anomaly';
        detectedFeatures = [
          'Anomalous slope morphology detected via computer vision',
          'Vegetation displacement and soil scarp formation',
        ];
        confidence = 0.85;
        baselineRisk = 65;
    }

    const postVerificationRisk = Math.min(100, baselineRisk + riskBoost);

    return NextResponse.json({
      verificationId: `VLM-VERIFY-${Date.now()}`,
      status: 'VERIFIED_BY_VLM',
      model: 'YOLOv8-MountainGeoHazards-v2 + Llama-3-Vision-Edge',
      reporter: reporterType || 'Apda Mitra / BRO Road Patrol',
      sector: watershedSector || 'Joshimath - Marwari Flank (NH-07)',
      coordinates: gpsCoordinates || [30.556, 79.567],
      primaryHazard,
      confidenceScore: confidence,
      confidenceScorePct: Math.round(confidence * 100),
      detectedFeatures,
      riskImpact: {
        baselineRiskPct: baselineRisk,
        riskScoreBoostPct: riskBoost,
        postVerificationRiskPct: postVerificationRisk,
        escalationRecommended: postVerificationRisk >= 85 ? 'RED_EVACUATION' : 'ORANGE_ADVISORY',
      },
      actionableDirective:
        postVerificationRisk >= 85
          ? 'BRO Quick Reaction Team mobilized with heavy excavator; halt Char Dham convoys at nearest police checkpost.'
          : 'Issue geotechnical advisory to local SDM and deploy field surveyor for piezometer inspection.',
      timestamp: new Date().toISOString(),
    });
  } catch (err: any) {
    return NextResponse.json(
      { error: err.message || 'Error processing computer vision verification' },
      { status: 500 }
    );
  }
}
