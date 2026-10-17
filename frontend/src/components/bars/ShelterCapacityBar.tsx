'use client';

import React from 'react';
import { motion } from 'motion/react';
import { cn } from '@/lib/utils';
import { Users } from 'lucide-react';

interface ShelterCapacityBarProps {
  shelterName?: string;
  capacity: number;
  occupancy: number;
  elevationM?: number;
  label?: string;
  className?: string;
}

export function ShelterCapacityBar({
  shelterName,
  capacity,
  occupancy,
  elevationM,
  className,
}: ShelterCapacityBarProps) {
  const percentage = Math.min(100, Math.round((occupancy / Math.max(1, capacity)) * 100));
  const isCritical = percentage >= 95;
  const isWarning = percentage >= 75 && percentage < 95;

  const barColor = isCritical
    ? 'linear-gradient(90deg, #ef4444, #dc2626)'
    : isWarning
    ? 'linear-gradient(90deg, #f59e0b, #d97706)'
    : 'linear-gradient(90deg, #10b981, #059669)';

  const badgeColor = isCritical
    ? 'bg-red-100 text-red-800 border-red-300'
    : isWarning
    ? 'bg-amber-100 text-amber-900 border-amber-300'
    : 'bg-emerald-100 text-emerald-900 border-emerald-300';

  return (
    <div className={cn('p-3.5 bg-slate-50 border border-slate-200 rounded-lg space-y-2', className)}>
      <div className="flex justify-between items-center text-xs">
        <div className="flex items-center gap-2">
          <Users className="w-3.5 h-3.5 text-blue-700" />
          <span className="font-bold text-slate-900">{shelterName}</span>
          {elevationM && (
            <span className="text-[10px] text-slate-500 font-mono">El: {elevationM}m</span>
          )}
        </div>
        <span className={cn('text-[10px] font-bold px-2 py-0.5 rounded border', badgeColor)}>
          {percentage}% {isCritical ? 'CRITICAL (OVERFLOW)' : isWarning ? 'WATCH' : 'NOMINAL'}
        </span>
      </div>

      {/* Progress Track */}
      <div className="w-full h-2.5 bg-slate-200 rounded-full overflow-hidden border border-slate-300 relative">
        <motion.div
          className="h-full rounded-full relative"
          style={{ background: barColor }}
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        />
      </div>

      <div className="flex justify-between items-center text-[11px] font-mono text-slate-600">
        <span>Occupancy: <strong>{occupancy}</strong> / {capacity} Beds</span>
        <span>{capacity - occupancy > 0 ? `${capacity - occupancy} Beds Remaining` : '0 Available (Redirecting)'}</span>
      </div>
    </div>
  );
}
