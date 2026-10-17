"""
Authentic Uttarakhand Disaster CAP 1.2 Test Fixtures.
Modeled on historic Himalayan disaster events to exercise ingestion, geofencing,
multilingual resolution, and multi-channel dispatch pipelines without live credentials.
"""

from typing import Dict, Any, List
from backend.cap_schema import (
    CapAlertItem,
    AlertSeverity,
    HimalayanHazardType,
    CapUrgency,
    CapCertainty,
    CapStatus,
    CapMsgType,
    CapArea,
    LocalizedCapInfo,
    SupportedLocale,
)

# 1. 2013 Kedarnath Flash Flood & Cloudburst (Mandakini Valley)
FIXTURE_2013_KEDARNATH_CLOUDBURST = CapAlertItem(
    identifier="IN-UK-SEOC-2013-0616-KEDAR",
    sender="seoc.dehradun@uk.gov.in",
    senderName="Uttarakhand State Emergency Operation Centre",
    sent="2013-06-16T18:30:00+05:30",
    status=CapStatus.ACTUAL,
    msgType=CapMsgType.ALERT,
    scope="Public",
    hazardType=HimalayanHazardType.CLOUDBURST_SEVERE_STORM,
    severity=AlertSeverity.CRITICAL,
    urgency=CapUrgency.IMMEDIATE,
    certainty=CapCertainty.OBSERVED,
    districts=["Rudraprayag", "Chamoli"],
    area=CapArea(
        areaDesc="Mandakini River Valley, Kedarnath Shrine Basin, Rambara corridor",
        polygon=[[30.73, 79.06], [30.65, 79.02], [30.50, 78.98], [30.40, 79.00]],
    ),
    effective="2013-06-16T18:30:00+05:30",
    onset="2013-06-16T18:45:00+05:30",
    expires="2013-06-17T06:00:00+05:30",
    sourceFeed="IMD_NOWCAST",
    sourceLastUpdated="2013-06-16T18:30:00+05:30",
    localized={
        "en-IN": LocalizedCapInfo(
            language=SupportedLocale.EN_IN,
            headline="Catastrophic Cloudburst & Flash Flood Deluge: Mandakini Basin",
            description="Extreme convective cloudburst triggering high-velocity debris surge down Mandakini river.",
            instruction="Climb immediately to higher ridges above 2,500m. Vacate valley floor and riverbanks.",
            senderName="USDMA SEOC",
            event="Cloudburst / Flash Flood",
        ),
        "hi-IN": LocalizedCapInfo(
            language=SupportedLocale.HI_IN,
            headline="अत्यंत भीषण बादल फटना एवं आकस्मिक जलप्रलय: मंदाकिनी घाटी",
            description="केदारनाथ क्षेत्र में मूसलधार बादल फटने से मंदाकिनी नदी में विनाशकारी जलस्तर वृद्धि।",
            instruction="तुरंत नदी तट छोड़कर ऊंचे पहाड़ी डांडों पर शरण लें। निचले पुलों और गदेरों से दूर रहें।",
            senderName="USDMA SEOC",
            event="बादल फटना / आकस्मिक बाढ़",
        ),
        "gbm-IN": LocalizedCapInfo(
            language=SupportedLocale.GBM_IN,
            headline="मंदाकिनी मा मैल फाटण अर भयंकर बाढ़ी कु महासंकट",
            description="केदारनाथ मा भयानक मैल फाटि गे। मंदाकिनी गदेरा मा विकराल पाणी आणु च।",
            instruction="झटपट गदेरा बाटा दूर उचा डांडा मा चड़ि जावां। नदी कि बाणि बाटा भागी जावां।",
            senderName="USDMA SEOC",
            event="मैल फाटण",
        ),
        "kfy-IN": LocalizedCapInfo(
            language=SupportedLocale.KFY_IN,
            headline="मंदाकिनी घाटी मा मैल फाटन अर विकराल बाड़ि",
            description="केदारनाथ क्षेत्र मा मैल फाटण ले मंदाकिनी मा विकराल बाढ़ आ रै छ।",
            instruction="झटपट गाड़ किनार बाटी दूर डांड मा पुजि जा। उचै ठौर मा ओट ल्या।",
            senderName="USDMA SEOC",
            event="मैल फाटन",
        ),
    },
)

