export interface HimKavachSector {
  id: string;
  name: string;
  district: string;
  highwayCorridor: string;
  hazardType: 'GLOF' | 'LANDSLIDE' | 'SUBSIDENCE' | 'CLOUDBURST' | 'CASCADING_SURGE';
  coordinates: [number, number];
  elevationM: number;
  slopeDeg: number;
  mctFaultProximityKm: number;
  twiIndex: number;
  currentRiskScore: number;
  threatLevel: 'NOMINAL' | 'ELEVATED' | 'CRITICAL' | 'EXTREME';
  shapAttribution: {
    cumulativeRainPct: number;
    slopeFaultProximityPct: number;
    insarSubsidencePct: number;
    vegetationLossPct: number;
  };
  sensorHealth: {
    status: 'IOT_GROUND_LIVE' | 'SATELLITE_INTERPOLATED' | 'FAILOVER_SYNTHETIC';
    confidenceScorePct: number;
    lastPingSecondsAgo: number;
  };
  historicalAnalog: {
    matchedEvent: string;
    similarityScorePct: number;
    dateOfEvent: string;
    historicalImpactSummary: string;
  };
  trafficHaltingGate: {
    policeCheckpost: string;
    highwayStatus: 'OPEN' | 'HOLD_AT_GATE' | 'DIVERT_PILGRIMS' | 'EVACUATE_CORRIDOR';
    pilgrimCapacityHolding: number;
    holdingShelterName: string;
  };
  isolationVulnerability: {
    isolatedVillages: string[];
    affectedPopulationEst: number;
    nearestSdrfUnit: string;
    sdrfEtaMinutes: number;
    jcbStagingPoint: string;
    nearestHelipad: string;
  };
  bilingualBulletins: {
    english: string;
    hindi: string;
  };
}

export interface CascadingStep {
  stepIndex: number;
  timeOffsetMin: number;
  headline: string;
  surgeDischargeM3s: number;
  waveVelocityMs: number;
  activeThreatColor: string;
  summary: string;
  actionRequired: string;
}

