'use client';

import React, { useState, useEffect, useCallback } from 'react';
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
import { DmmcLocale } from '@/lib/dmmc_localization';
import { AlertTriangle, RefreshCw, Radio } from 'lucide-react';
import { AiCommanderBot } from '@/components/common/AiCommanderBot';

export default function ActiveAlertsLandingPage() {
  const [alerts, setAlerts] = useState<CapAlertItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedDistrict, setSelectedDistrict] = useState<UttarakhandDistrict | 'ALL'>('ALL');
  const [selectedAlert, setSelectedAlert] = useState<CapAlertItem | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [locale, setLocale] = useState<DmmcLocale>('en-IN');
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
                Uttarakhand Disaster Early Warning &bull; Active Alerts
              </h1>
            </div>
            <p className="text-xs sm:text-sm text-slate-600 max-w-2xl leading-relaxed">
              Official real-time emergency warnings from the Disaster Mitigation &amp; Management Centre (DMMC) and State Emergency Operations Centre (SEOC).
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsZeroDataModalOpen(true)}
              className="flex items-center gap-1.5 text-xs font-bold text-white bg-gradient-to-r from-red-600 to-amber-600 hover:from-red-700 hover:to-amber-700 border border-red-500 px-3 py-2 rounded-md transition-all shadow-sm"
              title="Simulate / Trigger Zero-Data Cell Broadcast for iOS & Android"
            >
              <Radio className="w-3.5 h-3.5 animate-pulse" />
              <span>Zero-Data Broadcast (iOS/Android)</span>
            </button>

            <button
              onClick={fetchAlerts}
              disabled={loading}
              className="flex items-center gap-1.5 text-xs font-bold text-slate-700 bg-slate-100 hover:bg-slate-200 border border-slate-300 px-3 py-2 rounded-md transition-colors shadow-xs"
              title="Refresh latest telemetry feeds"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
              <span>Sync {lastSyncTime}</span>
            </button>
          </div>
        </div>

        {/* Critical Emergency Banner (only appears if critical alerts active) */}
        {hasCriticalAlert && (
          <div className="bg-red-50 border-l-4 border-red-700 p-4 rounded-r-lg shadow-xs flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-red-700 flex-shrink-0 mt-0.5" />
            <div className="space-y-0.5">
              <h2 className="text-sm font-bold text-red-950">
                CRITICAL WARNINGS IN EFFECT
              </h2>
              <p className="text-xs text-red-900 leading-relaxed">
                One or more life-safety flash flood or landslide evacuation orders are active. Follow instructions immediately and avoid mountain riverbeds.
              </p>
            </div>
          </div>
        )}

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