# 2. 2021 Chamoli GLOF / Rock-Ice Avalanche (Rishiganga & Dhauliganga)
FIXTURE_2021_CHAMOLI_GLOF = CapAlertItem(
    identifier="IN-UK-SEOC-2021-0207-CHAMOLI",
    sender="seoc.dehradun@uk.gov.in",
    senderName="DMMC Emergency Operations",
    sent="2021-02-07T10:15:00+05:30",
    status=CapStatus.ACTUAL,
    msgType=CapMsgType.ALERT,
    scope="Public",
    hazardType=HimalayanHazardType.FLASH_FLOOD_GLOF,
    severity=AlertSeverity.CRITICAL,
    urgency=CapUrgency.IMMEDIATE,
    certainty=CapCertainty.OBSERVED,
    districts=["Chamoli"],
    area=CapArea(
        areaDesc="Rishiganga, Dhauliganga, Alaknanda River Gorges (Raini to Joshimath)",
        polygon=[[30.55, 79.74], [30.48, 79.68], [30.56, 79.56], [30.55, 79.74]],
    ),
    effective="2021-02-07T10:15:00+05:30",
    onset="2021-02-07T10:20:00+05:30",
    expires="2021-02-07T18:00:00+05:30",
    sourceFeed="CWC_GAUGE",
    sourceLastUpdated="2021-02-07T10:15:00+05:30",
    localized={
        "en-IN": LocalizedCapInfo(
            language=SupportedLocale.EN_IN,
            headline="Glacial Breach Surge Watch: Rishiganga - Dhauliganga Confluence",
            description="Sudden rock-ice mass displacement created flash wave surging past Raini village toward Tapovan.",
            instruction="Move immediately 100 meters vertically uphill. Stay away from barrage tunnels and bridges.",
            senderName="DMMC Control",
            event="GLOF / Flash Flood",
        ),
        "hi-IN": LocalizedCapInfo(
            language=SupportedLocale.HI_IN,
            headline="हिमनद विस्फोट एवं आकस्मिक जल प्रलय: ऋषिगंगा-धौलीगंगा क्षेत्र",
            description="रैणी गांव के निकट हिमनद टूटने से भारी मलबे के साथ जलस्तर में तीव्र वृद्धि।",
            instruction="तुरंत 100 मीटर ऊंचे स्थानों पर चले जाएं। तपोवन बैराज और पुलों से दूर रहें।",
            senderName="DMMC Control",
            event="हिमनद झील विस्फोट",
        ),
        "gbm-IN": LocalizedCapInfo(
            language=SupportedLocale.GBM_IN,
            headline="धौलीगंगा अर ऋषिगंगा मा हिउँ फाटण अर बाढ़ी",
            description="रैणी का उप्पर हिउँ अर चट्टान टुटि गे। नदी मा भारी मलबा आणु च।",
            instruction="गाड़ी अर सड़क छोडि क डांडा मा भागी जावां। पुल बाटा दूर रवां।",
            senderName="DMMC Control",
            event="हिमनद आफत",
        ),
        "kfy-IN": LocalizedCapInfo(
            language=SupportedLocale.KFY_IN,
            headline="ऋषिगंगा मा हिउँ फाटन अर बाड़ि कु संकट",
            description="रैणी का उप्पर पहाड़ खिसकि गो। धौलीगंगा मा पाणी बड़ण लागो।",
            instruction="नदी किनार बाटी झटपट डांड मा पुजि जा। सुरक्षित जगह मा बैठा।",
            senderName="DMMC Control",
            event="हिउँ बाड़ि",
        ),
    },
)