export const HIM_KAVACH_SECTORS: HimKavachSector[] = [
  {
    id: 'SEC-JOSHIMATH-NH07',
    name: 'Joshimath - Marwari Subsidence & Toe-Slope Flank',
    district: 'Chamoli',
    highwayCorridor: 'NH-07 (Badrinath Highway)',
    hazardType: 'SUBSIDENCE',
    coordinates: [30.556, 79.567],
    elevationM: 1890,
    slopeDeg: 38.5,
    mctFaultProximityKm: 2.1,
    twiIndex: 8.4,
    currentRiskScore: 78,
    threatLevel: 'CRITICAL',
    shapAttribution: {
      cumulativeRainPct: 42,
      slopeFaultProximityPct: 29,
      insarSubsidencePct: 21,
      vegetationLossPct: 8,
    },
    sensorHealth: {
      status: 'IOT_GROUND_LIVE',
      confidenceScorePct: 98,
      lastPingSecondsAgo: 14,
    },
    historicalAnalog: {
      matchedEvent: 'January 2023 Joshimath Aquifer Breach & Foundation Fissures',
      similarityScorePct: 91,
      dateOfEvent: 'January 2–5, 2023',
      historicalImpactSummary: 'Rapid subsidence (-5.4 cm/month) triggered foundational cracks across 860 structures; NH-07 transit halted.',
    },
    trafficHaltingGate: {
      policeCheckpost: 'Joshimath Cantonment / Pandukeshwar Gate (NH-07)',
      highwayStatus: 'HOLD_AT_GATE',
      pilgrimCapacityHolding: 1200,
      holdingShelterName: 'Joshimath GMVN Safe Elevation Transit Camp (Elev: 1950m)',
    },
    isolationVulnerability: {
      isolatedVillages: ['Mana Village', 'Helang Ward 3', 'Ravigram Upper'],
      affectedPopulationEst: 4200,
      nearestSdrfUnit: 'SDRF 3rd Battalion Joshimath Company HQ',
      sdrfEtaMinutes: 18,
      jcbStagingPoint: 'BRO Project Shivalik Depot (Km 42)',
      nearestHelipad: 'Joshimath Military Cantonment Helipad',
    },
    bilingualBulletins: {
      english: 'DEOC CHAMOLI EMERGENCY ORDER: NH-07 corridor near Joshimath toe slope flagged at 78% risk due to cumulative rainwater seepage. All Badrinath upward pilgrim traffic held at Pandukeshwar barrier. SDRF Quick Response Team on stand-by.',
      hindi: 'जिला आपदा नियंत्रण केंद्र चमोली आदेश: जोशीमठ के समीप NH-07 ढलान पर अत्यधिक पानी रिसाव के कारण 78% भूस्खलन खतरा। बद्रीनाथ जा रहे समस्त वाहनों को पांडुकेश्वर बैरियर पर रोका गया है। सुरक्षित GMVN शेल्टर में शरण लें।',
    },
  },
  {
    id: 'SEC-VASUNDHARA-GLOF',
    name: 'Vasudhara Tal Glacial Moraine Catchment',
    district: 'Chamoli',
    highwayCorridor: 'Alaknanda High Catchment (Mana-Badrinath)',
    hazardType: 'GLOF',
    coordinates: [30.795, 79.435],
    elevationM: 4500,
    slopeDeg: 46.0,
    mctFaultProximityKm: 1.4,
    twiIndex: 9.1,
    currentRiskScore: 84,
    threatLevel: 'EXTREME',
    shapAttribution: {
      cumulativeRainPct: 48,
      slopeFaultProximityPct: 27,
      insarSubsidencePct: 18,
      vegetationLossPct: 7,
    },
    sensorHealth: {
      status: 'IOT_GROUND_LIVE',
      confidenceScorePct: 95,
      lastPingSecondsAgo: 8,
    },
    historicalAnalog: {
      matchedEvent: 'February 2021 Chamoli Rishi Ganga Rock-Ice Avalanche',
      similarityScorePct: 88,
      dateOfEvent: 'February 7, 2021',
      historicalImpactSummary: 'Detachment of 27M m³ ice/rock mass at 5,600m caused 1,600 m³/s surge bore, destroying downstream Tapovan hydro intake within 15 mins.',
    },
    trafficHaltingGate: {
      policeCheckpost: 'Mana Military Checkpost / Govindghat Barrier',
      highwayStatus: 'EVACUATE_CORRIDOR',
      pilgrimCapacityHolding: 2500,
      holdingShelterName: 'Shri Badrinath Dharamshala High-Ground Haven (Cap: 800)',
    },
    isolationVulnerability: {
      isolatedVillages: ['Mana Border Post', 'Lambagarh Settlement', 'Ghat Sector'],
      affectedPopulationEst: 2800,
      nearestSdrfUnit: 'SDRF High-Altitude Rescue Platoon, Badrinath',
      sdrfEtaMinutes: 25,
      jcbStagingPoint: 'BRO Mana Pass Construction Detachment',
      nearestHelipad: 'Badrinath Army Aviation Helipad',
    },
    bilingualBulletins: {
      english: 'FLASH FLOOD & GLOF RED ALERT: Vasudhara Tal proglacial moraine breach threshold elevated. Estimated surge wave ETA to lower bridge: 28 minutes. Evacuate riverbeds immediately to high ground.',
      hindi: 'आकस्मिक बाढ़ एवं GLOF रेड अलर्ट: वसुंधरा ताल हिमनद झील मोरेन पर अत्यधिक जल दबाव। निचले पुल तक बाढ़ की लहर पहुँचने का अनुमानित समय 28 मिनट। तुरंत अलकनंदा तटों से ऊंचे डांडों पर चले जाएं।',
    },
  },
  {
    id: 'SEC-SIROBAGAD-NH07',
    name: 'Sirobagad Chronic Landslide Funnel (NH-07)',
    district: 'Pauri Garhwal',
    highwayCorridor: 'NH-07 (Srinagar - Rudraprayag Axis)',
    hazardType: 'LANDSLIDE',
    coordinates: [30.252, 78.892],
    elevationM: 680,
    slopeDeg: 52.0,
    mctFaultProximityKm: 3.8,
    twiIndex: 7.9,
    currentRiskScore: 71,
    threatLevel: 'CRITICAL',
    shapAttribution: {
      cumulativeRainPct: 45,
      slopeFaultProximityPct: 35,
      insarSubsidencePct: 12,
      vegetationLossPct: 8,
    },
    sensorHealth: {
      status: 'IOT_GROUND_LIVE',
      confidenceScorePct: 99,
      lastPingSecondsAgo: 5,
    },
    historicalAnalog: {
      matchedEvent: 'August 2023 Sirobagad Chronic Slope Failure',
      similarityScorePct: 89,
      dateOfEvent: 'August 14, 2023',
      historicalImpactSummary: 'Continuous rock debris blocked NH-07 for 38 hours, stranding 4,000 Char Dham pilgrims between Srinagar and Rudraprayag.',
    },
    trafficHaltingGate: {
      policeCheckpost: 'Srinagar Dam Gate / Kirtinagar Barrier',
      highwayStatus: 'HOLD_AT_GATE',
      pilgrimCapacityHolding: 1800,
      holdingShelterName: 'HNB Garhwal University Campus Assembly Hall (Cap: 800)',
    },
    isolationVulnerability: {
      isolatedVillages: ['Sirobagad Hamlet', 'Kaleshwar Basti', 'Chhapan Bhog Colony'],
      affectedPopulationEst: 1900,
      nearestSdrfUnit: 'SDRF Company Srinagar Garhwal',
      sdrfEtaMinutes: 12,
      jcbStagingPoint: 'NHAI Heavy Excavator Station Sirobagad North',
      nearestHelipad: 'Srinagar SSB Training Ground Helipad',
    },
    bilingualBulletins: {
      english: 'NH-07 SIROBAGAD ALERT: 72h continuous rainfall has saturated fragile phyllite rock face (52° slope). NH-07 traffic halted at Srinagar checkpost. Excavators stationed for active debris clearing.',
      hindi: 'NH-07 सिरोबगड़ भूस्खलन चेतावनी: 72 घंटे की बारिश से 52° खड़ी ढलान अत्यधिक कमजोर। श्रीनगर चेकपोस्ट पर वाहनों को रोका गया। मलबा हटाने के लिए जेसीबी तैनात।',
    },
  },
  {
    id: 'SEC-BALIANALA-NAINITAL',
    name: 'Balianala Toe-Erosion & Slope Creep Corridor',
    district: 'Nainital',
    highwayCorridor: 'NH-109 / Nainital Lake Valley Basin',
    hazardType: 'LANDSLIDE',
    coordinates: [29.381, 79.458],
    elevationM: 1938,
    slopeDeg: 42.0,
    mctFaultProximityKm: 6.2,
    twiIndex: 8.8,
    currentRiskScore: 66,
    threatLevel: 'ELEVATED',
    shapAttribution: {
      cumulativeRainPct: 38,
      slopeFaultProximityPct: 32,
      insarSubsidencePct: 20,
      vegetationLossPct: 10,
    },
    sensorHealth: {
      status: 'SATELLITE_INTERPOLATED',
      confidenceScorePct: 82,
      lastPingSecondsAgo: 45,
    },
    historicalAnalog: {
      matchedEvent: 'September 2021 Balianala Hill Toe Collapse',
      similarityScorePct: 84,
      dateOfEvent: 'September 18, 2021',
      historicalImpactSummary: 'Subsurface aquifer seepage eroded toe of Krol rock; 120 houses evacuated in Rais Hotel and Harinagar wards.',
    },
    trafficHaltingGate: {
      policeCheckpost: 'Jeolikote Toll Barrier / Tallital Police Outpost',
      highwayStatus: 'DIVERT_PILGRIMS',
      pilgrimCapacityHolding: 950,
      holdingShelterName: 'Nainital Club High-Ground Assembly Hall (Cap: 500)',
    },
    isolationVulnerability: {
      isolatedVillages: ['Harinagar Ward 4', 'Krishnapur Settlement', 'Balia Riparian'],
      affectedPopulationEst: 3100,
      nearestSdrfUnit: 'SDRF Team Nainital / Police Lines',
      sdrfEtaMinutes: 15,
      jcbStagingPoint: 'PWD Nainital Yard Sukhatal',
      nearestHelipad: 'Nainital Golf Course / Cantonment Flat Ground',
    },
    bilingualBulletins: {
      english: 'NAINITAL DEOC ADVISORY: Balianala slope moisture saturation index elevated to 76%. Municipal geotechnical alert in effect for Harinagar ward. Heavy vehicles diverted via Bhimtal route.',
      hindi: 'नैनीताल आपदा नियंत्रण परामर्श: बलियानाला ढलान पर जल संतृप्ति स्तर 76% तक बढ़ा। हरिनगर एवं कृष्णापुर क्षेत्र में सतर्कता। भारी वाहनों को भवाली-भीमताल मार्ग पर डायवर्ट किया गया।',
    },
  },
  {
    id: 'SEC-CHORABARI-KEDAR',
    name: 'Chorabari Moraine Basin & Mandakini Gorge',
    district: 'Rudraprayag',
    highwayCorridor: 'NH-107 (Kedarnath Trek Axis)',
    hazardType: 'GLOF',
    coordinates: [30.738, 79.068],
    elevationM: 3960,
    slopeDeg: 45.0,
    mctFaultProximityKm: 0.9,
    twiIndex: 9.4,
    currentRiskScore: 82,
    threatLevel: 'EXTREME',
    shapAttribution: {
      cumulativeRainPct: 50,
      slopeFaultProximityPct: 25,
      insarSubsidencePct: 18,
      vegetationLossPct: 7,
    },
    sensorHealth: {
      status: 'IOT_GROUND_LIVE',
      confidenceScorePct: 96,
      lastPingSecondsAgo: 10,
    },
    historicalAnalog: {
      matchedEvent: 'June 2013 Kedarnath Multi-Basin Deluge',
      similarityScorePct: 94,
      dateOfEvent: 'June 16–17, 2013',
      historicalImpactSummary: 'Chorabari moraine failure caused 1,450 m³/s surge wave traveling at 8.2 m/s, washing away Sonprayag, Rambara, and Kedarnath base structures.',
    },
    trafficHaltingGate: {
      policeCheckpost: 'Sonprayag Registration Gate / Guptkashi Barrier (NH-107)',
      highwayStatus: 'HOLD_AT_GATE',
      pilgrimCapacityHolding: 3500,
      holdingShelterName: 'Guptkashi Govt Intermediate College Safe Haven (Cap: 600)',
    },
    isolationVulnerability: {
      isolatedVillages: ['Kedarnath Shrine Township', 'Lincheli Post', 'Junglechatti'],
      affectedPopulationEst: 5400,
      nearestSdrfUnit: 'SDRF High-Altitude Quick Reaction Unit Kedarnath Mandir',
      sdrfEtaMinutes: 10,
      jcbStagingPoint: 'PWD Sonprayag Parking Terminal',
      nearestHelipad: 'Kedarnath Helipad & Guptkashi Helipad Hub',
    },
    bilingualBulletins: {
      english: 'KEDARNATH MANDAKINI EVACUATION BULLETIN: Freezing level isotherm at 4,200m combined with 65mm rain. Upward yatra trek from Sonprayag suspended immediately. Pilgrims directed to permanent shelters.',
      hindi: 'केदारनाथ मंदाकिनी आपातकालीन बुलेटिन: 4,200 मीटर हिमांक स्तर एवं तेज वर्षा के कारण चोराबाड़ी क्षेत्र में जलस्तर बढ़ा। सोनप्रयाग से ऊपर की पैदल यात्रा तुरंत स्थगित। श्रद्धालु पक्के आश्रमों में रुकें।',
    },
  },
];

