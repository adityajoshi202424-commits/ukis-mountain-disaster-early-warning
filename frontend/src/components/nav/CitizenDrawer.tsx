'use client';

import React from 'react';
import Link from 'next/link';
import { 
  X, 
  Globe, 
  ShieldCheck, 
  Users, 
  AlertCircle, 
  Wifi, 
  WifiOff, 
  PhoneCall, 
  CheckCircle2, 
  Check,
  Shield,
  ChevronRight
} from 'lucide-react';
import { DmmcLocale, DMMC_LOCALIZATIONS } from '@/lib/dmmc_localization';

interface CitizenDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  currentLocale: DmmcLocale;
  onSelectLocale: (locale: DmmcLocale) => void;
  onOpenMarkSafe: () => void;
  onOpenReportHazard: () => void;
  onOpenFamilyLookup: () => void;
  lowBandwidth: boolean;
  onToggleLowBandwidth: () => void;
  lastSyncTime?: string;
}

export function CitizenDrawer({
  isOpen,
  onClose,
  currentLocale,
  onSelectLocale,
  onOpenMarkSafe,
  onOpenReportHazard,
  onOpenFamilyLookup,
  lowBandwidth,
  onToggleLowBandwidth,
  lastSyncTime,
}: CitizenDrawerProps) {
  if (!isOpen) return null;

  const t = DMMC_LOCALIZATIONS[currentLocale] || DMMC_LOCALIZATIONS['en-IN'];

  const languages: { code: DmmcLocale; label: string; native: string; desc: string }[] = [
    { code: 'en-IN', label: 'English', native: 'English', desc: 'Default Interface' },
    { code: 'hi-IN', label: 'Hindi', native: 'हिन्दी', desc: 'आधिकारिक राजभाषा' },
    { code: 'gbm-IN', label: 'Garhwali', native: 'गढ़वाली', desc: 'पहाड़ी बोली (गढ़वाळ)' },
    { code: 'kfy-IN', label: 'Kumaoni', native: 'कुमाऊँनी', desc: 'पहाड़ी बोली (कुमाऊं)' },
  ];

  const handleLanguageChange = (code: DmmcLocale) => {
    onSelectLocale(code);
    if (typeof window !== 'undefined') {
      localStorage.setItem('dmmc_selected_locale', code);
      window.dispatchEvent(new Event('dmmc-locale-changed'));
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs transition-opacity"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Drawer Panel */}
      <div className="relative w-full max-w-sm bg-white h-full shadow-2xl flex flex-col z-10 border-l border-slate-200">
        {/* Drawer Header */}
        <div className="p-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
          <div>
            <h2 className="text-sm font-bold text-slate-900">
              {currentLocale === 'hi-IN'
                ? 'नागरिक सेवाएँ एवं सेटिंग्स'
                : currentLocale === 'gbm-IN'
                ? 'नागरिक सेवा अर व्यवस्था'
                : currentLocale === 'kfy-IN'
                ? 'नागरिक सेवा अर खाता'
                : 'Citizen Services & Tools'}
            </h2>
            <p className="text-xs text-slate-500">
              {currentLocale === 'hi-IN'
                ? 'DMMC उत्तराखंड आपदा पोर्टल'
                : currentLocale === 'gbm-IN'
                ? 'DMMC उत्तराखंड आफत पोर्टल'
                : currentLocale === 'kfy-IN'
                ? 'DMMC उत्तराखंड आफत पोर्टल'
                : 'DMMC Uttarakhand Disaster Portal'}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-500 hover:text-slate-900 rounded-md hover:bg-slate-200 transition-colors"
            aria-label="Close menu"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Drawer Scrollable Content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-6 text-sm">
          {/* 1. Language Switcher */}
          <div>
            <label className="flex items-center justify-between font-bold text-xs text-slate-700 uppercase tracking-wider mb-2.5">
              <span className="flex items-center gap-1.5">
                <Globe className="w-4 h-4 text-blue-700" />
                <span>
                  {currentLocale === 'hi-IN'
                    ? 'भाषा चयन / Language'
                    : currentLocale === 'gbm-IN'
                    ? 'भाषा छांटा / Language'
                    : currentLocale === 'kfy-IN'
                    ? 'भाषा छांटा / Language'
                    : 'Language / भाषा'}
                </span>
              </span>
              <span className="text-[10px] font-mono text-blue-700 font-bold bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
                {currentLocale.toUpperCase()}
              </span>
            </label>

            <div className="grid grid-cols-2 gap-2">
              {languages.map((lang) => {
                const isSelected = currentLocale === lang.code;
                return (
                  <button
                    key={lang.code}
                    onClick={() => handleLanguageChange(lang.code)}
                    className={`p-3 rounded-lg border text-left transition-all relative ${
                      isSelected
                        ? 'bg-blue-600 text-white border-blue-700 shadow-md ring-2 ring-blue-300'
                        : 'bg-slate-50 border-slate-200 hover:bg-slate-100 text-slate-800'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className={`block font-extrabold text-sm ${isSelected ? 'text-white' : 'text-slate-900'}`}>
                        {lang.native}
                      </span>
                      {isSelected && <Check className="w-4 h-4 text-white" />}
                    </div>
                    <span className={`block text-[11px] font-semibold mt-0.5 ${isSelected ? 'text-blue-100' : 'text-slate-600'}`}>
                      {lang.label}
                    </span>
                    <span className={`block text-[9px] mt-1 ${isSelected ? 'text-blue-200' : 'text-slate-400'}`}>
                      {lang.desc}
                    </span>
                  </button>
                );
              })}
            </div>

            <p className="text-[11px] text-slate-500 mt-2 font-sans italic">
              {currentLocale === 'hi-IN'
                ? '✓ भाषा परिवर्तित हो चुकी है। सभी अलर्ट और पेज हिंदी में अपडेट हो गए हैं।'
                : currentLocale === 'gbm-IN'
                ? '✓ गढ़वाली भाषा चुणी गे। सबै अलर्ट अर रस्ता गढ़वाली मा अपडेट ह्वे ग्येन।'
                : currentLocale === 'kfy-IN'
                ? '✓ कुमाऊँनी भाषा चुणी गो। सब्बै अलर्ट अर रस्ता कुमाऊँनी मा अपडेट भई गैन।'
                : '✓ UI language active: English.'}
            </p>
          </div>

          <hr className="border-slate-100" />

          {/* 2. Citizen Safety Actions */}
          <div className="space-y-2">
            <label className="font-bold text-xs text-slate-700 uppercase tracking-wider block mb-2">
              {currentLocale === 'hi-IN'
                ? 'जन सुरक्षा त्वरित कार्य'
                : currentLocale === 'gbm-IN'
                ? 'जन सुरक्षा बचाव कार्य'
                : currentLocale === 'kfy-IN'
                ? 'जन सुरक्षा बचाव कार्य'
                : 'Public Safety Actions'}
            </label>

            <button
              onClick={() => { onClose(); onOpenMarkSafe(); }}
              className="w-full flex items-center gap-3 p-3 bg-emerald-50 hover:bg-emerald-100 border border-emerald-300 rounded-lg text-emerald-900 font-bold text-left transition-colors shadow-xs"
            >
              <ShieldCheck className="w-5 h-5 text-emerald-700 flex-shrink-0" />
              <div>
                <span className="block text-xs sm:text-sm">
                  {currentLocale === 'hi-IN'
                    ? 'स्वयं को सुरक्षित चिह्नित करें'
                    : currentLocale === 'gbm-IN'
                    ? 'अपणी कुशलता कु संदेश भेजा'
                    : currentLocale === 'kfy-IN'
                    ? 'अपणी कुशलता कु संदेश भेजा'
                    : 'Mark Yourself Safe'}
                </span>
                <span className="block text-[11px] text-emerald-700 font-normal">
                  {currentLocale === 'hi-IN'
                    ? 'परिवार के नंबरों पर तत्काल सूचना भेजें'
                    : currentLocale === 'gbm-IN'
                    ? 'घर का फोन नंबर मा संदेश भेजा'
                    : currentLocale === 'kfy-IN'
                    ? 'घर का फोन नंबर मा संदेश भेजा'
                    : 'Notify linked family numbers'}
                </span>
              </div>
            </button>

            <button
              onClick={() => { onClose(); onOpenFamilyLookup(); }}
              className="w-full flex items-center gap-3 p-3 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg text-blue-900 font-bold text-left transition-colors"
            >
              <Users className="w-5 h-5 text-blue-700 flex-shrink-0" />
              <div>
                <span className="block text-xs sm:text-sm">
                  {currentLocale === 'hi-IN'
                    ? 'परिजनों की सुरक्षा स्थिति जांचें'
                    : currentLocale === 'gbm-IN'
                    ? 'अपन्युं की सुरक्षा पता करा'
                    : currentLocale === 'kfy-IN'
                    ? 'अपन्युं की सुरक्षा पता करा'
                    : "Check Loved Ones' Safety"}
                </span>
                <span className="block text-[11px] text-blue-700 font-normal">
                  {currentLocale === 'hi-IN'
                    ? 'मोबाइल नंबर से चेक-इन स्थिति देखें'
                    : currentLocale === 'gbm-IN'
                    ? 'फोन नंबर बाटा पता करा'
                    : currentLocale === 'kfy-IN'
                    ? 'फोन नंबर बाटी पता करा'
                    : 'Lookup check-in status by phone'}
                </span>
              </div>
            </button>

            <button
              onClick={() => { onClose(); onOpenReportHazard(); }}
              className="w-full flex items-center gap-3 p-3 bg-amber-50 hover:bg-amber-100 border border-amber-300 rounded-lg text-amber-900 font-bold text-left transition-colors"
            >
              <AlertCircle className="w-5 h-5 text-amber-700 flex-shrink-0" />
              <div>
                <span className="block text-xs sm:text-sm">
                  {currentLocale === 'hi-IN'
                    ? 'पर्वतीय आपदा की रिपोर्ट करें'
                    : currentLocale === 'gbm-IN'
                    ? 'बाढ़ी या पैरो की खबर करा'
                    : currentLocale === 'kfy-IN'
                    ? 'बाड़ि या पैरो की खबर करा'
                    : 'Report Mountain Hazard'}
                </span>
                <span className="block text-[11px] text-amber-800 font-normal">
                  {currentLocale === 'hi-IN'
                    ? 'सड़क रुकावट या भूस्खलन जियोटैग करें'
                    : currentLocale === 'gbm-IN'
                    ? 'रस्ता रुकावट या पैरो फोटो भेजा'
                    : currentLocale === 'kfy-IN'
                    ? 'रस्ता रुकावट या पैरो फोटो भेजा'
                    : 'Geotag road blockages or slides'}
                </span>
              </div>
            </button>
          </div>

          <hr className="border-slate-100" />

          {/* 3. Connectivity & Low-Bandwidth Mode */}
          <div>
            <label className="font-bold text-xs text-slate-700 uppercase tracking-wider block mb-2">
              {currentLocale === 'hi-IN'
                ? 'कनेक्टिविटी एवं डेटा मोड'
                : currentLocale === 'gbm-IN'
                ? 'नेटवर्क अर डेटा मोड'
                : currentLocale === 'kfy-IN'
                ? 'नेटवर्क अर डेटा मोड'
                : 'Connectivity Mode'}
            </label>
            <div className="flex items-center justify-between p-3 bg-slate-50 border border-slate-200 rounded-lg">
              <div className="flex items-center gap-2">
                {lowBandwidth ? (
                  <WifiOff className="w-4 h-4 text-amber-700" />
                ) : (
                  <Wifi className="w-4 h-4 text-emerald-700" />
                )}
                <div>
                  <span className="block text-xs font-bold text-slate-900">
                    {lowBandwidth ? 'कम बैंडविड्थ (टेक्स्ट केवल)' : 'सामान्य 4G/5G डेटा मोड'}
                  </span>
                  <span className="block text-[10px] text-slate-500">
                    {lowBandwidth ? 'मानचित्र टाइल्स अक्षम (बैटरी बचत)' : 'पूर्ण जीआईएस मानचित्र सक्षम'}
                  </span>
                </div>
              </div>
              <button
                onClick={onToggleLowBandwidth}
                className={`text-xs font-bold px-2.5 py-1 rounded border transition-colors ${
                  lowBandwidth 
                    ? 'bg-amber-100 border-amber-300 text-amber-900' 
                    : 'bg-white border-slate-300 text-slate-700 hover:bg-slate-100'
                }`}
              >
                {lowBandwidth ? 'सक्रिय' : 'बदलें'}
              </button>
            </div>
          </div>

          <hr className="border-slate-100" />

          {/* 4. Emergency Contacts Hotlines */}
          <div>
            <label className="font-bold text-xs text-slate-700 uppercase tracking-wider block mb-2">
              {t.emergencyHotlinesLabel}
            </label>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <a 
                href="tel:112"
                className="flex items-center gap-2 p-2.5 bg-red-50 hover:bg-red-100 border border-red-200 text-red-900 font-bold rounded-lg transition-colors"
              >
                <PhoneCall className="w-4 h-4 text-red-700" />
                <div>
                  <span className="block font-mono text-sm leading-none">112</span>
                  <span className="block text-[10px] text-red-700 font-normal">राष्ट्रीय आपातकाल</span>
                </div>
              </a>

              <a 
                href="tel:1070"
                className="flex items-center gap-2 p-2.5 bg-slate-100 hover:bg-slate-200 border border-slate-200 text-slate-900 font-bold rounded-lg transition-colors"
              >
                <PhoneCall className="w-4 h-4 text-slate-700" />
                <div>
                  <span className="block font-mono text-sm leading-none">1070</span>
                  <span className="block text-[10px] text-slate-600 font-normal">राज्य SEOC</span>
                </div>
              </a>
            </div>
          </div>

          <hr className="border-slate-100" />

          {/* 5. DMMC Administrative Operations Portal */}
          <div>
            <label className="font-bold text-xs text-slate-700 uppercase tracking-wider block mb-2">
              {currentLocale === 'hi-IN'
                ? 'अधिकारी एवं आपदा नियंत्रण कक्ष'
                : currentLocale === 'gbm-IN'
                ? 'अधिकारी अर आपदा नियंत्रण कक्ष'
                : currentLocale === 'kfy-IN'
                ? 'अधिकारी अर आपदा नियंत्रण कक्ष'
                : 'Official Command & Control'}
            </label>
            <Link
              href="/admin"
              onClick={onClose}
              className="flex items-center justify-between p-3 bg-red-50 hover:bg-red-100 border border-red-200 text-red-900 rounded-lg transition-colors group"
            >
              <div className="flex items-center gap-2.5">
                <Shield className="w-4 h-4 text-red-700" />
                <div>
                  <span className="block text-xs font-bold text-red-950">
                    {currentLocale === 'hi-IN'
                      ? 'DMMC राज्य आपदा संचालन केंद्र (Admin)'
                      : 'DMMC State Operations Center (Admin)'}
                  </span>
                  <span className="block text-[10px] text-red-700">
                    {currentLocale === 'hi-IN'
                      ? 'आपातकालीन अलर्ट जारी करें, सायरन व कॉल नियंत्रण'
                      : 'Manual CAP issuance, siren tests & phone calls'}
                  </span>
                </div>
              </div>
              <ChevronRight className="w-4 h-4 text-red-600 group-hover:translate-x-0.5 transition-transform" />
            </Link>
          </div>
        </div>

        {/* Drawer Footer */}
        <div className="p-3 border-t border-slate-200 bg-slate-50 flex items-center justify-between text-[11px] text-slate-500 font-mono">
          <span>सिंक: {lastSyncTime || '30s'}</span>
          <span className="text-emerald-700 font-bold flex items-center gap-1">
            <CheckCircle2 className="w-3.5 h-3.5" />
            USDMA DEVBHOOMI
          </span>
        </div>
      </div>
    </div>
  );
}
