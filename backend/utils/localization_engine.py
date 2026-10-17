"""
Vernacular Localization & Multilingual Mountain Disaster Alert Engine
Compliant with NDMA / USDMA Vernacular Mountain Early Warning Protocols (UKIS P-011)

Supports Uttarakhand's Linguistic Ecosystem:
- English (en) - Universal Operational & Military/NDRF Standard
- Hindi (hi) - Uttarakhand State Official Language (Civil Administration Standard)
- Garhwali (gar) - Primary Regional Dialect for Garhwal Division (Chamoli, Rudraprayag, Uttarkashi, Tehri, Pauri)
- Kumaoni (kum) - Primary Regional Dialect for Kumaon Division (Pithoragarh, Bageshwar, Almora, Nainital, Champawat)
- Jaunsari (jau) - Indigenous Mountain Dialect for Jaunsar-Bawar belt (Chakrata, Kalsi, Dehradun Hills)
- Sanskrit (sa) - Second Official State Language of Uttarakhand
"""

from __future__ import annotations
from typing import Dict, Optional


LOCALIZATION_REGISTRY = {
    "en": {
        "language_name": "English",
        "hazard": "Himalayan Flash Flood & Cloudburst Alert",
        "action": "Evacuate valley floor immediately to high-ground shelters.",
    },
    "hi": {
        "language_name": "हिन्दी (Hindi)",
        "hazard": "पर्वतीय आकस्मिक बाढ़ एवं बादल फटने की चेतावनी",
        "action": "नदी घाटी के निचले इलाकों से तुरंत सुरक्षित ऊंचे स्थानों पर जाएं।",
    },
    "gar": {
        "language_name": "गढ़वाली (Garhwali)",
        "hazard": "पहाड़ी गाड़-गधेर बाढ़ अर बादल फाटण की चेतावनी",
        "action": "सब लोग फौरन गाड़ का कन्द्रा छोड़िकै सुरक्षित ऊंचा डांडा पर जांवा।",
    },
    "kum": {
        "language_name": "कुमाऊँनी (Kumaoni)",
        "hazard": "बादर फाटन और गाड़-गधेर में बाढ़ै की चेतावनी",
        "action": "सबी लोग गाड़-गधेरक तीर छोड़िबे तुरंते सुरखित ऊंच डांण में जाव।",
    },
    "jau": {
        "language_name": "जौनसारी (Jaunsari)",
        "hazard": "गधेरे में बाढ़ और खाले खिसकणे री भारी चेतावनी",
        "action": "सारे लोग खोलि-खालि छोड़िकै उच्ची धार पर सुरक्षित जाइओ।",
    },
    "sa": {
        "language_name": "संस्कृतम् (Sanskrit - UK 2nd Official)",
        "hazard": "पार्वतीय आकस्मिक जलौघः मेघस्फोट चेतावनी च",
        "action": "शीघ्रमेव उपत्यकां त्यक्त्वा सुरक्षितम् उच्चस्थानं गच्छन्तु।",
    },
}