export const CASCADING_SIMULATION_STEPS: CascadingStep[] = [
  {
    stepIndex: 0,
    timeOffsetMin: 0,
    headline: 'T+00 min: Convective Cloudburst / GLOF Moraine Overtopping at 4,500m',
    surgeDischargeM3s: 1450,
    waveVelocityMs: 8.5,
    activeThreatColor: '#EF4444',
    summary: 'Cloudburst triggers catastrophic moraine dam overtopping at Vasudhara Tal / Chorabari basin at 4,500m. 1,450 m³/s initial bore released into narrow gorge.',
    actionRequired: 'Automated 120dB river siren triggers at Alpine Sector; C-DOT Cell Broadcast dispatched to Channel 4370.',
  },
  {
    stepIndex: 1,
    timeOffsetMin: 20,
    headline: 'T+20 min: Surge Inundates Upper Tapovan / Hydro Intake Gorges',
    surgeDischargeM3s: 1320,
    waveVelocityMs: 7.8,
    activeThreatColor: '#DC2626',
    summary: 'Flood crest bore strikes downstream hydropower intake tunnels at 7.8 m/s (~28 km/h). Water height rises 11.2 meters above winter baseline.',
    actionRequired: 'BRO and hydro barrage gates opened for full spillway clearance; workers evacuated from tunnel portals.',
  },
  {
    stepIndex: 2,
    timeOffsetMin: 45,
    headline: 'T+45 min: Wavefront Strikes Joshimath Lower Bridge & Undercuts Slopes',
    surgeDischargeM3s: 1180,
    waveVelocityMs: 7.1,
    activeThreatColor: '#B91C1C',
    summary: 'Bore wave reaches Joshimath Marwari bridge. High-velocity river scour severely undercuts unstable toe slopes, accelerating ancient landslide slip planes.',
    actionRequired: 'NH-07 traffic halted at Pandukeshwar; police divert Char Dham buses into Joshimath Cantonment shelters.',
  },
  {
    stepIndex: 3,
    timeOffsetMin: 75,
    headline: 'T+75 min: Helang & Pipalkoti River Road Undermined; Secondary Landslides',
    surgeDischargeM3s: 980,
    waveVelocityMs: 6.4,
    activeThreatColor: '#991B1B',
    summary: 'Secondary rockfalls and debris avalanches triggered on NH-07 hillsides. Road foundation fissures detected by BRO telemetry.',
    actionRequired: 'JCB excavators staged at Km 42 mobilized; SDRF platoon deploys safety ropes along high-ridge detour.',
  },
  {
    stepIndex: 4,
    timeOffsetMin: 120,
    headline: 'T+120 min: Surge Confluence at Karnaprayag; Pindar Backwater Swell',
    surgeDischargeM3s: 820,
    waveVelocityMs: 5.6,
    activeThreatColor: '#7F1D1D',
    summary: 'Alaknanda surge reaches Karnaprayag sangam. Pindar river backwater swell creates temporary localized ponding in market areas.',
    actionRequired: 'DEOC orders evacuation of riverfront market shops to GIC Karnaprayag; siren sounds continuous warble.',
  },
  {
    stepIndex: 5,
    timeOffsetMin: 180,
    headline: 'T+180 min: Srinagar Hydro Dam Reservoir Attenuates Flood Crest',
    surgeDischargeM3s: 640,
    waveVelocityMs: 4.8,
    activeThreatColor: '#10B981',
    summary: 'Srinagar hydro dam pre-depletion reservoir safely absorbs 640 m³/s peak crest. Downstream Rishikesh and Haridwar maintain safe freeboard.',
    actionRequired: 'DEOC issues all-clear transition for lower plains; damage assessment teams deployed to upper reach.',
  },
];