# 3. Active Landslide & Slope Failure (NH-07 Sirobagarh Corridor)
FIXTURE_LANDSLIDE_NH07 = CapAlertItem(
    identifier="IN-UK-GSI-2026-0812-SLOPE",
    sender="gsi.dehradun@gov.in",
    senderName="Geological Survey of India Mountain Cell",
    sent="2026-08-12T14:00:00+05:30",
    status=CapStatus.ACTUAL,
    msgType=CapMsgType.ALERT,
    scope="Public",
    hazardType=HimalayanHazardType.LANDSLIDE_SLOPE_FAILURE,
    severity=AlertSeverity.SEVERE,
    urgency=CapUrgency.EXPECTED,
    certainty=CapCertainty.LIKELY,
    districts=["Rudraprayag", "Pauri Garhwal"],
    area=CapArea(
        areaDesc="NH-07 Badrinath National Highway, Sirobagarh active landslide zone",
        polygon=[[30.24, 78.85], [30.26, 78.88], [30.22, 78.90], [30.24, 78.85]],
    ),
    effective="2026-08-12T14:00:00+05:30",
    expires="2026-08-13T02:00:00+05:30",
    sourceFeed="GSI_BHUVAN",
    sourceLastUpdated="2026-08-12T14:00:00+05:30",
    localized={
        "en-IN": LocalizedCapInfo(
            language=SupportedLocale.EN_IN,
            headline="Severe Rockfall & Colluvial Slope Failure Warning: NH-07 Sirobagarh",
            description="Saturated schistose bedrock experiencing active shear failure. Heavy shooting stones active.",
            instruction="Suspend transit. Heavy vehicles must halt at Srinagar and Rudraprayag holding bays.",
            senderName="GSI / District Magistrate",
            event="Landslide / Rockfall",
        ),
        "hi-IN": LocalizedCapInfo(
            language=SupportedLocale.HI_IN,
            headline="गंभीर भूस्खलन एवं मलबा गिरने की चेतावनी: NH-07 सिरोबगड़",
            description="पहाड़ी ढलान से भारी पत्थर और मलबा लगातार गिर रहा है। मार्ग अवरुद्ध।",
            instruction="यात्रा तुरंत स्थगित करें। वाहन सुरक्षित स्थानों पर रोकें।",
            senderName="GSI / जिला प्रशासन",
            event="भूस्खलन",
        ),
        "gbm-IN": LocalizedCapInfo(
            language=SupportedLocale.GBM_IN,
            headline="सिरोबगड़ सड़क मा पवाड़ टुटण अर ढुंग गिरण कु खतरा",
            description="NH-07 सड़क मा बडू पहाड़ खिसकि गे। गाड़ी रोकि द्यावां।",
            instruction="गाड़ी सुरक्षित ठौर मा खडी करा। पवाड़ का नीच जन जावा।",
            senderName="जिला प्रशासन",
            event="पवाड़ टुटण",
        ),
        "kfy-IN": LocalizedCapInfo(
            language=SupportedLocale.KFY_IN,
            headline="NH-07 सिरोबगड़ मा पैरो गिरन कु बड़ो खतरा",
            description="पहाड़ बाटी भारी ढुंग गिर रई छन। रस्तो बंद च।",
            instruction="यात्रा रोक द्या। गाड़ी पक्की ठौर मा खडी करा।",
            senderName="जिला प्रशासन",
            event="पैरो गिरन",
        ),
    },
)

# 4. High-Magnitude Himalayan MCT Seismic Rupture (Zone V)
FIXTURE_SEISMIC_CHAMOLI_M6 = CapAlertItem(
    identifier="IN-UK-IITR-2026-0915-EEW",
    sender="eew.iitr@iitr.ac.in",
    senderName="IIT Roorkee Regional Earthquake Early Warning System",
    sent="2026-09-15T08:00:00+05:30",
    status=CapStatus.ACTUAL,
    msgType=CapMsgType.ALERT,
    scope="Public",
    hazardType=HimalayanHazardType.EARTHQUAKE_SEISMIC,
    severity=AlertSeverity.CRITICAL,
    urgency=CapUrgency.IMMEDIATE,
    certainty=CapCertainty.OBSERVED,
    districts=["Chamoli", "Rudraprayag", "Pithoragarh", "Bageshwar"],
    area=CapArea(
        areaDesc="Main Central Thrust (MCT) Fault Belt, Chamoli-Pipalkoti Epicenter",
        polygon=[[30.40, 79.30], [30.60, 79.50], [30.20, 79.70], [30.10, 79.20]],
    ),
    effective="2026-09-15T08:00:00+05:30",
    onset="2026-09-15T08:00:15+05:30",
    expires="2026-09-15T12:00:00+05:30",
    sourceFeed="IITR_EEW",
    sourceLastUpdated="2026-09-15T08:00:00+05:30",
    localized={
        "en-IN": LocalizedCapInfo(
            language=SupportedLocale.EN_IN,
            headline="EARTHQUAKE EARLY WARNING: Magnitude 6.2 Detected near Chamoli",
            description="P-wave sensors triggered. S-wave destructive shaking arriving in 15-30 seconds.",
            instruction="DROP, COVER, AND HOLD ON. Extinguish stoves. Move away from glass and weak masonry.",
            senderName="IIT Roorkee EEW",
            event="Earthquake Warning",
        ),
        "hi-IN": LocalizedCapInfo(
            language=SupportedLocale.HI_IN,
            headline="भूकंप पूर्व चेतावनी: चमोली के निकट 6.2 तीव्रता का भूकंप दर्ज",
            description="विनाशकारी झटके अगले 15-30 सेकंड में पहुंचने का अनुमान है।",
            instruction="झुको, ढको और पकड़ो (ड्रॉप, कवर, होल्ड ऑन)। खुले सुरक्षित मैदान में जाएं।",
            senderName="IIT रुड़की EEW",
            event="भूकंप चेतावनी",
        ),
        "gbm-IN": LocalizedCapInfo(
            language=SupportedLocale.GBM_IN,
            headline="भूचाल की पैली चेताउनी: चमोली मा बडू भूकंप",
            description="तेज झटकु आउण वाळु च। झटपट सम्भळि जावां।",
            instruction="झुकां, ढकां अर मजबूत चीज तैं धैरि राखवां। खुला मैदान मा भागी जावां।",
            senderName="IIT रुड़की",
            event="भूचाल",
        ),
        "kfy-IN": LocalizedCapInfo(
            language=SupportedLocale.KFY_IN,
            headline="भूचाल चेताउनी: चमोली मा बड़ो भूचाल दर्ज",
            description="तेज झटका आउन वाल छन। झटपट सतर्क रया।",
            instruction="झुका, ढका अर मजबुत चीज धैरि रया। खुला मैदान मा जावा।",
            senderName="IIT रुड़की",
            event="भूचाल",
        ),
    },
)

