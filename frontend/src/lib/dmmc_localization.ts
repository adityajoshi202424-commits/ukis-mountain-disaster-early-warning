/**
 * DMMC Uttarakhand Localization & UI Dynamic String Store
 * Strict weather.gov/alerts functional feature parity adapted for Uttarakhand's 13 districts.
 * ZERO HARDCODED CONSTANTS: All UI labels, district names, survival checklists,
 * and button strings are loaded dynamically from this central matrix.
 * Locales: English (en-IN), Hindi (hi-IN), Garhwali (gbm-IN), Kumaoni (kfy-IN).
 */

export type DmmcLocale = 'en-IN' | 'hi-IN' | 'gbm-IN' | 'kfy-IN';

export interface GuidebookItem {
  id: string;
  hazardType: string;
  title: string;
  before: string[];
  during: string[];
  after: string[];
  helpline: string;
}

export interface LocalizationBundle {
  appName: string;
  appSubtitle: string;
  tabs: {
    alerts: string;
    map: string;
    guidebook: string;
  };
  sosButton: string;
  sosModalTitle: string;
  sosModalDesc: string;
  sosCall112: string;
  sosCall1070: string;
  sosDispatchBeacon: string;
  sosBeaconSuccess: string;
  drawerTitle: string;
  selectLanguage: string;
  phoneNumberLabel: string;
  phoneNumberPlaceholder: string;
  deviceTokenLabel: string;
  forceSyncButton: string;
  emergencyHotlinesLabel: string;
  filterDistrictLabel: string;
  allDistricts: string;
  liveFeedStatus: string;
  reconnectingStatus: string;
  viewOnMapButton: string;
  guidebookTitle: string;
  offlineReadyBadge: string;
  emergencyGuidebook: GuidebookItem[];
  districts: Record<string, string>;
  severityLabels: {
    CRITICAL: string;
    SEVERE: string;
    ADVISORY: string;
    NORMAL: string;
  };
  // Weather.gov Parity Keys
  noActiveAlertsTitle: string;
  noActiveAlertsDesc: string;
  dataUnavailableTitle: string;
  dataUnavailableDesc: string;
  weatherGovParityTitle: string;
  filtersTitle: string;
  filterSeverityLabel: string;
  filterUrgencyLabel: string;
  filterCertaintyLabel: string;
  filterHazardLabel: string;
  allFilterOption: string;
  capModalTitle: string;
  capFieldHeadline: string;
  capFieldEvent: string;
  capFieldSeverity: string;
  capFieldUrgency: string;
  capFieldCertainty: string;
  capFieldEffective: string;
  capFieldExpires: string;
  capFieldOnset: string;
  capFieldEnds: string;
  capFieldSender: string;
  capFieldAreaDesc: string;
  capFieldInstruction: string;
  capFieldDescription: string;
  lastSyncedLabel: string;
  offlineCachedNotice: string;
  viewCapDetailsButton: string;
  closeButton: string;
}

