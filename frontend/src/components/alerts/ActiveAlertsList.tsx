'use client';

import React, { useState, useMemo } from 'react';
import { CapAlertItem, AlertSeverity, UttarakhandDistrict, UTTARAKHAND_DISTRICTS } from '@/types/shared_cap';
import { AlertCard } from './AlertCard';
import { NoActiveAlertsState } from './NoActiveAlertsState';
import { Filter, Search, MapPin } from 'lucide-react';
import { useLanguage } from '@/context/LanguageContext';

interface ActiveAlertsListProps {
  alerts: CapAlertItem[];
  onSelectAlert: (alert: CapAlertItem) => void;
  selectedDistrict: UttarakhandDistrict | 'ALL';
  onChangeDistrict: (district: UttarakhandDistrict | 'ALL') => void;
}

export function ActiveAlertsList({
  alerts,
  onSelectAlert,
  selectedDistrict,
  onChangeDistrict,
}: ActiveAlertsListProps) {
  const { locale, t, translateDistrict } = useLanguage();
  const [severityFilter, setSeverityFilter] = useState<'ALL' | AlertSeverity>('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  const filteredAlerts = useMemo(() => {
    return alerts.filter((item) => {
      const anyItem = item as any;
      const itemDistricts: string[] = item.districts || (anyItem.district ? [anyItem.district] : []);
      // 1. District filter
      if (selectedDistrict !== 'ALL' && !itemDistricts.includes(selectedDistrict)) {
        return false;
      }
      // 2. Severity filter
      if (severityFilter !== 'ALL' && item.severity !== severityFilter) {
        return false;
      }
      // 3. Search query
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const headline = (anyItem.headline || item.localized?.['en-IN']?.headline || '').toLowerCase();
        const areaDesc = (item.area?.areaDesc || anyItem.area_desc || '').toLowerCase();
        const riverBasin = (anyItem.river_basin || '').toLowerCase();
        if (!headline.includes(q) && !areaDesc.includes(q) && !riverBasin.includes(q)) {
          return false;
        }
      }
      return true;
    });
  }, [alerts, selectedDistrict, severityFilter, searchQuery]);

  const getSearchPlaceholder = () => {
    if (locale === 'hi-IN') return 'नदी बेसिन या गाँव के नाम से खोजें...';
    if (locale === 'gbm-IN') return 'गाड़ या गांउ का नौं बाटा खोजा...';
    if (locale === 'kfy-IN') return 'गाड़ या गांउ का नौं बाटी खोजा...';
    return 'Search by river basin or village...';
  };

  const getSeverityPillLabel = (sev: 'ALL' | AlertSeverity) => {
    if (sev === 'ALL') {
      if (locale === 'hi-IN') return 'सभी चेतावनियाँ';
      if (locale === 'gbm-IN') return 'सबै चेताउनी';
      if (locale === 'kfy-IN') return 'सब्बै चेताउनी';
      return 'All Alerts';
    }
    if (sev === 'CRITICAL') return locale === 'hi-IN' ? 'गंभीर' : locale === 'gbm-IN' ? 'भारी आफत' : locale === 'kfy-IN' ? 'भारी आफत' : 'Critical';
    if (sev === 'SEVERE') return locale === 'hi-IN' ? 'चेतावनी' : locale === 'gbm-IN' ? 'बडू खतरा' : locale === 'kfy-IN' ? 'बड़ो खतरा' : 'Severe';
    if (sev === 'ADVISORY') return locale === 'hi-IN' ? 'परामर्श' : locale === 'gbm-IN' ? 'पहरेदारी' : locale === 'kfy-IN' ? 'निगरानी' : 'Advisory';
    return sev;
  };

  const getFeedHeaderTitle = () => {
    if (selectedDistrict === 'ALL') {
      if (locale === 'hi-IN') return 'राज्यव्यापी सक्रिय आपदा बुलेटिन';
      if (locale === 'gbm-IN') return 'उत्तराखंड डांडा आफत बुलेटिन';
      if (locale === 'kfy-IN') return 'उत्तराखंड डांड आफत बुलेटिन';
      return 'Statewide Warnings';
    }
    const distName = translateDistrict(selectedDistrict);
    if (locale === 'hi-IN') return `${distName} सक्रिय आपदा चेतावनी`;
    if (locale === 'gbm-IN') return `${distName} आफत चेताउनी`;
    if (locale === 'kfy-IN') return `${distName} आफत चेताउनी`;
    return `${selectedDistrict} Warnings`;
  };

  return (
    <section className="space-y-4">
      {/* Filter Toolbar */}
      <div className="bg-white border border-slate-200 rounded-lg p-3 sm:p-4 shadow-xs space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          {/* District Dropdown */}
          <div className="flex items-center gap-2 flex-1 min-w-[200px]">
            <MapPin className="w-4 h-4 text-slate-500 flex-shrink-0" />
            <select
              value={selectedDistrict}
              onChange={(e) => onChangeDistrict(e.target.value as UttarakhandDistrict | 'ALL')}
              className="w-full bg-slate-50 border border-slate-300 text-slate-900 text-sm font-bold rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-600 focus:outline-none"
              aria-label="Filter alerts by district"
            >
              <option value="ALL">{t.allDistricts || 'All 13 Uttarakhand Districts'}</option>
              {UTTARAKHAND_DISTRICTS.map((d) => (
                <option key={d} value={d}>
                  {translateDistrict(d)}
                </option>
              ))}
            </select>
          </div>

          {/* Search Box */}
          <div className="relative flex-1 min-w-[200px]">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder={getSearchPlaceholder()}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-50 border border-slate-300 text-slate-900 text-sm rounded-md pl-9 pr-3 py-2 focus:ring-2 focus:ring-blue-600 focus:outline-none placeholder:text-slate-400"
            />
          </div>
        </div>

        {/* Severity Filter Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pt-1 scrollbar-none">
          <span className="text-xs font-bold text-slate-500 uppercase mr-1 flex items-center gap-1">
            <Filter className="w-3 h-3" /> {t.filterSeverityLabel || 'Severity:'}
          </span>
          {(['ALL', 'CRITICAL', 'SEVERE', 'ADVISORY'] as const).map((sev) => {
            const isActive = severityFilter === sev;
            return (
              <button
                key={sev}
                onClick={() => setSeverityFilter(sev)}
                className={`px-3 py-1 rounded text-xs font-bold transition-colors whitespace-nowrap ${
                  isActive
                    ? 'bg-slate-900 text-white'
                    : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                }`}
              >
                {getSeverityPillLabel(sev)}
              </button>
            );
          })}
        </div>
      </div>

      {/* Alert Feed Header */}
      <div className="flex items-center justify-between text-xs text-slate-600 px-1">
        <span className="font-bold uppercase tracking-wider">
          {getFeedHeaderTitle()}
        </span>
        <span>
          {locale === 'hi-IN'
            ? `कुल सक्रिय चेतावनियाँ: ${filteredAlerts.length}`
            : locale === 'gbm-IN'
            ? `सक्रिय चेताउनी: ${filteredAlerts.length}`
            : locale === 'kfy-IN'
            ? `सक्रिय चेताउनी: ${filteredAlerts.length}`
            : `Showing ${filteredAlerts.length} active notification${filteredAlerts.length === 1 ? '' : 's'}`}
        </span>
      </div>

      {/* Cards List or Empty State */}
      {filteredAlerts.length === 0 ? (
        <NoActiveAlertsState district={selectedDistrict} />
      ) : (
        <div className="space-y-3">
          {filteredAlerts.map((alert) => (
            <AlertCard key={alert.identifier || (alert as any).id} alert={alert} onSelect={onSelectAlert} />
          ))}
        </div>
      )}
    </section>
  );
}