# 5. Forest Fire Outbreak (Chir Pine Belt, Pauri Garhwal)
FIXTURE_FOREST_FIRE_PAURI = CapAlertItem(
    identifier="IN-UK-FSI-2026-0520-FIRE",
    sender="fsi.vanagni@gov.in",
    senderName="Forest Survey of India / Uttarakhand Forest Dept",
    sent="2026-05-20T11:00:00+05:30",
    status=CapStatus.ACTUAL,
    msgType=CapMsgType.ALERT,
    scope="Public",
    hazardType=HimalayanHazardType.FOREST_FIRE,
    severity=AlertSeverity.SEVERE,
    urgency=CapUrgency.EXPECTED,
    certainty=CapCertainty.OBSERVED,
    districts=["Pauri Garhwal"],
    area=CapArea(
        areaDesc="Khirsu and Pauri Pine Forest Corridor, Ridges 3 and 4",
        polygon=[[30.12, 78.75], [30.18, 78.82], [30.10, 78.85], [30.12, 78.75]],
    ),
    effective="2026-05-20T11:00:00+05:30",
    expires="2026-05-21T06:00:00+05:30",
    sourceFeed="FOREST_FIRE_TRACK",
    sourceLastUpdated="2026-05-20T11:00:00+05:30",
    localized={
        "en-IN": LocalizedCapInfo(
            language=SupportedLocale.EN_IN,
            headline="Chir Pine Wildfire Warning: High-Wind Flame Front Advancing",
            description="Severe canopy and ground pine-needle wildfire breaching secondary ridge firebreak.",
            instruction="Clear 10m defensible zone around homesteads. Evacuate downhill away from windward front.",
            senderName="Forest Dept SEOC",
            event="Forest Fire",
        ),
        "hi-IN": LocalizedCapInfo(
            language=SupportedLocale.HI_IN,
            headline="चीड़ वन अग्नि चेतावनी: तीव्र हवाओं के साथ वनाग्नि का प्रसार",
            description="खिर्सू क्षेत्र में वनाग्नि रिहायशी बस्तियों की ओर बढ़ रही है।",
            instruction="बस्तियों के चारों ओर फायरलाइन साफ करें। हवा की विपरीत दिशा में नीचे की ओर निकलें।",
            senderName="वन विभाग / SEOC",
            event="वनाग्नि",
        ),
        "gbm-IN": LocalizedCapInfo(
            language=SupportedLocale.GBM_IN,
            headline="पौड़ी का जंगल मा कुलां की भयंकर आग",
            description="हवा का झोका से आग बस्त्युं कि तरफ आणी च।",
            instruction="घर का चौतरफ सफाई करा। हवा का उलट दिशा मा भागी जावां।",
            senderName="वन विभाग",
            event="कुलां की आग",
        ),
        "kfy-IN": LocalizedCapInfo(
            language=SupportedLocale.KFY_IN,
            headline="जंगल मा भयंकर दावानल / आग कु खतरा",
            description="तेज हवा ले आग बस्ती का कानी बढ़ रई छ।",
            instruction="घर का चौतरफ सफाई राखि रया। हवा का उलट दिशा मा भागा।",
            senderName="वन विभाग",
            event="दावानल",
        ),
    },
)

