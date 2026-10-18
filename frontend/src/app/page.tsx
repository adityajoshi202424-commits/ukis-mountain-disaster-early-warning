'use client';

import React, { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { TopNav } from '@/components/nav/TopNav';
import { CitizenDrawer } from '@/components/nav/CitizenDrawer';
import { ActiveAlertsList } from '@/components/alerts/ActiveAlertsList';
import { CapDetailModal } from '@/components/alerts/CapDetailModal';
import { SosFab } from '@/components/alerts/SosFab';
import { GovFooter } from '@/components/layout/GovFooter';
import { MarkSafeModal } from '@/components/citizen/MarkSafeModal';
import { ReportHazardModal } from '@/components/citizen/ReportHazardModal';
import { FamilyCheckInModal } from '@/components/citizen/FamilyCheckInModal';
import { ZeroDataAlertModal } from '@/components/common/ZeroDataAlertModal';
import { CapAlertItem, UttarakhandDistrict } from '@/types/shared_cap';
import { AlertTriangle, RefreshCw, Radio, ChevronRight, Activity } from 'lucide-react';
import { AiCommanderBot } from '@/components/common/AiCommanderBot';
import { useLanguage } from '@/context/LanguageContext';

export default function ActiveAlertsLandingPage() {
  const { locale, setLocale, t } = useLanguage();
  const [alerts, setAlerts] = useState<CapAlertItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedDistrict, setSelectedDistrict] = useState<UttarakhandDistrict | 'ALL'>('ALL');
  const [selectedAlert, setSelectedAlert] = useState<CapAlertItem | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [isMarkSafeOpen, setIsMarkSafeOpen] = useState(false);
  const [isReportHazardOpen, setIsReportHazardOpen] = useState(false);
  const [isFamilyLookupOpen, setIsFamilyLookupOpen] = useState(false);
  const [isZeroDataModalOpen, setIsZeroDataModalOpen] = useState(false);
  const [lowBandwidth, setLowBandwidth] = useState(false);
  const [lastSyncTime, setLastSyncTime] = useState<string>('Checking...');

  const fetchAlerts = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/v1/alerts/feed', { cache: 'no-store' });
      if (res.ok) {
        const data = await res.json();
        const activeItems: CapAlertItem[] = data.alerts || data.active_alerts || [];
        setAlerts(activeItems);
        if (typeof window !== 'undefined') {
          localStorage.setItem('dmmc_cached_alerts', JSON.stringify(activeItems));
        }
      } else {
        throw new Error(`Feed response status: ${res.status}`);
      }
    } catch (err) {
      console.warn('Live alert feed unavailable (fail-closed). Checking local cache.');
      if (typeof window !== 'undefined') {
        const cached = localStorage.getItem('dmmc_cached_alerts');
        if (cached) {
          try {
            setAlerts(JSON.parse(cached));
          } catch {
            setAlerts([]);
          }
        }
      }
    } finally {
      setLoading(false);
      setLastSyncTime(
        new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      );
    }
  }, []);

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 30000); // 30s auto-refresh
    return () => clearInterval(interval);
  }, [fetchAlerts]);

  const hasCriticalAlert = alerts.some((a) => a.severity === 'CRITICAL');

  const getPageTitle = () => {
    if (locale === 'hi-IN') return 'उत्तराखंड आपदा प्रारंभिक चेतावनी • सक्रिय चेतावनियाँ';
    if (locale === 'gbm-IN') return 'उत्तराखंड आफत की पैली चेताउनी • सक्रिय चेतावनियाँ';
    if (locale === 'kfy-IN') return 'उत्तराखंड आफत की पैली चेताउनी • सक्रिय चेताउनियां';
    return 'Uttarakhand Disaster Early Warning • Active Alerts';
  };

  const getPageSubtitle = () => {
    if (locale === 'hi-IN') return 'आपदा न्यूनीकरण एवं प्रबंधन केंद्र (DMMC) एवं राज्य आपातकालीन परिचालन केंद्र (SEOC) की आधिकारिक चेतावनियाँ।';
    if (locale === 'gbm-IN') return 'DMMC अर SEOC देहरादून बाटा सीधा आधिकारिक आफत चेताउनी। 24 घंटा सीधी पहरेदारी।';
    if (locale === 'kfy-IN') return 'DMMC अर SEOC बाटी सीधा आधिकारिक आफत चेताउनी। 24 घंटा सीधी निगरानी।';
    return 'Official real-time emergency warnings from the Disaster Mitigation & Management Centre (DMMC) and State Emergency Operations Centre (SEOC).';
  };

  const getZeroDataBtnLabel = () => {
    if (locale === 'hi-IN') return 'शून्य-डेटा प्रसारण (iOS/Android)';
    if (locale === 'gbm-IN') return 'बिना इंटरनेट प्रसारण (iOS/Android)';
    if (locale === 'kfy-IN') return 'बिना डेटा प्रसारण (iOS/Android)';
    return 'Zero-Data Broadcast (iOS/Android)';
  };

  const getCriticalBannerText = () => {
    if (locale === 'hi-IN') {
      return {
        title: 'गंभीर आपातकालीन चेतावनी सक्रिय है',
        desc: 'एक या अधिक जीवन-सुरक्षा आकस्मिक बाढ़ अथवा भूस्खलन निकासी आदेश प्रभावी हैं। तुरंत निर्देशों का पालन करें और नदी तटों से दूर रहें।',
      };
    }
    if (locale === 'gbm-IN') {
      return {
        title: 'भारी आफत कु अलर्ट जारी च',
        desc: 'एक या ज्यादा भारी आफत या बाढ़ी कु हुकुम जारी च। तुरंत हुकुम माना अर गदेरा का किनार जन जावा।',
      };
    }
    if (locale === 'kfy-IN') {
      return {
        title: 'भारी आफत कु अलर्ट जारी छ',
        desc: 'एक या जादा भारी आफत या बाड़ि कु हुकुम जारी छ। झटपट हुकुम माना अर गाड़ किनार जन जाया।',
      };
    }
    return {
      title: 'CRITICAL WARNINGS IN EFFECT',
      desc: 'One or more life-safety flash flood or landslide evacuation orders are active. Follow instructions immediately and avoid mountain riverbeds.',
    };
  };

  const criticalContent = getCriticalBannerText();

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900 font-sans">
      <TopNav
        onOpenDrawer={() => setDrawerOpen(true)}
        hasActiveAlerts={hasCriticalAlert}
      />

      <main className="flex-1 max-w-5xl mx-auto w-full px-4 sm:px-6 py-6 sm:py-8 space-y-6">
        {/* Official Headline Banner */}
        <div className="bg-white border border-slate-200 rounded-lg p-5 sm:p-6 shadow-xs flex flex-wrap items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-600 animate-pulse" />
              <h1 className="text-xl sm:text-2xl font-extrabold text-slate-900 tracking-tight">
                {getPageTitle()}
              </h1>
            </div>
            <p className="text-xs sm:text-sm text-slate-600 max-w-2xl leading-relaxed">
              {getPageSubtitle()}
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsZeroDataModalOpen(true)}
              className="flex items-center gap-1.5 text-xs font-bold text-white bg-gradient-to-r from-red-600 to-amber-600 hover:from-red-700 hover:to-amber-700 border border-red-500 px-3 py-2 rounded-md transition-all shadow-sm"
              title="Simulate / Trigger Zero-Data Cell Broadcast for iOS & Android"
            >
              <Radio className="w-3.5 h-3.5 animate-pulse" />
              <span>{getZeroDataBtnLabel()}</span>
            </button>

            <button
              onClick={fetchAlerts}
              disabled={loading}
              className="flex items-center gap-1.5 text-xs font-bold text-slate-700 bg-slate-100 hover:bg-slate-200 border border-slate-300 px-3 py-2 rounded-md transition-colors shadow-xs"
              title="Refresh latest telemetry feeds"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
              <span>{locale === 'hi-IN' ? 'सिंक' : locale === 'gbm-IN' ? 'सिंक करा' : locale === 'kfy-IN' ? 'सिंक करा' : 'Sync'} {lastSyncTime}</span>
            </button>
          </div>
        </div>

        {/* Critical Emergency Banner (only appears if critical alerts active) */}
        {hasCriticalAlert && (
          <div className="bg-red-50 border-l-4 border-red-700 p-4 rounded-r-lg shadow-xs flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-red-700 flex-shrink-0 mt-0.5" />
            <div className="space-y-0.5">
              <h2 className="text-sm font-bold text-red-950">
                {criticalContent.title}
              </h2>
              <p className="text-xs text-red-900 leading-relaxed">
                {criticalContent.desc}
              </p>
            </div>
          </div>
        )}

        {/* UKIS Flagship Showcase Banner: HIM-KAVACH (Devbhoomi-DRISHTI) */}
        <div className="relative overflow-hidden rounded-xl border border-indigo-200 bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 p-5 text-white shadow-md">
          <div className="absolute top-0 right-0 -mt-4 -mr-4 w-44 h-44 rounded-full bg-indigo-500/10 blur-2xl pointer-events-none" />
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 relative z-10">
            <div className="space-y-1.5">
              <div className="flex flex-wrap items-center gap-2">
                <span className="inline-flex items-center gap-1 rounded bg-indigo-500/20 px-2 py-0.5 text-[11px] font-bold text-indigo-300 border border-indigo-400/30">
                  <Activity className="w-3.5 h-3.5 text-indigo-400 animate-pulse" />
                  UKIS 2026 FLAGSHIP ENTRY • ITDA & USDMA
                </span>
                <span className="rounded bg-emerald-500/20 px-2 py-0.5 text-[10px] font-bold text-emerald-300 border border-emerald-500/30">
                  EXPLAINABLE AI (XAI)
                </span>
                <span className="rounded bg-amber-500/20 px-2 py-0.5 text-[10px] font-bold text-amber-300 border border-amber-500/30">
                  CASCADING GLOF SIMULATOR
                </span>
              </div>
              <h2 className="text-lg sm:text-xl font-extrabold tracking-tight text-white flex items-center gap-2">
                <span>HIM-KAVACH</span>
                <span className="text-xs font-semibold text-indigo-200 px-2 py-0.5 rounded bg-indigo-900/60 border border-indigo-700/50">
                  Devbhoomi-DRISHTI
                </span>
              </h2>
              <p className="text-xs sm:text-sm text-slate-300 max-w-2xl leading-relaxed">
                Explainable Geospatial Multi-Hazard Early-Warning & Cascading-Risk Intelligence for Uttarakhand&apos;s fragile topography. Solves the &ldquo;Black-Box Trust Deficit&rdquo; with TreeSHAP attributions, Vasundhara Tal GLOF wave routing (T+0 to T+180m), Joshimath/Sirobagad landslide triggers, and automated DEOC Char Dham halting SOPs.
              </p>
            </div>
            <div className="flex-shrink-0">
              <Link
                href="/him-kavach"
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs sm:text-sm transition-all shadow-md hover:shadow-indigo-500/25 border border-indigo-400"
              >
                <span>Launch HIM-KAVACH Platform</span>
                <ChevronRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </div>

        {/* weather.gov Active Alerts Feed List */}
        <ActiveAlertsList
          alerts={alerts}
          onSelectAlert={(alert) => setSelectedAlert(alert)}
          selectedDistrict={selectedDistrict}
          onChangeDistrict={setSelectedDistrict}
        />
      </main>

      {/* CAP 1.2 Detail Dialog */}
      <CapDetailModal
        alert={selectedAlert}
        onClose={() => setSelectedAlert(null)}
      />

      {/* Slide-out Drawer for Language & Secondary Citizen Services */}
      <CitizenDrawer
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        currentLocale={locale}
        onSelectLocale={setLocale}
        onOpenMarkSafe={() => setIsMarkSafeOpen(true)}
        onOpenReportHazard={() => setIsReportHazardOpen(true)}
        onOpenFamilyLookup={() => setIsFamilyLookupOpen(true)}
        lowBandwidth={lowBandwidth}
        onToggleLowBandwidth={() => setLowBandwidth(!lowBandwidth)}
        lastSyncTime={lastSyncTime}
      />

      {/* Citizen Safety Action Modals */}
      <MarkSafeModal
        isOpen={isMarkSafeOpen}
        onClose={() => setIsMarkSafeOpen(false)}
      />
      <ReportHazardModal
        isOpen={isReportHazardOpen}
        onClose={() => setIsReportHazardOpen(false)}
      />
      <FamilyCheckInModal
        isOpen={isFamilyLookupOpen}
        onClose={() => setIsFamilyLookupOpen(false)}
      />

      {/* Universal Floating SOS Speed Dial */}
      <SosFab />

      {/* Zero-Data & Power-Loss Cell Broadcast Simulator */}
      <ZeroDataAlertModal
        isOpen={isZeroDataModalOpen}
        onClose={() => setIsZeroDataModalOpen(false)}
        district={selectedDistrict === 'ALL' ? 'Chamoli' : selectedDistrict}
        locale={locale}
      />

      {/* Interactive AI Mountain Disaster Commander Assistant Bot */}
      <AiCommanderBot />

      {/* Government Footer */}
      <GovFooter />
    </div>
  );
}
