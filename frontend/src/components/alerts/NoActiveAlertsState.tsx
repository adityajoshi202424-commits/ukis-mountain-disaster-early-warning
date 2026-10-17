'use client';

import React from 'react';
import { ShieldCheck, CheckCircle2, Clock } from 'lucide-react';
import { UttarakhandDistrict } from '@/types/shared_cap';

interface NoActiveAlertsStateProps {
  district: UttarakhandDistrict | 'ALL';
  lastCheckedTime?: string;
}

export function NoActiveAlertsState({
  district,
  lastCheckedTime = 'Just now',
}: NoActiveAlertsStateProps) {
  const districtName = district === 'ALL' ? 'Uttarakhand (All Districts)' : `${district} District`;

  return (
    <div className="bg-emerald-50 border border-emerald-300 rounded-lg p-6 text-center space-y-3 shadow-xs">
      <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-emerald-100 text-emerald-700 mx-auto">
        <ShieldCheck className="w-7 h-7" aria-hidden="true" />
      </div>

      <div className="space-y-1">
        <h3 className="text-base sm:text-lg font-bold text-emerald-950">
          No Active Warnings or Evacuation Orders
        </h3>
        <p className="text-sm text-emerald-800 max-w-lg mx-auto leading-relaxed">
          All sensor telemetry for <strong>{districtName}</strong> is baseline nominal. 
          CWC river gauges, IMD nowcasts, and IIT Roorkee seismic telemetry report no flash-flood or cloudburst threats.
        </p>
      </div>

      <div className="pt-2 flex items-center justify-center gap-1.5 text-xs text-emerald-700 font-mono">
        <Clock className="w-3.5 h-3.5" aria-hidden="true" />
        <span>Telemetry verified: {lastCheckedTime}</span>
      </div>
    </div>
  );
}