# 6. Heavy Snowfall & Avalanche Warning (High Mountain Passes, Uttarkashi)
FIXTURE_AVALANCHE_UTTARKASHI = CapAlertItem(
    identifier="IN-UK-DGRE-2026-0125-SNOW",
    sender="dgre.sase@drdo.gov.in",
    senderName="Defence Geo-Informatics Research Establishment (DGRE / SASE)",
    sent="2026-01-25T07:00:00+05:30",
    status=CapStatus.ACTUAL,
    msgType=CapMsgType.ALERT,
    scope="Public",
    hazardType=HimalayanHazardType.AVALANCHE_SNOWFALL,
    severity=AlertSeverity.ADVISORY,
    urgency=CapUrgency.FUTURE,
    certainty=CapCertainty.POSSIBLE,
    districts=["Uttarkashi"],
    area=CapArea(
        areaDesc="Harsil, Gangotri Highway Corridor, Slopes above 3,200m",
        polygon=[[31.00, 78.70], [31.10, 78.90], [30.95, 78.85], [31.00, 78.70]],
    ),
    effective="2026-01-25T07:00:00+05:30",
    expires="2026-01-26T18:00:00+05:30",
    sourceFeed="AVALANCHE_MONITOR",
    sourceLastUpdated="2026-01-25T07:00:00+05:30",
    localized={
        "en-IN": LocalizedCapInfo(
            language=SupportedLocale.EN_IN,
            headline="High-Altitude Snowfall & Stage-3 Avalanche Danger Advisory",
            description="Heavy fresh snowfall on unstable faceted depth hoar layer. Natural releases expected.",
            instruction="Avoid travel along slopes exceeding 30 degrees. Carry avalanche beacon and probe.",
            senderName="DGRE / SASE",
            event="Avalanche Advisory",
        ),
        "hi-IN": LocalizedCapInfo(
            language=SupportedLocale.HI_IN,
            headline="हिमस्खलन एवं भारी बर्फबारी परामर्श: उत्तरकाशी उच्च हिमालय",
            description="गंगोत्री अक्ष पर 3,200 मीटर से ऊपर हिमस्खलन की मध्यम से उच्च संभावना।",
            instruction="खड़ी ढलानों से दूर रहें। अनावश्यक यात्रा से बचें।",
            senderName="DGRE / SASE",
            event="हिमस्खलन परामर्श",
        ),
        "gbm-IN": LocalizedCapInfo(
            language=SupportedLocale.GBM_IN,
            headline="उत्तरकाशी का डांड्युं मा हिउँ खिसकण कु परामर्श",
            description="उच्च हिमालय मा भारी बर्फबारी। डांडा बाटा बर्फ खिसकि सकद।",
            instruction="खड़ी ढलानों मा जन जावा। मौसम साफ होणा तक रुका।",
            senderName="SASE",
            event="हिउँ खिसकण",
        ),
        "kfy-IN": LocalizedCapInfo(
            language=SupportedLocale.KFY_IN,
            headline="उत्तरकाशी मा हिउँ गिरन अर बर्फबारी की सलाह",
            description="ऊंचा डांड मा हिउँ गिरन कु खतरा च। सतर्क रया।",
            instruction="खतरनाक डांड बाटी दूर रया। यात्रा जन करा।",
            senderName="SASE",
            event="हिउँ गिरन",
        ),
    },
)

# 7. Deliberately Malformed CAP Payload (Testing Pipeline Validation & Exception Handling)
FIXTURE_MALFORMED_CAP_PAYLOAD: Dict[str, Any] = {
    "identifier": "",  # Empty mandatory identifier
    "sender": "invalid-email-address",
    "status": "NON_EXISTENT_STATUS",
    "msgType": "BOGUS_TYPE",
    "area": {
        "areaDesc": "Outside territorial bounds",
        "polygon": [[10.0, 50.0]],  # Violates Uttarakhand spatial bounding box
    },
    "localized": {},  # Missing localized info blocks
}

ALL_HISTORIC_FIXTURES: List[CapAlertItem] = [
    FIXTURE_2013_KEDARNATH_CLOUDBURST,
    FIXTURE_2021_CHAMOLI_GLOF,
    FIXTURE_LANDSLIDE_NH07,
    FIXTURE_SEISMIC_CHAMOLI_M6,
    FIXTURE_FOREST_FIRE_PAURI,
    FIXTURE_AVALANCHE_UTTARKASHI,
]