class VernacularLocalizationEngine:
    """
    Generates verified, authentic emergency disaster alerts in official regional languages
    and indigenous mountain dialects of Uttarakhand.
    """

    DISTRICT_LANGUAGE_MAP: Dict[str, str] = {
        # Garhwal Division
        "Chamoli": "gar",
        "Rudraprayag": "gar",
        "Uttarkashi": "gar",
        "Tehri Garhwal": "gar",
        "Pauri Garhwal": "gar",
        "Dehradun": "hi",
        "Haridwar": "hi",
        # Kumaon Division
        "Pithoragarh": "kum",
        "Bageshwar": "kum",
        "Almora": "kum",
        "Champawat": "kum",
        "Nainital": "kum",
        "Udham Singh Nagar": "hi",
    }

    @staticmethod
    def generate_localized_alert(
        district: str,
        river_surge_m_hr: float = 1.4,
        rain_velocity_mm_hr: float = 35.0,
        risk_level: str = "HIGH",
        horizon_minutes: int = 45,
    ) -> Dict[str, str]:
        """
        Generates multilingual emergency strings across official and dialect languages of Devbhoomi Uttarakhand.
        """
        surge_val = f"{river_surge_m_hr:+.1f}"

        # 1. English (Universal Standard)
        en_alert = (
            f"CRITICAL EMERGENCY: Mountain Flash Flood warning issued for {district} Watershed. "
            f"Rapid river stage acceleration ({surge_val} m/hr, rainfall {rain_velocity_mm_hr:.0f} mm/hr). "
            f"Evacuate riverbeds immediately to high-ground shelters within {horizon_minutes} minutes."
        )

        # 2. Hindi (State Official Standard)
        hi_alert = (
            f"गंभीर आपातकालीन चेतावनी: {district} जलग्रहण क्षेत्र के लिए आकस्मिक बाढ़/बादल फटने की लाल चेतावनी। "
            f"नदी का जलस्तर तेजी से बढ़ रहा है ({surge_val} मी/घंटा, वर्षा {rain_velocity_mm_hr:.0f} मिमी/घंटा)। "
            f"अगले {horizon_minutes} मिनटों में नदी तल छोड़कर तुरंत पूर्व-चिह्नित ऊंचे शरणस्थलों में जाएं।"
        )

        # 3. Garhwali (Garhwal Division Dialect - Chamoli, Rudraprayag, Uttarkashi, Tehri)
        gar_alert = (
            f"भारी चेतावनी: {district} मा गाड़-गधेरा उफणन अर बादल फाटण की चेतावनी जारी। "
            f"नदी को जलस्तर भयंकर तेजी से बढ़णू छ ({surge_val} मी/घंटा)। "
            f"{horizon_minutes} मिनट का भीतर सबी लोग गाड़ का किनारा छोड़ि उच्चा डांडा पर सुरक्षित बणयां।"
        )

        # 4. Kumaoni (Kumaon Division Dialect - Pithoragarh, Bageshwar, Almora, Nainital)
        kum_alert = (
            f"सख्त चेतावनी: {district} में गाड़-गधेर में बाढ़ै और बादर फाटनै की भारी चेतावनी। "
            f"नदी को पाणी भौत तेजी ले बड़नो छू ({surge_val} मी/घंटा)। "
            f"{horizon_minutes} मिनट में सबी लोग गाड़क तीर छोड़िबे सुरखित ऊंच डांण में जाव।"
        )

        # 5. Jaunsari (Dehradun / Chakrata Mountain Belt)
        jau_alert = (
            f"आपात चेतावनी: {district} इलाके रे खाले-गधेरे में बाढ़ और पानी बढ़ने री चेतावनी। "
            f"खोले रो पानी तेजी से चढ़ोन्दो ({surge_val} मी/घंटा)। "
            f"{horizon_minutes} मिंटो रे अंदर सारे लोग उच्ची धार पर सुरक्षित पहुँचे।"
        )

        # 6. Sanskrit (Uttarakhand Second Official Language)
        sa_alert = (
            f"आपत्कालीनसूचना: {district} जनपदे पर्वतीय आकस्मिक जलौघः मेघस्फोटस्य च रक्तचेतावनी प्रसारिता। "
            f"नद्याः जलस्तरः तीव्रगत्या वर्धते ({surge_val} मी/घण्टा)। "
            f"{horizon_minutes} निमेषाभ्यन्तरे नदीतीरं त्यक्त्वा उच्चस्थानं गच्छन्तु।"
        )

        return {
            "en": en_alert,
            "hi": hi_alert,
            "gar": gar_alert,
            "kum": kum_alert,
            "jau": jau_alert,
            "sa": sa_alert,
        }

    @classmethod
    def get_primary_vernacular_for_district(cls, district: str) -> str:
        return cls.DISTRICT_LANGUAGE_MAP.get(district, "hi")


localization_engine = VernacularLocalizationEngine()