export const DMMC_LOCALIZATIONS: Record<DmmcLocale, LocalizationBundle> = {
  'en-IN': {
    appName: 'DMMC Uttarakhand Early-Warning Platform',
    appSubtitle: 'Government of Uttarakhand • Disaster Mitigation & Management Centre',
    tabs: {
      alerts: 'Active Alerts',
      map: 'Live Map & Shelters',
      guidebook: 'Emergency Guidebook',
    },
    sosButton: '🚨 EMERGENCY SOS: CALL 112',
    sosModalTitle: 'EMERGENCY 112 / DISASTER SOS',
    sosModalDesc: 'Initiating immediate distress signal to State Emergency Operation Centre (1070) & National 112.',
    sosCall112: '📞 Call 112 (National)',
    sosCall1070: '📞 Call 1070 (State SEOC)',
    sosDispatchBeacon: 'Transmit SOS GPS Beacon to Command Control',
    sosBeaconSuccess: '✓ SOS Distress Beacon Transmitted with GPS Coordinates',
    drawerTitle: 'DMMC Control & Profile Drawer',
    selectLanguage: 'Choose Regional Language',
    phoneNumberLabel: 'Subscriber Mobile Number (for SMS Dispatches)',
    phoneNumberPlaceholder: '+91 98XXXXXXXX',
    deviceTokenLabel: 'Device Push Notification Token',
    forceSyncButton: 'Force Language Handshake Sync',
    emergencyHotlinesLabel: 'Official Emergency Hotlines',
    filterDistrictLabel: 'District Focus:',
    allDistricts: 'All Mountain Districts',
    liveFeedStatus: 'LIVE TELEMETRY',
    reconnectingStatus: 'CONNECTING...',
    viewOnMapButton: 'View on Bhuvan GIS Map →',
    guidebookTitle: 'Emergency Preparedness & Survival Guidebook',
    offlineReadyBadge: 'Preloaded for Zero-Network Offline Use',
    noActiveAlertsTitle: 'No Active Warnings, Watches, or Advisories',
    noActiveAlertsDesc: 'There are no active alerts issued for this district. Operational sensors report baseline telemetry. Continuous 24/7 monitoring active.',
    dataUnavailableTitle: 'Institutional Feeds Gated (Awaiting DMMC Provisioning)',
    dataUnavailableDesc: 'Telemetry feed adapters fail closed until institutional credentials and endpoints are provisioned in .env.production. No fake alerts are displayed.',
    weatherGovParityTitle: 'Uttarakhand Active Hazard Bulletins',
    filtersTitle: 'Filter Active Hazards',
    filterSeverityLabel: 'Severity:',
    filterUrgencyLabel: 'Urgency:',
    filterCertaintyLabel: 'Certainty:',
    filterHazardLabel: 'Hazard Event:',
    allFilterOption: 'ALL',
    capModalTitle: 'Common Alerting Protocol (CAP 1.2) Detail Record',
    capFieldHeadline: 'Official Headline',
    capFieldEvent: 'Hazard Event',
    capFieldSeverity: 'CAP Severity',
    capFieldUrgency: 'CAP Urgency',
    capFieldCertainty: 'CAP Certainty',
    capFieldEffective: 'Effective From',
    capFieldExpires: 'Expires At',
    capFieldOnset: 'Expected Onset',
    capFieldEnds: 'Estimated End',
    capFieldSender: 'Issuing Agency',
    capFieldAreaDesc: 'Affected Mountain Region',
    capFieldInstruction: 'Protective Directives',
    capFieldDescription: 'Hazard Technical Overview',
    lastSyncedLabel: 'Last Telemetry Sync',
    offlineCachedNotice: 'OFFLINE CACHED BULLETIN — ZERO CONNECTIVITY MODE',
    viewCapDetailsButton: 'View Full CAP 1.2 Record →',
    closeButton: 'Close',
    districts: {
      Dehradun: 'Dehradun District',
      Uttarkashi: 'Uttarkashi District',
      Chamoli: 'Chamoli District',
      Rudraprayag: 'Rudraprayag District',
      'Tehri Garhwal': 'Tehri Garhwal District',
      'Pauri Garhwal': 'Pauri Garhwal District',
      Pithoragarh: 'Pithoragarh District',
      Bageshwar: 'Bageshwar District',
      Almora: 'Almora District',
      Champawat: 'Champawat District',
      Nainital: 'Nainital District',
      Haridwar: 'Haridwar District',
      'Udham Singh Nagar': 'Udham Singh Nagar District',
    },
    severityLabels: {
      CRITICAL: 'CRITICAL (Immediate Action Required)',
      SEVERE: 'SEVERE (Prepare Protective Measures)',
      ADVISORY: 'ADVISORY (Monitor Conditions)',
      NORMAL: 'NORMAL (Baseline Telemetry Clear)',
    },
    emergencyGuidebook: [
      {
        id: 'guide-glof-flood',
        hazardType: 'FLASH_FLOOD_GLOF',
        title: 'Flash Floods & Glacial Outbursts (GLOF)',
        before: ['Identify high-ground evacuation ridge paths.', 'Keep waterproof 72-hour survival kit ready.'],
        during: ['At sirens or roar, immediately climb uphill away from riverbeds.', 'Never cross swollen mountain streams.'],
        after: ['Stay at designated high ground until official USDMA clearance.'],
        helpline: '1070',
      },
      {
        id: 'guide-landslide',
        hazardType: 'LANDSLIDE_MUDSLIDE',
        title: 'Landslides, Mudslides & Slope Failures',
        before: ['Inspect hillside slope retaining walls for new tension cracks.', 'Avoid building near steep colluvial fans.'],
        during: ['Run perpendicular to slope direction if rumble is heard.', 'Seek shelter behind large bedrock outcroppings.'],
        after: ['Watch for secondary slope slides triggered by trapped groundwater.'],
        helpline: '1077',
      },
      {
        id: 'guide-cloudburst',
        hazardType: 'CLOUDBURST',
        title: 'Cloudbursts & Convective Storms',
        before: ['Keep drainage chutes cleared of debris.'],
        during: ['Seek structural shelter on elevated foundations.', 'Stay out of valley-bottom culverts.'],
        after: ['Inspect foundation integrity before re-entering buildings.'],
        helpline: '1070',
      },
      {
        id: 'guide-earthquake',
        hazardType: 'EARTHQUAKE',
        title: 'Earthquakes (Seismic Zone IV & V)',
        before: ['Fasten heavy overhead objects; identify safe doorframes or reinforced corners.'],
        during: ['Drop, Cover, and Hold On. Move to open ground if safely outdoors.'],
        after: ['Shut off LPG cylinders. Expect severe mountain aftershocks.'],
        helpline: '112',
      },
      {
        id: 'guide-avalanche',
        hazardType: 'AVALANCHE',
        title: 'High-Altitude Avalanches & Heavy Snowfall',
        before: ['Check DGRE / SASE avalanche danger bulletin before traversing passes.'],
        during: ['If caught, swim upward and create an air pocket in front of mouth with cupped hands.'],
        after: ['Conserve oxygen. Blow whistle or trigger reflective beacon.'],
        helpline: '1077',
      },
      {
        id: 'guide-forestfire',
        hazardType: 'FOREST_FIRE',
        title: 'Chir Pine Forest Fires',
        before: ['Maintain 10-meter cleared firebreak around settlements.'],
        during: ['Evacuate downhill or crosswind away from the fire front.', 'Breathe through wet cloth.'],
        after: ['Douse hot pine needle embers.'],
        helpline: '1070',
      },
    ],
  },
  'hi-IN': {
    appName: 'आपदा न्यूनीकरण एवं प्रबंधन केंद्र (DMMC)',
    appSubtitle: 'उत्तराखंड शासन • प्रारंभिक चेतावनी एवं आपदा प्रबंधन प्रणाली',
    tabs: {
      alerts: 'सक्रिय चेतावनियाँ',
      map: 'लाइव मानचित्र एवं शरण स्थल',
      guidebook: 'आपदा मार्गदर्शिका',
    },
    sosButton: '🚨 आपातकालीन SOS: 112 डायल करें',
    sosModalTitle: 'आपातकालीन 112 / आपदा SOS सहायता',
    sosModalDesc: 'राज्य आपदा परिचालन केंद्र (1070) एवं राष्ट्रीय आपातकाल 112 को त्वरित संकट संदेश प्रेषित किया जा रहा है।',
    sosCall112: '📞 112 पर कॉल करें (राष्ट्रीय)',
    sosCall1070: '📞 1070 पर कॉल करें (राज्य SEOC)',
    sosDispatchBeacon: 'कंट्रोल रूम को जीपीएस संकट बीकन भेजें',
    sosBeaconSuccess: '✓ जीपीएस निर्देशांकों के साथ संकट संकेत सफलतापूर्वक भेजा गया',
    drawerTitle: 'DMMC नियंत्रण एवं प्रोफाइल विवरण',
    selectLanguage: 'क्षेत्रीय भाषा का चयन करें',
    phoneNumberLabel: 'मोबाइल नंबर (SMS चेतावनी प्रसारण हेतु)',
    phoneNumberPlaceholder: '+91 98XXXXXXXX',
    deviceTokenLabel: 'डिवाइस पुश टोकन',
    forceSyncButton: 'भाषा प्राथमिकता सिंक करें',
    emergencyHotlinesLabel: 'आधिकारिक आपातकालीन नंबर',
    filterDistrictLabel: 'जनपद चयन:',
    allDistricts: 'समस्त पर्वतीय जनपद',
    liveFeedStatus: 'लाइव टेलीमेट्री',
    reconnectingStatus: 'कनेक्ट हो रहा है...',
    viewOnMapButton: 'भुवन जीआईएस मानचित्र पर देखें →',
    guidebookTitle: 'आपदा सुरक्षा एवं जीवन रक्षा मार्गदर्शिका',
    offlineReadyBadge: 'बिना इंटरनेट ऑफलाइन उपयोग हेतु प्रीलोडेड',
    noActiveAlertsTitle: 'कोई सक्रिय चेतावनी, अलर्ट या परामर्श नहीं',
    noActiveAlertsDesc: 'इस जनपद के लिए वर्तमान में कोई आपातकालीन चेतावनी सक्रिय नहीं है। परिचालन सेंसर सामान्य स्थिति दर्शाते हैं। 24/7 निगरानी सक्रिय है।',
    dataUnavailableTitle: 'संस्थागत टेलीमेट्री अनुपलब्ध (DMMC क्रेडेंशियल्स की प्रतीक्षा)',
    dataUnavailableDesc: 'जब तक DMMC द्वारा वास्तविक क्रेडेंशियल्स प्रदान नहीं किए जाते, सिस्टम सुरक्षित रूप से डेटा अनुपलब्ध दर्शाता है। कोई नकली अलर्ट नहीं दिखाए जाते।',
    weatherGovParityTitle: 'उत्तराखंड सक्रिय आपदा बुलेटिन',
    filtersTitle: 'सक्रिय आपदाओं को फ़िल्टर करें',
    filterSeverityLabel: 'गंभीरता:',
    filterUrgencyLabel: 'तात्कालिकता:',
    filterCertaintyLabel: 'निश्चितता:',
    filterHazardLabel: 'आपदा प्रकार:',
    allFilterOption: 'सभी',
    capModalTitle: 'कॉमन अलर्टिंग प्रोटोकॉल (CAP 1.2) आधिकारिक विवरण',
    capFieldHeadline: 'शीर्षक',
    capFieldEvent: 'आपदा प्रकार',
    capFieldSeverity: 'गंभीरता स्तर',
    capFieldUrgency: 'तात्कालिकता',
    capFieldCertainty: 'निश्चितता',
    capFieldEffective: 'प्रभावी समय',
    capFieldExpires: 'समाप्ति समय',
    capFieldOnset: 'प्रारंभ समय',
    capFieldEnds: 'संभावित अंत',
    capFieldSender: 'जारीकर्ता संस्था',
    capFieldAreaDesc: 'प्रभावित पर्वतीय क्षेत्र',
    capFieldInstruction: 'सुरक्षा निर्देश',
    capFieldDescription: 'तकनीकी विवरण',
    lastSyncedLabel: 'अंतिम टेलीमेट्री सिंक',
    offlineCachedNotice: 'ऑफलाइन संगृहीत बुलेटिन — शून्य नेटवर्क मोड',
    viewCapDetailsButton: 'पूर्ण CAP 1.2 रिकॉर्ड देखें →',
    closeButton: 'बंद करें',
    districts: {
      Dehradun: 'देहरादून जनपद',
      Uttarkashi: 'उत्तरकाशी जनपद',
      Chamoli: 'चमोली जनपद',
      Rudraprayag: 'रुद्रप्रयाग जनपद',
      'Tehri Garhwal': 'टिहरी गढ़वाल जनपद',
      'Pauri Garhwal': 'पौड़ी गढ़वाल जनपद',
      Pithoragarh: 'पिथौरागढ़ जनपद',
      Bageshwar: 'बागेश्वर जनपद',
      Almora: 'अल्मोड़ा जनपद',
      Champawat: 'चंपावत जनपद',
      Nainital: 'नैनीताल जनपद',
      Haridwar: 'हरिद्वार जनपद',
      'Udham Singh Nagar': 'ऊधम सिंह नगर जनपद',
    },
    severityLabels: {
      CRITICAL: 'गंभीर चेतावनी (तत्काल सुरक्षित स्थान पर जाएं)',
      SEVERE: 'गंभीर सतर्कता (कार्रवाई हेतु तैयार रहें)',
      ADVISORY: 'परामर्श निगरानी (नवीनतम जानकारी रखें)',
      NORMAL: 'सामान्य स्थिति (प्रणाली सुरक्षित)',
    },
    emergencyGuidebook: [
      {
        id: 'guide-glof-flood',
        hazardType: 'FLASH_FLOOD_GLOF',
        title: 'आकस्मिक बाढ़ एवं हिमनद झील विस्फोट (GLOF)',
        before: ['निकटतम ऊंचे डांडे की पहचान रखें।', '72 घंटे की आपातकालीन किट तैयार रखें।'],
        during: ['अलर्ट मिलते ही नदी तटों से तुरंत दूर ऊंचे स्थान पर जाएं।', 'बहते पानी में वाहन न चलाएं।'],
        after: ['जब तक प्रशासन अनुमति न दे, नदी किनारे न लौटें।'],
        helpline: '1070',
      },
      {
        id: 'guide-landslide',
        hazardType: 'LANDSLIDE_MUDSLIDE',
        title: 'भूस्खलन एवं मलबा गिरने का खतरा',
        before: ['पहाड़ी ढलानों पर पड़ी दरारों पर नजर रखें।', 'गदेरों के मुहाने पर निर्माण न करें।'],
        during: ['गड़गड़ाहट सुनते ही ढलान के लंबवत सुरक्षित दिशा में भागें।'],
        after: ['द्वितीयक भूस्खलन से सावधान रहें।'],
        helpline: '1077',
      },
      {
        id: 'guide-cloudburst',
        hazardType: 'CLOUDBURST',
        title: 'बादल फटने की घटना (क्लाउडबर्स्ट)',
        before: ['नालों और गदेरों को साफ रखें।'],
        during: ['पक्के भवनों में शरण लें। बरसाती नालों से दूर रहें।'],
        after: ['भवन की नींव जांचने के बाद ही भीतर जाएं।'],
        helpline: '1070',
      },
      {
        id: 'guide-earthquake',
        hazardType: 'EARTHQUAKE',
        title: 'भूकंप (भूकंपीय क्षेत्र IV / V)',
        before: ['भारी वस्तुओं को मजबूती से बांधें।'],
        during: ['झुको, ढको और पकड़ो (ड्रॉप, कवर, होल्ड ऑन)।'],
        after: ['गैस सिलेंडर बंद करें। आफ्टरशॉक से सावधान रहें।'],
        helpline: '112',
      },
      {
        id: 'guide-avalanche',
        hazardType: 'AVALANCHE',
        title: 'हिमस्खलन एवं भारी बर्फबारी',
        before: ['DGRE बुलेटिन की जांच करें।'],
        during: ['ऊपर की ओर तैरने की कोशिश करें और मुंह के आगे हवा का गड्ढा बनाएं।'],
        after: ['ऑक्सीजन बचाएं। सीटी बजाएं।'],
        helpline: '1077',
      },
      {
        id: 'guide-forestfire',
        hazardType: 'FOREST_FIRE',
        title: 'चीड़ वनों की आग (वनाग्नि)',
        before: ['बस्तियों के चारों ओर 10 मीटर की फायरलाइन बनाएं।'],
        during: ['हवा की विपरीत दिशा में ढलान से नीचे की ओर निकलें।'],
        after: ['सुलगते अंगारों पर पानी डालें।'],
        helpline: '1070',
      },
    ],
  },
  'gbm-IN': {
    appName: 'गढ़वाळ आपदा प्रबंधन केंद्र (DMMC)',
    appSubtitle: 'उत्तराखंड सरकार • डांड्युं मा बाढ़ी अर आफत की पैली चेताउनी',
    tabs: {
      alerts: 'सक्रिय चेतावनियाँ',
      map: 'नक्शा अर ओट',
      guidebook: 'बचाव पोथी',
    },
    sosButton: '🚨 आपातकाल SOS: 112 लगावां',
    sosModalTitle: 'आपातकालीन 112 / आपदा SOS सहायता',
    sosModalDesc: 'देहरादून कंट्रोल रूम (1070) अर 112 मा सीधा संदेश भेजणू च।',
    sosCall112: '📞 112 लगावां (देश)',
    sosCall1070: '📞 1070 लगावां (उत्तराखंड)',
    sosDispatchBeacon: 'कंट्रोल रूम मा अपणू जीपीएस संदेश भेजा',
    sosBeaconSuccess: '✓ डांडा बाटा जीपीएस संदेश पहुंचि गे',
    drawerTitle: 'DMMC खाता अर व्यवस्था',
    selectLanguage: 'भाषा छांटा',
    phoneNumberLabel: 'फोन नंबर (SMS खातिर)',
    phoneNumberPlaceholder: '+91 98XXXXXXXX',
    deviceTokenLabel: 'फोन पहचान टोकन',
    forceSyncButton: 'भाषा सिंक करा',
    emergencyHotlinesLabel: 'मदद खातिर नंबर',
    filterDistrictLabel: 'जिलु छांटा:',
    allDistricts: 'सबै पहाड़ी जिलु',
    liveFeedStatus: 'सीधा प्रसारण',
    reconnectingStatus: 'जुड़णू च...',
    viewOnMapButton: 'भुवन नक्शा मा देखा →',
    guidebookTitle: 'पहाड़ मा आपदा बाटा बचण कु रस्ता',
    offlineReadyBadge: 'बिना नेटवर्क कु पोथी तैयार',
    noActiveAlertsTitle: 'कोइ बाढ़ी या आफत कु अलर्ट न्है',
    noActiveAlertsDesc: 'ये जिलु मा अबी कोइ आफत कु संदेश न्है। पाणी अर डांडा सामान्य च। २४ घंटा पहरेदारी जारी च।',
    dataUnavailableTitle: 'सरकारी क्रेडेंशियल प्रतीक्षारत (Fail-Closed)',
    dataUnavailableDesc: 'जब तक सरकारि टोकन .env.production मा नी जुड़दा, सिस्टम डेटा उपलब्ध न्है बतालु। कोइ झुठु अलर्ट नी देखैलु।',
    weatherGovParityTitle: 'उत्तराखंड आफत चेताउनी बुलेटिन',
    filtersTitle: 'चेताउनी छांटा',
    filterSeverityLabel: 'खतरा:',
    filterUrgencyLabel: 'जल्दी:',
    filterCertaintyLabel: 'पक्की बात:',
    filterHazardLabel: 'आपदा:',
    allFilterOption: 'सबै',
    capModalTitle: 'CAP 1.2 पुरा सरकारी विवरण',
    capFieldHeadline: 'मुख्य खबर',
    capFieldEvent: 'आपदा प्रकार',
    capFieldSeverity: 'खतरा स्तर',
    capFieldUrgency: 'तात्कालिकता',
    capFieldCertainty: 'सत्यता',
    capFieldEffective: 'शुरू बखत',
    capFieldExpires: 'खतम बखत',
    capFieldOnset: 'आउण कु बखत',
    capFieldEnds: 'समाप्ति',
    capFieldSender: 'सरकारी विभाग',
    capFieldAreaDesc: 'प्रभावित पहाड़ी इलाका',
    capFieldInstruction: 'बचाव कु हुकुम',
    capFieldDescription: 'पूरी बात',
    lastSyncedLabel: 'अंतिम सिंक',
    offlineCachedNotice: 'नेटवर्क बिना पुरानु बुलेटिन',
    viewCapDetailsButton: 'पुरा CAP 1.2 विवरण देखा →',
    closeButton: 'बंद करा',
    districts: {
      Dehradun: 'देहरादून जिलु',
      Uttarkashi: 'उत्तरकाशी जिलु',
      Chamoli: 'चमोली जिलु',
      Rudraprayag: 'रुद्रप्रयाग जिलु',
      'Tehri Garhwal': 'टिहरी गढ़वाळ जिलु',
      'Pauri Garhwal': 'पौड़ी गढ़वाळ जिलु',
      Pithoragarh: 'पिथौरागढ़ जिलु',
      Bageshwar: 'बागेश्वर जिलु',
      Almora: 'अल्मोड़ा जिलु',
      Champawat: 'चंपावत जिलु',
      Nainital: 'नैनीताल जिलु',
      Haridwar: 'हरिद्वार जिलु',
      'Udham Singh Nagar': 'ऊधम सिंह नगर जिलु',
    },
    severityLabels: {
      CRITICAL: 'भारी आफत (तुरंत डांडा मा चड़ि जावां)',
      SEVERE: 'बडू खतरा (सतर्क रवां)',
      ADVISORY: 'ध्यान द्या (खबर राखवां)',
      NORMAL: 'शान्त माहौल (सब ठीक च)',
    },
    emergencyGuidebook: [
      {
        id: 'guide-glof-flood',
        hazardType: 'FLASH_FLOOD_GLOF',
        title: 'गदेरा मा बाढ़ी अर ताल फुटण कु संकट',
        before: ['उचै डांडा मा जाण कु रस्तो पहल्यां तैं तय करा।'],
        during: ['सायरन सुणदा ही गदेरा बाटा दूर डांडा मा भागी जावां।'],
        after: ['अधिकारी जब तक नी बोलदा, नदी का किनार जन आवा।'],
        helpline: '1070',
      },
      {
        id: 'guide-landslide',
        hazardType: 'LANDSLIDE_MUDSLIDE',
        title: 'पहाड़ टुटण अर पवाड़ खिसकण कु खतरा',
        before: ['डांडा मा पड़ी फाट पर नजर राखवां।'],
        during: ['आवाज आणा पर सीधी दिशा मा भागी जावां।'],
        after: ['नया मलबा मा गोड जन धैरा।'],
        helpline: '1077',
      },
      {
        id: 'guide-cloudburst',
        hazardType: 'CLOUDBURST',
        title: 'मैल फाटण अर भयंकर बरखा',
        before: ['गदेरा की बाणि खुली राखवां।'],
        during: ['पक्की छत का नीच ओट ल्यावां।'],
        after: ['घर की नींव जांचा।'],
        helpline: '1070',
      },
      {
        id: 'guide-earthquake',
        hazardType: 'EARTHQUAKE',
        title: 'भूचाल / भूकंप (ज़ोन IV अर V)',
        before: ['घर की दीवार पर भारी सामान नी लटकावा।'],
        during: ['झुकां, ढकां अर मजबूत चीज तैं धैरि राखवां।'],
        after: ['सिलेंडर बंद करा।'],
        helpline: '112',
      },
      {
        id: 'guide-avalanche',
        hazardType: 'AVALANCHE',
        title: 'हिउँ खिसकण अर बर्फबारी',
        before: ['SASE बुलेटिन देखा।'],
        during: ['बर्फ मा उप्पर तैराण की कोसिस करा।'],
        after: ['सीटी बजावां।'],
        helpline: '1077',
      },
      {
        id: 'guide-forestfire',
        hazardType: 'FOREST_FIRE',
        title: 'कुलां की आग (दावानल)',
        before: ['घर का चौतरफ 10 मीटर की सफाई राखवां।'],
        during: ['हवा का उलट दिशा मा भागा।'],
        after: ['अंगार मा पाणी छांटा।'],
        helpline: '1070',
      },
    ],
  },
  'kfy-IN': {
    appName: 'कुमाऊं आपदा प्रबंधन केंद्र (DMMC)',
    appSubtitle: 'उत्तराखंड सरकार • डांड मा बाड़ि अर आफत की पैली चेताउनी',
    tabs: {
      alerts: 'सक्रिय चेताउनियां',
      map: 'नक्श अर ओट',
      guidebook: 'सुरक्षा पोथी',
    },
    sosButton: '🚨 आपातकाल SOS: 112 लगावा',
    sosModalTitle: 'आपातकालीन 112 / आपदा SOS सहायता',
    sosModalDesc: 'कंट्रोल रूम (1070) अर 112 मा संदेश भेजूं छौं।',
    sosCall112: '📞 112 लगावा (देश)',
    sosCall1070: '📞 1070 लगावा (उत्तराखंड)',
    sosDispatchBeacon: 'कंट्रोल रूम मा जीपीएस संदेश भेजा',
    sosBeaconSuccess: '✓ जीपीएस संदेश पहुँच गो',
    drawerTitle: 'DMMC खाता अर प्रोफाइल',
    selectLanguage: 'भाषा छांटा',
    phoneNumberLabel: 'मोबाइल नंबर (SMS खातिर)',
    phoneNumberPlaceholder: '+91 98XXXXXXXX',
    deviceTokenLabel: 'फोन टोकन',
    forceSyncButton: 'भाषा सिंक करा',
    emergencyHotlinesLabel: 'मदद खातिर नंबर',
    filterDistrictLabel: 'जिलु छांटा:',
    allDistricts: 'सब्बै पहाड़ी जिलु',
    liveFeedStatus: 'सीधा प्रसारण',
    reconnectingStatus: 'जुड़ूं छ...',
    viewOnMapButton: 'भुवन नक्श मा देखा →',
    guidebookTitle: 'आपदा बाटी बचन की पोथी',
    offlineReadyBadge: 'नेटवर्क बिना पोथी तैयार',
    noActiveAlertsTitle: 'कोइ बाड़ि या आफत कु अलर्ट न्ही',
    noActiveAlertsDesc: 'ये जिलु मा अबी कोइ आफत कु संदेश न्ही। गाड़ अर डांड शान्त छन। २४ घंटा निगरानी चालू छ।',
    dataUnavailableTitle: 'सरकारी क्रेडेंशियल प्रतीक्षारत (Fail-Closed)',
    dataUnavailableDesc: 'जब तलक सरकारि क्रेडेंशियल .env.production मा न्ही जुड़ना, सिस्टम डेटा उपलब्ध न्ही बताल। कोइ झुठु अलर्ट न्ही दिखौल।',
    weatherGovParityTitle: 'उत्तराखंड आफत चेताउनी बुलेटिन',
    filtersTitle: 'चेताउनी छांटा',
    filterSeverityLabel: 'खतरा:',
    filterUrgencyLabel: 'तात्कालिकता:',
    filterCertaintyLabel: 'सत्यता:',
    filterHazardLabel: 'आपदा:',
    allFilterOption: 'सब्बै',
    capModalTitle: 'CAP 1.2 पूरो सरकारी विवरण',
    capFieldHeadline: 'मुख्य खबर',
    capFieldEvent: 'आपदा प्रकार',
    capFieldSeverity: 'खतरा स्तर',
    capFieldUrgency: 'तात्कालिकता',
    capFieldCertainty: 'सत्यता',
    capFieldEffective: 'शुरू बखत',
    capFieldExpires: 'खतम बखत',
    capFieldOnset: 'प्रारंभ',
    capFieldEnds: 'अंत',
    capFieldSender: 'सरकारी विभाग',
    capFieldAreaDesc: 'प्रभावित इलाका',
    capFieldInstruction: 'बचाव कु हुकुम',
    capFieldDescription: 'पूरी बात',
    lastSyncedLabel: 'अंतिम सिंक',
    offlineCachedNotice: 'नेटवर्क बिना पुरानु बुलेटिन',
    viewCapDetailsButton: 'पूरो CAP 1.2 विवरण देखा →',
    closeButton: 'बंद करा',
    districts: {
      Dehradun: 'देहरादून जिलु',
      Uttarkashi: 'उत्तरकाशी जिलु',
      Chamoli: 'चमोली जिलु',
      Rudraprayag: 'रुद्रप्रयाग जिलु',
      'Tehri Garhwal': 'टिहरी गढ़वाल जिलु',
      'Pauri Garhwal': 'पौड़ी गढ़वाल जिलु',
      Pithoragarh: 'पिथौरागढ़ जिलु',
      Bageshwar: 'बागेश्वर जिलु',
      Almora: 'अल्मोड़ा जिलु',
      Champawat: 'चंपावत जिलु',
      Nainital: 'नैनीताल जिलु',
      Haridwar: 'हरिद्वार जिलु',
      'Udham Singh Nagar': 'ऊधम सिंह नगर जिलु',
    },
    severityLabels: {
      CRITICAL: 'भारी आफत (झटपट उचै ठांव मा जा)',
      SEVERE: 'बड़ो खतरा (सतर्क रया)',
      ADVISORY: 'ध्यान दिया (खबर राखि रया)',
      NORMAL: 'शान्त माहौल (सब भलो छ)',
    },
    emergencyGuidebook: [
      {
        id: 'guide-glof-flood',
        hazardType: 'FLASH_FLOOD_GLOF',
        title: 'गाड़ मा बाड़ि अर ताल फुटण कु खतरा',
        before: ['उचै डांड मा जान कु रस्तो पैली तय करा।'],
        during: ['सायरन सुणते ही गाड़ किनार बाटी दूर डांड मा भागी जा।'],
        after: ['जब तलक हुकुम न मिले, नदी किनार जन आया।'],
        helpline: '1070',
      },
      {
        id: 'guide-landslide',
        hazardType: 'LANDSLIDE_MUDSLIDE',
        title: 'पैरो गिरन अर डांड खिसकन कु खतरा',
        before: ['पहाड़ मा पड़ी दरार पर नजर राखि रया।'],
        during: ['आवाज आणा पर सुरक्षित दिशा मा भागा।'],
        after: ['नया मलबा पर जन हिंडा।'],
        helpline: '1077',
      },
      {
        id: 'guide-cloudburst',
        hazardType: 'CLOUDBURST',
        title: 'मैल फाटन अर मूसलधार बरखा',
        before: ['नाल खुला राखि रया।'],
        during: ['पक्के घर का भितर ओट ल्या।'],
        after: ['घर की नींव जाँचा।'],
        helpline: '1070',
      },
      {
        id: 'guide-earthquake',
        hazardType: 'EARTHQUAKE',
        title: 'भूचाल / भूकंप (ज़ोन IV अर V)',
        before: ['भारी सामान नी लटकावा।'],
        during: ['झुका, ढका अर मजबुत चीज धैरि रया।'],
        after: ['सिलेंडर बंद करा।'],
        helpline: '112',
      },
      {
        id: 'guide-avalanche',
        hazardType: 'AVALANCHE',
        title: 'हिउँ खिसकन अर भारी बर्फबारी',
        before: ['SASE बुलेटिन देखा।'],
        during: ['बर्फ मा उप्पर तैरण की कोसिस करा।'],
        after: ['सीटी बजावा।'],
        helpline: '1077',
      },
      {
        id: 'guide-forestfire',
        hazardType: 'FOREST_FIRE',
        title: 'कुलां की आग (दावानल)',
        before: ['घर का चौतरफ 10 मीटर की सफाई राखि रया।'],
        during: ['हवा का उलट दिशा मा भागा।'],
        after: ['अंगार मा पाणी छांटा।'],
        helpline: '1070',
      },
    ],
  },
};
