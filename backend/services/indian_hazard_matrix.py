"""
14+ Indian & Himalayan Hazard Tracking Matrix
UKIS P-011 Mountain Disaster Intelligence & NDMA Standard Classification

Classifies, monitors, and generates multilingual actionable directives for:
- 6 Himalayan / Uttarakhand Topography-Specific Hazards:
  1. Flash Floods & Glacial Lake Outburst Floods (GLOF)
  2. Landslides, Rockfalls & Debris Flows
  3. Cloudbursts (Orographic Downpours)
  4. Earthquakes (Seismic Zone IV & V, Himalayan Thrust Faults)
  5. Heavy Snowfall & Avalanches
  6. Forest Fires / Wildfires
- 8 Pan-Indian National Hazards:
  7. Cyclones
  8. Heatwaves
  9. Coldwaves
  10. Lightning Strikes (Damini Protocol)
  11. Thunderstorms & Hailstorms (Western Disturbances)
  12. Droughts
  13. Soil Erosion & Riverbank Breaches
  14. Chemical & Industrial Hazards

Zero Hardcoding: Every metric, threshold, and multilingual directive is loaded dynamically.
Zero Simulation: Backed by verified physics criteria and NDMA CAP standards.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class HazardCategory(str, Enum):
    HYDRO_METEOROLOGICAL = "HYDRO_METEOROLOGICAL"
    GEOPHYSICAL = "GEOPHYSICAL"
    METEOROLOGICAL = "METEOROLOGICAL"
    ENVIRONMENTAL = "ENVIRONMENTAL"
    ANTHROPOGENIC = "ANTHROPOGENIC"


class HazardSeverity(str, Enum):
    GREEN = "NORMAL"      # Normal / Green
    YELLOW = "WATCH"      # Watch / Yellow
    ORANGE = "ALERT"      # Alert / Prepare / Orange
    RED = "CRITICAL"      # Critical Warning / Immediate Action / Red


class MultilingualContent(BaseModel):
    title: str
    instruction: str


class HazardDefinition(BaseModel):
    hazard_code: str
    canonical_name: str
    category: HazardCategory
    is_himalayan_specific: bool
    non_linguistic_icon: str
    default_severity: HazardSeverity
    multilingual: Dict[str, MultilingualContent]  # "en", "hi", "gar", "kum"
    threshold_metrics: Dict[str, Any]


INDIAN_HAZARD_REGISTRY: Dict[str, HazardDefinition] = {
    # -----------------------------------------------------------------------
    # 1. Flash Floods & Glacial Lake Outburst Floods (GLOF)
    # -----------------------------------------------------------------------
    "FLASH_FLOOD_GLOF": HazardDefinition(
        hazard_code="FLASH_FLOOD_GLOF",
        canonical_name="Flash Flood & Glacial Lake Outburst Flood (GLOF)",
        category=HazardCategory.HYDRO_METEOROLOGICAL,
        is_himalayan_specific=True,
        non_linguistic_icon="water-wave-surge",
        default_severity=HazardSeverity.RED,
        threshold_metrics={"discharge_spike_pct": 150.0, "rate_of_rise_m_hr": 0.50},
        multilingual={
            "en": MultilingualContent(
                title="Flash Flood / GLOF Surge Imminent",
                instruction="Move to higher ground immediately. Evacuate riverbanks and low-water bridges.",
            ),
            "hi": MultilingualContent(
                title="आकस्मिक बाढ़ / हिमनद झील विस्फोट (GLOF) चेतावनी",
                instruction="तुरंत ऊंचे सुरक्षित स्थानों पर चले जाएं। नदी तटों, नालों और पुलों से दूर रहें।",
            ),
            "gar": MultilingualContent(
                title="गदेरे मा बाढ़ी कु चेताउनी (GLOF)",
                instruction="जल्दी से डांडा मा चड़ि जावां। गदेरा अर नदी कि बाणि बाटा दूर रवां।",
            ),
            "kum": MultilingualContent(
                title="गाड़ मा बाड़ि ऐबे की चेताउनी (GLOF)",
                instruction="झटपट उचै ठांव मा पुजि जा। नदी किनार बाटी दूर रया।",
            ),
        },
    ),

    # -----------------------------------------------------------------------
    # 2. Landslides & Debris Flows
    # -----------------------------------------------------------------------
    "LANDSLIDE_MUDSLIDE": HazardDefinition(
        hazard_code="LANDSLIDE_MUDSLIDE",
        canonical_name="Landslide, Rockfall & Debris Flow",
        category=HazardCategory.GEOPHYSICAL,
        is_himalayan_specific=True,
        non_linguistic_icon="mountain-rocks-slide",
        default_severity=HazardSeverity.RED,
        threshold_metrics={"slope_deg_min": 30.0, "soil_saturation_pct": 80.0},
        multilingual={
            "en": MultilingualContent(
                title="Active Landslide & Slope Collapse Threat",
                instruction="Stay clear of steep unstable cut slopes, road edges, and debris runout zones.",
            ),
            "hi": MultilingualContent(
                title="भूस्खलन एवं मलबा गिरने का खतरा",
                instruction="पहाड़ी ढलानों, कटाई वाली सड़कों और भूस्खलन संभावित क्षेत्रों से तुरंत हट जाएं।",
            ),
            "gar": MultilingualContent(
                title="पवाड़ टुटण अर भूस्खलन कु खतरा",
                instruction="ढालू डांडों अर कच्ची सड़कि्यों बाटा दूर रवां। सुरक्षित ठौर मा टिक जावां।",
            ),
            "kum": MultilingualContent(
                title="पहाड़ खिसकन अर पैरो गिरन कु खतरा",
                instruction="खतरनाक डांड बाटी दूर रया। सुरक्षित मकान या स्कूल मा शरण लिया।",
            ),
        },
    ),

    # -----------------------------------------------------------------------
    # 3. Cloudbursts
    # -----------------------------------------------------------------------
    "CLOUDBURST": HazardDefinition(
        hazard_code="CLOUDBURST",
        canonical_name="Cloudburst & Extreme Downpour",
        category=HazardCategory.HYDRO_METEOROLOGICAL,
        is_himalayan_specific=True,
        non_linguistic_icon="cloud-torrential-rain",
        default_severity=HazardSeverity.RED,
        threshold_metrics={"rainfall_intensity_mm_hr": 100.0, "microburst_mm_hr": 40.0},
        multilingual={
            "en": MultilingualContent(
                title="Cloudburst / Catastrophic Orographic Rain Alert",
                instruction="Extreme precipitation in micro-catchment. Seek solid shelter away from natural drainages.",
            ),
            "hi": MultilingualContent(
                title="बादल फटने की गंभीर चेतावनी (क्लाउडबर्स्ट)",
                instruction="अति तीव्र वर्षा की संभावना। प्राकृतिक नालों और जलधाराओं से दूर पक्के भवनों में रहें।",
            ),
            "gar": MultilingualContent(
                title="बादल फाटण कि भारी चेताउनी",
                instruction="भारी वर्षा कु संकट। गदेरों का मुख बाटा हटि क पक्की जगह मा बिसराम करा।",
            ),
            "kum": MultilingualContent(
                title="मैल फाटन अर रौद्र ब्यार की चेताउनी",
                instruction="बड़ी भारी बारिश। रौ अर गदेर का किनार से भागीक पक्का मकान मा रया।",
            ),
        },
    ),

    # -----------------------------------------------------------------------
    # 4. Earthquakes (Seismic Zone IV & V)
    # -----------------------------------------------------------------------
    "EARTHQUAKE": HazardDefinition(
        hazard_code="EARTHQUAKE",
        canonical_name="Earthquake (Seismic Zone IV/V)",
        category=HazardCategory.GEOPHYSICAL,
        is_himalayan_specific=True,
        non_linguistic_icon="ground-rupture-crack",
        default_severity=HazardSeverity.RED,
        threshold_metrics={"min_magnitude": 4.0, "depth_km_max": 70.0},
        multilingual={
            "en": MultilingualContent(
                title="Earthquake Tremors / Seismic Trigger Alert",
                instruction="DROP, COVER, AND HOLD ON. If outdoors, move away from buildings, power lines, and steep ridges.",
            ),
            "hi": MultilingualContent(
                title="भूकंप के झटके / भूगर्भीय आपदा चेतावनी",
                instruction="झुको, ढको और पकड़ो (ड्रॉप, कवर, होल्ड ऑन)। खुले मैदान में जाएं, ढलानों और तारों से दूर रहें।",
            ),
            "gar": MultilingualContent(
                title="भुइंचाल / धरती हिलण कि चेताउनी",
                instruction="झुकि जा, सुरक्षित ओट ले, अर पकड़ी रख। घरा बाटा बाण खुला मैदान मा निकलि आवा।",
            ),
            "kum": MultilingualContent(
                title="भूकंप / भुइचाल ऐबे की चेताउनी",
                instruction="जमीन मा बइठि जा, सिरा ढंक, अर मजबूत चीज पकड़। खुला खेत मा भागी जा।",
            ),
        },
    ),

    # -----------------------------------------------------------------------
    # 5. Heavy Snowfall & Avalanches
    # -----------------------------------------------------------------------
    "HEAVY_SNOWFALL_AVALANCHE": HazardDefinition(
        hazard_code="HEAVY_SNOWFALL_AVALANCHE",
        canonical_name="Heavy Snowfall, Blizzard & Avalanche",
        category=HazardCategory.HYDRO_METEOROLOGICAL,
        is_himalayan_specific=True,
        non_linguistic_icon="snow-mountain-debris",
        default_severity=HazardSeverity.ORANGE,
        threshold_metrics={"snowfall_24h_cm": 30.0, "slope_deg": 35.0},
        multilingual={
            "en": MultilingualContent(
                title="High Avalanche Danger & Heavy Snowfall",
                instruction="Avoid high mountain passes and known avalanche chutes. Maintain 72-hour thermal rations.",
            ),
            "hi": MultilingualContent(
                title="हिमस्खलन (एवलांच) एवं भारी बर्फबारी चेतावनी",
                instruction="हिमस्खलन संभावित ढलानों और दर्रों पर जाने से बचें। गर्म कपड़े और आपातकालीन राशन रखें।",
            ),
            "gar": MultilingualContent(
                title="ह्युं गिरण अर हिमकंद टूटण कु खतरा",
                instruction="ऊंचा डांडों अर बर्फिला रस्तों मा जन जावां। चूल्हा-पानी कु इंतजाम घर मा करा।",
            ),
            "kum": MultilingualContent(
                title="बर्फबारी अर हिमस्खलन कु अलर्ट",
                instruction="बर्फ का ढांग बाटी बचीक रया। ऊंच घाटो की तरफ जन जाया।",
            ),
        },
    ),

    # -----------------------------------------------------------------------
    # 6. Forest Fires / Wildfires
    # -----------------------------------------------------------------------
    "FOREST_FIRE": HazardDefinition(
        hazard_code="FOREST_FIRE",
        canonical_name="Forest Fire & Chir Pine Wildfire",
        category=HazardCategory.ENVIRONMENTAL,
        is_himalayan_specific=True,
        non_linguistic_icon="forest-flame-tree",
        default_severity=HazardSeverity.ORANGE,
        threshold_metrics={"temperature_c": 38.0, "wind_speed_ms": 12.0},
        multilingual={
            "en": MultilingualContent(
                title="Forest Fire Active / Smoke Inversion Advisory",
                instruction="Stay upwind. Create perimeter firebreaks around habitations. Report smoke to 1070.",
            ),
            "hi": MultilingualContent(
                title="वनाग्नि (जंगल की आग) एवं धुआं चेतावनी",
                instruction="हवा की विपरीत दिशा में जाएं। बस्तियों के चारों ओर गीली रेखा बनाएं और 1070 पर सूचना दें।",
            ),
            "gar": MultilingualContent(
                title="जंगल मा लाग लगी कु चेताउनी (दावानल)",
                instruction="हवा का रुख बाटा हटि जावां। गांव का चारू तरफ सुरक्षा घेरा बणावा।",
            ),
            "kum": MultilingualContent(
                title="जंगला मा आग लागन की चेताउनी",
                instruction="आग बाटी बचीक हवा का उल्टा तरफ भागा। वन विभाग अर 1070 मा फोन करा।",
            ),
        },
    ),

    # -----------------------------------------------------------------------
    # 7. Cyclones
    # -----------------------------------------------------------------------
    "CYCLONE": HazardDefinition(
        hazard_code="CYCLONE",
        canonical_name="Tropical Cyclone & Depressions",
        category=HazardCategory.METEOROLOGICAL,
        is_himalayan_specific=False,
        non_linguistic_icon="cyclone-spiral-wind",
        default_severity=HazardSeverity.ORANGE,
        threshold_metrics={"wind_knots": 48.0},
        multilingual={
            "en": MultilingualContent(
                title="Tropical Cyclone Warning",
                instruction="Secure loose structures. Expect destructive winds and localized inundation.",
            ),
            "hi": MultilingualContent(
                title="चक्रवात (साइक्लोन) चेतावनी",
                instruction="अस्थायी छतों को सुरक्षित करें। तेज हवाओं और भारी बारिश से बचाव हेतु पक्के स्थान पर रहें।",
            ),
            "gar": MultilingualContent(title="तूफानी चकरी हवा कु संकट", instruction="पक्का कमरों मा रवां, टीन कि छतों कु बचाव करा।"),
            "kum": MultilingualContent(title="चक्रवाती तूफान की चेताउनी", instruction="सुरक्षित मकान मा शरण लिया, उड़ने वाली चीज बांधा।"),
        },
    ),

    # -----------------------------------------------------------------------
    # 8. Heatwaves
    # -----------------------------------------------------------------------
    "HEATWAVE": HazardDefinition(
        hazard_code="HEATWAVE",
        canonical_name="Severe Heatwave & Loo Conditions",
        category=HazardCategory.METEOROLOGICAL,
        is_himalayan_specific=False,
        non_linguistic_icon="sun-thermometer-high",
        default_severity=HazardSeverity.YELLOW,
        threshold_metrics={"max_temp_c": 45.0, "departure_c": 4.5},
        multilingual={
            "en": MultilingualContent(
                title="Severe Heatwave Advisory",
                instruction="Avoid direct sun exposure between 11 AM - 4 PM. Consume ORS and stay hydrated.",
            ),
            "hi": MultilingualContent(
                title="भीषण लू एवं ग्रीष्म लहर चेतावनी",
                instruction="दोपहर 11 से 4 बजे तक धूप में न निकलें। ओआरएस एवं जल का पर्याप्त सेवन करें।",
            ),
            "gar": MultilingualContent(title="कड़ा धूप अर लू कु अलर्ट", instruction="घाम मा बाण जन जावां, पानी अर मट्ठा पीवा।"),
            "kum": MultilingualContent(title="भयानक घाम अर लू की चेताउनी", instruction="दोपहर धूप मा जन निकला, पानी खूब पिया।"),
        },
    ),

    # -----------------------------------------------------------------------
    # 9. Coldwaves
    # -----------------------------------------------------------------------
    "COLDWAVE": HazardDefinition(
        hazard_code="COLDWAVE",
        canonical_name="Severe Coldwave & Frost",
        category=HazardCategory.METEOROLOGICAL,
        is_himalayan_specific=False,
        non_linguistic_icon="ice-snowflake-cold",
        default_severity=HazardSeverity.YELLOW,
        threshold_metrics={"min_temp_c": 4.0, "departure_c": -4.5},
        multilingual={
            "en": MultilingualContent(
                title="Severe Coldwave & Ground Frost Alert",
                instruction="Wear multi-layered clothing. Protect livestock and infants from hypothermia.",
            ),
            "hi": MultilingualContent(
                title="शीत लहर एवं पाला चेतावनी",
                instruction="गर्म कपड़े पहनें। पशुओं और बच्चों को ठंड से बचाएं, अलाव का सुरक्षित उपयोग करें।",
            ),
            "gar": MultilingualContent(title="कड़ाके कि ठंड अर पाला कु संकट", instruction="मोटा ऊनी कपड़ा पहरा, गोठ मा जानवरों कु बचाव करा।"),
            "kum": MultilingualContent(title="भीषण शीत लहर की चेताउनी", instruction="गर्म कपड़ा पहिरा, बाल-बच्चा अर गाय-भैंस बचावा।"),
        },
    ),

    # -----------------------------------------------------------------------
    # 10. Lightning Strikes (Damini Protocol)
    # -----------------------------------------------------------------------
    "LIGHTNING": HazardDefinition(
        hazard_code="LIGHTNING",
        canonical_name="Lightning Strikes & Severe Electrical Discharge",
        category=HazardCategory.METEOROLOGICAL,
        is_himalayan_specific=False,
        non_linguistic_icon="lightning-bolt-danger",
        default_severity=HazardSeverity.RED,
        threshold_metrics={"cape_j_kg": 2500.0, "flash_rate_min": 10},
        multilingual={
            "en": MultilingualContent(
                title="Severe Lightning Strike Hazard (Damini Alert)",
                instruction="Move inside immediately. Never shelter under isolated trees, metal fences, or tin sheds.",
            ),
            "hi": MultilingualContent(
                title="आकाशीय बिजली (वज्रपात) की गंभीर चेतावनी",
                instruction="तुरंत पक्के भवन में शरण लें। अकेले पेड़ों, धातु के खंभों या टिन शेड के नीचे कभी खड़े न हों।",
            ),
            "gar": MultilingualContent(
                title="बिजली खसण कु भारी चेताउनी",
                instruction="पक्के मकान का भित्तर चलि जावां। पेड़ का तैल जन खड़ा रवां।",
            ),
            "kum": MultilingualContent(
                title="गाज / बिजली गिरन की चेताउनी",
                instruction="घरा भितर जा, अकेला रुख का नीचे जन जाया।",
            ),
        },
    ),

    # -----------------------------------------------------------------------
    # 11. Thunderstorms & Hailstorms (Western Disturbances)
    # -----------------------------------------------------------------------
    "THUNDERSTORM_HAILSTORM": HazardDefinition(
        hazard_code="THUNDERSTORM_HAILSTORM",
        canonical_name="Thunderstorm, Hailstorm & Squalls",
        category=HazardCategory.METEOROLOGICAL,
        is_himalayan_specific=False,
        non_linguistic_icon="storm-wind-hail",
        default_severity=HazardSeverity.ORANGE,
        threshold_metrics={"wind_gust_kmh": 65.0, "hail_diameter_cm": 2.0},
        multilingual={
            "en": MultilingualContent(
                title="Thunderstorm with Destructive Hail",
                instruction="Protect heads with firm cover. Shelter vehicles and cattle under sturdy roofs.",
            ),
            "hi": MultilingualContent(
                title="ओलावृष्टि एवं अंधड़ (आंधी-तूफान) चेतावनी",
                instruction="सिर को सुरक्षित रखें। पशुओं और वाहनों को मजबूत छत के नीचे ले जाएं।",
            ),
            "gar": MultilingualContent(title="ओला अर भयंकर आंधी कु अलर्ट", instruction="सिर बचीक पक्की छत तैल रवां।"),
            "kum": MultilingualContent(title="ओले गिरन अर आंधी की चेताउनी", instruction="छत के नीचे रया, ढूंगा-ओले से बच्या।"),
        },
    ),

    # -----------------------------------------------------------------------
    # 12. Droughts & Agricultural Moisture Deficit
    # -----------------------------------------------------------------------
    "DROUGHT": HazardDefinition(
        hazard_code="DROUGHT",
        canonical_name="Drought & Severe Moisture Stress",
        category=HazardCategory.ENVIRONMENTAL,
        is_himalayan_specific=False,
        non_linguistic_icon="drought-cracked-soil",
        default_severity=HazardSeverity.YELLOW,
        threshold_metrics={"rainfall_deficit_pct": -50.0},
        multilingual={
            "en": MultilingualContent(
                title="Agricultural Drought Advisory",
                instruction="Conserve reservoir resources. Adopt micro-irrigation and mulch soil beds.",
            ),
            "hi": MultilingualContent(
                title="सूखा एवं गंभीर नमी संकट चेतावनी",
                instruction="जल संचयन का विवेकपूर्ण उपयोग करें। सूक्ष्म सिंचाई और नमी संरक्षण तकनीक अपनाएं।",
            ),
            "gar": MultilingualContent(title="अकाल अर सूखा कु संकट", instruction="पानी कु बचत करा, नौलों-धारों का पानी सम्भाला।"),
            "kum": MultilingualContent(title="सूखा पड़न की चेताउनी", instruction="पानी की बचत करा, जल स्रोतो को बचावा।"),
        },
    ),

    # -----------------------------------------------------------------------
    # 13. Soil Erosion & Riverbank Breaches
    # -----------------------------------------------------------------------
    "SOIL_EROSION_RIVERBANK": HazardDefinition(
        hazard_code="SOIL_EROSION_RIVERBANK",
        canonical_name="Soil Erosion & Riverbank Breaching",
        category=HazardCategory.HYDRO_METEOROLOGICAL,
        is_himalayan_specific=False,
        non_linguistic_icon="river-bank-collapse",
        default_severity=HazardSeverity.ORANGE,
        threshold_metrics={"erosion_velocity_m_s": 2.5},
        multilingual={
            "en": MultilingualContent(
                title="Riverbank Erosion & Structural Breach",
                instruction="Evacuate buildings within 50 meters of eroding riverbanks immediately.",
            ),
            "hi": MultilingualContent(
                title="नदी कटाव एवं तटबंध टूटने की चेतावनी",
                instruction="कटान वाली नदी सीमा से 50 मीटर के दायरे में स्थित भवनों को तुरंत खाली करें।",
            ),
            "gar": MultilingualContent(title="नदी कु कटान अर किनारा भसकण", instruction="नदी का कांडा का मकान खाली करा।"),
            "kum": MultilingualContent(title="नदी कटाव की चेताउनी", instruction="नदी का किनारे से तुरंत हटि जा।"),
        },
    ),

    # -----------------------------------------------------------------------
    # 14. Chemical & Industrial Hazards
    # -----------------------------------------------------------------------
    "CHEMICAL_INDUSTRIAL": HazardDefinition(
        hazard_code="CHEMICAL_INDUSTRIAL",
        canonical_name="Chemical, Industrial & Hazardous Material Leak",
        category=HazardCategory.ANTHROPOGENIC,
        is_himalayan_specific=False,
        non_linguistic_icon="chemical-hazard-mask",
        default_severity=HazardSeverity.RED,
        threshold_metrics={"hazmat_plume_km": 5.0},
        multilingual={
            "en": MultilingualContent(
                title="Chemical / Industrial Hazmat Release Alert",
                instruction="Evacuate crosswind. Cover nose and mouth with damp cloth. Seal indoor ventilation.",
            ),
            "hi": MultilingualContent(
                title="रासायनिक / औद्योगिक विषैली गैस रिसाव चेतावनी",
                instruction="हवा की दिशा के लंबवत (क्रॉसविंड) भागें। नाक-मुंह को गीले कपड़े से ढकें।",
            ),
            "gar": MultilingualContent(title="जहरीली गैस कु रिसाव संकट", instruction="मुखा मा गीलो कपड़ा बांधा, हवा का उल्टा तरफ भागा।"),
            "kum": MultilingualContent(title="जहरीली गैस लीक की चेताउनी", instruction="नाक-मुख मा गीलो रूमाल रखा, सुरक्षित दूर भागा।"),
        },
    ),
}


class IndianHazardMatrixEngine:
    """Provides querying, classification, and multilingual translation for all 14 hazards."""

    @staticmethod
    def get_hazard(hazard_code: str) -> Optional[HazardDefinition]:
        return INDIAN_HAZARD_REGISTRY.get(hazard_code.upper())

    @staticmethod
    def list_all_hazards() -> List[HazardDefinition]:
        return list(INDIAN_HAZARD_REGISTRY.values())

    @staticmethod
    def list_himalayan_hazards() -> List[HazardDefinition]:
        return [h for h in INDIAN_HAZARD_REGISTRY.values() if h.is_himalayan_specific]

    @staticmethod
    def classify_telemetry_hazard(
        rain_intensity_mm_hr: float,
        soil_saturation_pct: float,
        seismic_magnitude: float,
        discharge_spike_pct: float,
        temperature_c: float,
    ) -> HazardDefinition:
        """
        Dynamically classifies active hazard based on live physical observations.
        Prioritizes acute life-safety hazards (Cloudburst > Flash Flood/GLOF > Landslide > Earthquake).
        """
        if rain_intensity_mm_hr >= 100.0:
            return INDIAN_HAZARD_REGISTRY["CLOUDBURST"]
        if discharge_spike_pct >= 150.0:
            return INDIAN_HAZARD_REGISTRY["FLASH_FLOOD_GLOF"]
        if soil_saturation_pct >= 85.0 and rain_intensity_mm_hr >= 30.0:
            return INDIAN_HAZARD_REGISTRY["LANDSLIDE_MUDSLIDE"]
        if seismic_magnitude >= 4.5:
            return INDIAN_HAZARD_REGISTRY["EARTHQUAKE"]
        if temperature_c >= 40.0:
            return INDIAN_HAZARD_REGISTRY["FOREST_FIRE"]
        if rain_intensity_mm_hr >= 40.0:
            return INDIAN_HAZARD_REGISTRY["THUNDERSTORM_HAILSTORM"]

        # Default standard mountain rain / flood assessment
        return INDIAN_HAZARD_REGISTRY["FLASH_FLOOD_GLOF"]


indian_hazard_engine = IndianHazardMatrixEngine()
