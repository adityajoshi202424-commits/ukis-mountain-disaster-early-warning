'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { DmmcLocale, DMMC_LOCALIZATIONS, LocalizationBundle } from '@/lib/dmmc_localization';
import { CapAlertItem } from '@/types/shared_cap';

interface LanguageContextType {
  locale: DmmcLocale;
  setLocale: (newLocale: DmmcLocale) => void;
  t: LocalizationBundle;
  translateDistrict: (district: string) => string;
  translateAlert: (alert: CapAlertItem) => {
    headline: string;
    instruction: string;
    description: string;
    areaDesc: string;
    severityLabel: string;
  };
  fontSize: 'normal' | 'large' | 'larger';
  setFontSize: (size: 'normal' | 'large' | 'larger') => void;
  highContrast: boolean;
  toggleHighContrast: () => void;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<DmmcLocale>('en-IN');
  const [mounted, setMounted] = useState(false);
  const [fontSize, setFontSizeState] = useState<'normal' | 'large' | 'larger'>('normal');
  const [highContrast, setHighContrastState] = useState(false);

  // Read saved language preference from localStorage on mount
  useEffect(() => {
    setMounted(true);
    const saved = localStorage.getItem('dmmc_selected_locale') as DmmcLocale | null;
    if (saved && DMMC_LOCALIZATIONS[saved]) {
      setLocaleState(saved);
    }
  }, []);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    if (highContrast) {
      document.documentElement.classList.add('contrast-more');
    } else {
      document.documentElement.classList.remove('contrast-more');
    }
  }, [highContrast]);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    if (fontSize === 'large') {
      document.documentElement.style.fontSize = '17px';
    } else if (fontSize === 'larger') {
      document.documentElement.style.fontSize = '18.5px';
    } else {
      document.documentElement.style.fontSize = '';
    }
  }, [fontSize]);

  const toggleHighContrast = () => setHighContrastState((prev) => !prev);
  const setFontSize = (size: 'normal' | 'large' | 'larger') => setFontSizeState(size);

  const setLocale = (newLocale: DmmcLocale) => {
    setLocaleState(newLocale);
    if (typeof window !== 'undefined') {
      localStorage.setItem('dmmc_selected_locale', newLocale);
      // Dispatch custom event so any non-React listeners or parallel components sync
      window.dispatchEvent(new Event('dmmc-locale-changed'));
    }
  };

  const t: LocalizationBundle = DMMC_LOCALIZATIONS[locale] || DMMC_LOCALIZATIONS['en-IN'];

  const translateDistrict = (districtName: string): string => {
    if (!districtName) return '';
    return t.districts[districtName] || districtName;
  };

  const translateAlert = (alert: CapAlertItem) => {
    const anyAlert = alert as any;
    const severity = alert.severity || 'ADVISORY';
    const severityLabel = t.severityLabels[severity] || severity;

    // 1. If explicit localized dictionary exists on alert, use it
    if (alert.localized && alert.localized[locale]) {
      return {
        headline: alert.localized[locale]?.headline || anyAlert.headline || 'Emergency Warning',
        instruction: alert.localized[locale]?.instruction || anyAlert.instruction || '',
        description: alert.localized[locale]?.description || anyAlert.description || '',
        areaDesc: alert.area?.areaDesc || anyAlert.area_desc || '',
        severityLabel,
      };
    }

    // 2. Fallback to Hindi if Garhwali / Kumaoni and Hindi localized exists
    if ((locale === 'gbm-IN' || locale === 'kfy-IN') && alert.localized && alert.localized['hi-IN']) {
      return {
        headline: alert.localized['hi-IN']?.headline || anyAlert.headline || 'Emergency Warning',
        instruction: alert.localized['hi-IN']?.instruction || anyAlert.instruction || '',
        description: alert.localized['hi-IN']?.description || anyAlert.description || '',
        areaDesc: alert.area?.areaDesc || anyAlert.area_desc || '',
        severityLabel,
      };
    }

    // 3. Dynamic real-time translation for standard alerts based on hazard type & headline keywords
    const rawHeadline = anyAlert.headline || '';
    const rawInstruction = anyAlert.instruction || '';
    const rawDesc = anyAlert.description || '';
    const rawArea = alert.area?.areaDesc || anyAlert.area_desc || '';

    if (locale === 'en-IN') {
      return {
        headline: rawHeadline || 'Emergency Alert',
        instruction: rawInstruction || '',
        description: rawDesc || '',
        areaDesc: rawArea,
        severityLabel,
      };
    }

    // Dynamic Hindi Translation
    if (locale === 'hi-IN') {
      let hl = rawHeadline;
      let ins = rawInstruction;
      let desc = rawDesc;

      if (rawHeadline.includes('TORRENTIAL RAINFALL') || rawHeadline.includes('CLOUDBURST')) {
        hl = 'मूसलाधार वर्षा एवं बादल फटने (क्लाउडबर्स्ट) की चेतावनी';
        ins = 'तुरंत निकटतम ऊंचे सुरक्षित स्थान एवं शरण स्थल की ओर जाएं। उफनते गदेरों और नदी तटों से दूर रहें।';
        desc = 'लाइव वर्षा मापी तीव्र वर्षा दर रिपोर्ट कर रहे हैं। पर्वतीय नदी घाटियों में अचानक बाढ़ का अत्यधिक खतरा है।';
      } else if (rawHeadline.includes('GLOF') || rawHeadline.includes('FREEZING LEVEL') || rawHeadline.includes('THERMAL')) {
        hl = 'तीव्र हिमनद पिघलन एवं हिमनद झील विस्फोट (GLOF) सतर्कता';
        ins = 'अलकनंदा एवं धौलीगंगा नदी तटों से तुरंत दूर ऊंचे स्थानों पर जाएं। एसडीआरएफ दल निगरानी कर रहे हैं।';
        desc = '0°C हिमांक स्तर हिमनद मोरेन से ऊपर बना हुआ है। मोरेन पिघलन के कारण नदी डिस्चार्ज में वृद्धि हो रही है।';
      } else if (rawHeadline.includes('SOIL SATURATION') || rawHeadline.includes('SLOPE')) {
        hl = 'मृदा संतृप्ति एवं पहाड़ी ढलान भूस्खलन परामर्श';
        ins = 'पहाड़ी राजमार्गों पर सावधानीपूर्वक यात्रा करें। किसी भी दरार की सूचना तुरंत डीडीएमए 1077 पर दें।';
        desc = 'मृदा नमी सेंसर उच्च संतृप्ति स्तर रिपोर्ट कर रहे हैं। पहाड़ी ढलानों पर भूस्खलन एवं मलबा गिरने का जोखिम है।';
      } else if (rawHeadline.includes('OPERATIONAL TELEMETRY') || rawHeadline.includes('NOMINAL')) {
        hl = 'परिचालन टेलीमेट्री निगरानी: सभी नदी बेसिन सामान्य';
        ins = 'सभी चारधाम यात्रा मार्ग सुचारू हैं। मानक पर्वतीय सुरक्षा दिशानिर्देशों का पालन करें। हेल्पलाइन: 112 / 1070।';
        desc = 'वैज्ञानिक सेंसर सभी 13 जनपदों में सामान्य जल स्तर एवं प्रवाह की पुष्टि करते हैं। कोई आपातकालीन सीमा पार नहीं हुई है।';
      }

      return {
        headline: hl,
        instruction: ins,
        description: desc,
        areaDesc: rawArea,
        severityLabel,
      };
    }

    // Dynamic Garhwali Translation
    if (locale === 'gbm-IN') {
      let hl = rawHeadline;
      let ins = rawInstruction;
      let desc = rawDesc;

      if (rawHeadline.includes('TORRENTIAL RAINFALL') || rawHeadline.includes('CLOUDBURST')) {
        hl = 'मूसलधार बरखा अर गदेरा मा बाढ़ी कु भारी हुकुम';
        ins = 'झटपट उचै डांडा अर सुरक्षित ओट मा जावां। गदेरा अर नदी का किनार जन आवा।';
        desc = 'डांड्युं मा भारी बरखा होणी च। गदेरा मा पानी बदन कु खतरा च।';
      } else if (rawHeadline.includes('GLOF') || rawHeadline.includes('FREEZING LEVEL') || rawHeadline.includes('THERMAL')) {
        hl = 'डांड्युं मा बर्फ पिघलण अर ताल फुटण कु बडू खतरा (GLOF)';
        ins = 'अलकनंदा अर धौलीगंगा का किनार बाटा दूर उचै डांडा मा चड़ि जावां।';
        desc = 'गरमी का कारण डांड्युं की बर्फ पिघलणी च। नदी मा पाणी बदन कु अंदेशा च।';
      } else if (rawHeadline.includes('SOIL SATURATION') || rawHeadline.includes('SLOPE')) {
        hl = 'माटो मा पाणी भरि गे, डांडा खिसकण कु खतरा';
        ins = 'पहाड़ी रस्ता मा धीमे गाड़ी चलावा। कोइ दरार दिखै त 1077 मा फोन करा।';
        desc = 'माटो मा पाणी ज्यादा भरि गे। पहाड़ी ढलान मा पैरो गिरन कु खतरा बदि गे।';
      } else if (rawHeadline.includes('OPERATIONAL TELEMETRY') || rawHeadline.includes('NOMINAL')) {
        hl = 'सीधा प्रसारण पहरेदारी: सब डांडा अर गदेरा शान्त च';
        ins = 'सबै रस्ता खुला चन। चारधाम जात्रा सलाह मान्ना रवां। मदद खातिर 112 लगावां।';
        desc = 'सबै 13 जिलु मा नदी अर डांडा सामान्य चन। २४ घंटा पहरेदारी जारी च।';
      }

      return {
        headline: hl,
        instruction: ins,
        description: desc,
        areaDesc: rawArea,
        severityLabel,
      };
    }

    // Dynamic Kumaoni Translation
    if (locale === 'kfy-IN') {
      let hl = rawHeadline;
      let ins = rawInstruction;
      let desc = rawDesc;

      if (rawHeadline.includes('TORRENTIAL RAINFALL') || rawHeadline.includes('CLOUDBURST')) {
        hl = 'मैल फाटन अर मूसलधार बरखा कु भारी अलर्ट';
        ins = 'झटपट उचै ठांव अर ओट मा भागा। गाड़ किनार बाटी दूर रया।';
        desc = 'डांड मा भारी बरखा हूँणी छ। गाड़ मा बाड़ि आन कु खतरा छ।';
      } else if (rawHeadline.includes('GLOF') || rawHeadline.includes('FREEZING LEVEL') || rawHeadline.includes('THERMAL')) {
        hl = 'डांड मा हिउँ पिघलन अर ताल फुटण कु बड़ो खतरा (GLOF)';
        ins = 'गाड़ किनार बाटी दूर उचै डांड मा जा। सतर्क रया।';
        desc = 'तापमान बदन से डांड मा बर्फ पिघलूं छ। गाड़ मा पाणी बदन कु खतरा छ।';
      } else if (rawHeadline.includes('SOIL SATURATION') || rawHeadline.includes('SLOPE')) {
        hl = 'माटी मा पानी भरन अर डांड खिसकन कु खतरा';
        ins = 'रस्ता मा गाड़ी संभलि के चलावा। दरार दिखन पर 1077 मा खबर करा।';
        desc = 'माटी मा पानी ज्यादा भरि गो। पैरो गिरन कु बड़ो खतरा छ।';
      } else if (rawHeadline.includes('OPERATIONAL TELEMETRY') || rawHeadline.includes('NOMINAL')) {
        hl = 'सीधा प्रसारण निगरानी: सब्बै गाड़ अर डांड शान्त छन';
        ins = 'सब्बै रस्ता खुला छन। चारधाम जात्रा सलाह मानि रया। मदद खातिर 112 लगावा।';
        desc = 'सब्बै 13 जिलु मा गाड़ अर डांड शान्त छन। २४ घंटा निगरानी चालू छ।';
      }

      return {
        headline: hl,
        instruction: ins,
        description: desc,
        areaDesc: rawArea,
        severityLabel,
      };
    }

    return {
      headline: rawHeadline || 'Emergency Alert',
      instruction: rawInstruction || '',
      description: rawDesc || '',
      areaDesc: rawArea,
      severityLabel,
    };
  };

  return (
    <LanguageContext.Provider
      value={{
        locale,
        setLocale,
        t,
        translateDistrict,
        translateAlert,
        fontSize,
        setFontSize,
        highContrast,
        toggleHighContrast,
      }}
    >
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}
