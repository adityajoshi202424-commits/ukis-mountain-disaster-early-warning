'use client';

import React from 'react';
import { 
  AlertOctagon, 
  AlertTriangle, 
  Info, 
  MapPin, 
  Clock, 
  ChevronRight, 
  ShieldAlert,
  Waves,
  Mountain,
  Flame,
  Snowflake
} from 'lucide-react';
import { CapAlertItem, AlertSeverity, HimalayanHazardType } from '@/types/shared_cap';
import { useLanguage } from '@/context/LanguageContext';

interface AlertCardProps {
  alert: CapAlertItem;
  onSelect: (alert: CapAlertItem) => void;
}

const SEVERITY_CONFIG: Record<
  string,
  {
    badgeBg: string;
    badgeText: string;
    borderLeft: string;
    icon: React.ElementType;
    labelKey: 'CRITICAL' | 'SEVERE' | 'ADVISORY' | 'NORMAL';
  }
> = {
  CRITICAL: {
    badgeBg: 'bg-red-700',
    badgeText: 'text-white',
    borderLeft: 'border-l-red-700',
    icon: AlertOctagon,
    labelKey: 'CRITICAL',
  },
  SEVERE: {
    badgeBg: 'bg-amber-700',
    badgeText: 'text-white',
    borderLeft: 'border-l-amber-700',
    icon: AlertTriangle,
    labelKey: 'SEVERE',
  },
  ADVISORY: {
    badgeBg: 'bg-amber-800',
    badgeText: 'text-white',
    borderLeft: 'border-l-amber-800',
    icon: Info,
    labelKey: 'ADVISORY',
  },
  NORMAL: {
    badgeBg: 'bg-emerald-700',
    badgeText: 'text-white',
    borderLeft: 'border-l-emerald-700',
    icon: Info,
    labelKey: 'NORMAL',
  },
};

const HAZARD_ICONS: Record<string, React.ElementType> = {
  FLASH_FLOOD: Waves,
  LANDSLIDE: Mountain,
  CLOUDBURST: Waves,
  GLOF: Waves,
  AVALANCHE: Snowflake,
  DAM_BREACH: Waves,
  FOREST_FIRE: Flame,
  RIVER_SURGE: Waves,
  EARTHQUAKE: Mountain,
};

export function AlertCard({ alert, onSelect }: AlertCardProps) {
  const { locale, t, translateAlert, translateDistrict } = useLanguage();
  const anyAlert = alert as any;
  const severity: AlertSeverity = alert.severity || 'ADVISORY';
  const sevConfig = SEVERITY_CONFIG[severity] || SEVERITY_CONFIG.ADVISORY;
  const SevIcon = sevConfig.icon;
  const rawHazard = (alert.hazardType || anyAlert.hazard_type || 'FLASH_FLOOD') as HimalayanHazardType;
  const HazardIcon = HAZARD_ICONS[rawHazard] || ShieldAlert;

  const localizedAlert = translateAlert(alert);
  const headline = localizedAlert.headline;
  const instruction = localizedAlert.instruction;
  const rawDistrict = alert.districts?.[0] || anyAlert.district || 'Chamoli';
  const district = translateDistrict(rawDistrict);
  const riverBasin = anyAlert.river_basin || '';
  const sentTimeStr = alert.sent || anyAlert.sent_time || new Date().toISOString();

  const formattedTime = new Date(sentTimeStr).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  });

  const getActionLabel = () => {
    if (locale === 'hi-IN') return 'आवश्यक कार्रवाई:';
    if (locale === 'gbm-IN') return 'बचाव कु हुकुम:';
    if (locale === 'kfy-IN') return 'बचाव कु हुकुम:';
    return 'Action Required:';
  };

  const getIssuedLabel = () => {
    if (locale === 'hi-IN') return 'जारी';
    if (locale === 'gbm-IN') return 'जारी बखत';
    if (locale === 'kfy-IN') return 'जारी बखत';
    return 'Issued';
  };

  const getViewDetailsLabel = () => {
    if (locale === 'hi-IN') return 'पूर्ण विवरण एवं मानचित्र देखें';
    if (locale === 'gbm-IN') return 'नक्शा अर पूरा विवरण देखा';
    if (locale === 'kfy-IN') return 'नक्श अर पूरो विवरण देखा';
    return 'View Details & Map';
  };

  return (
    <article
      className={`bg-white border border-slate-200 border-l-4 ${sevConfig.borderLeft} rounded-lg p-4 sm:p-5 shadow-xs hover:shadow-md transition-shadow flex flex-col justify-between gap-3`}
    >
      {/* Top Row: Severity Badge + Hazard Type + Timestamp */}
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          {/* Strict WCAG AA Severity Badge (Icon + Label + Color) */}
          <span
            className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-bold ${sevConfig.badgeBg} ${sevConfig.badgeText}`}
          >
            <SevIcon className="w-3.5 h-3.5" aria-hidden="true" />
            <span>{t.severityLabels[sevConfig.labelKey] || sevConfig.labelKey}</span>
          </span>

          <span className="inline-flex items-center gap-1 text-xs font-semibold text-slate-700 bg-slate-100 px-2 py-0.5 rounded">
            <HazardIcon className="w-3 h-3 text-slate-500" aria-hidden="true" />
            <span>{String(rawHazard).replace(/_/g, ' ')}</span>
          </span>
        </div>

        {/* Timestamp */}
        <div className="flex items-center gap-1 text-xs font-mono text-slate-500">
          <Clock className="w-3.5 h-3.5" aria-hidden="true" />
          <span>{getIssuedLabel()} {formattedTime}</span>
        </div>
      </div>

      {/* Main Content: Bold Headline & Actionable Instruction */}
      <div className="space-y-1.5">
        <h3 className="text-base sm:text-lg font-bold text-slate-900 leading-snug">
          {headline}
        </h3>

        {instruction && (
          <p className="text-sm font-medium text-slate-700 bg-slate-50 border border-slate-200 rounded p-2.5 leading-relaxed">
            <strong className="text-slate-900 uppercase text-xs block mb-0.5">
              {getActionLabel()}
            </strong>
            {instruction}
          </p>
        )}
      </div>

      {/* Bottom Metadata & Action Button */}
      <div className="pt-2 border-t border-slate-100 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-3 text-xs text-slate-600">
          <span className="flex items-center gap-1 font-semibold text-slate-800">
            <MapPin className="w-3.5 h-3.5 text-slate-400" aria-hidden="true" />
            <span>{district}</span>
          </span>
          {riverBasin && (
            <span className="hidden sm:inline text-slate-500">
              Basin: <strong>{riverBasin}</strong>
            </span>
          )}
        </div>

        <button
          onClick={() => onSelect(alert)}
          className="inline-flex items-center gap-1 text-xs font-bold text-blue-700 hover:text-blue-900 py-1 px-2 rounded hover:bg-blue-50 transition-colors"
          aria-label={`View details for alert: ${headline}`}
        >
          <span>{getViewDetailsLabel()}</span>
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>
    </article>
  );
}
