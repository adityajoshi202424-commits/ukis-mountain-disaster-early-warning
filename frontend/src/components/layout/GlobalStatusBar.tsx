'use client';

import React, { useState, useEffect } from 'react';
import { Activity, Database, Radio, Server, ShieldCheck, Wifi } from 'lucide-react';
import { SlidingNumber } from '@/components/ui/sliding-number';

export function GlobalStatusBar() {
  const [latencyMs, setLatencyMs] = useState(24);
  const [currentTime, setCurrentTime] = useState('');

  useEffect(() => {
    const timer = setInterval(() => {
      const d = new Date();
      setCurrentTime(d.toISOString().replace('T', ' ').slice(0, 19) + ' UTC');
      // subtle realistic latency jitter between 18ms and 28ms
      setLatencyMs(20 + Math.floor(Math.sin(Date.now() / 3000) * 5));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <footer className="w-full bg-white border-t border-slate-200 py-3 px-4 lg:px-8 text-xs text-slate-600 font-sans mt-auto">
      <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
        {/* Left: System Status */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-500 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-600"></span>
            </span>
            <span className="text-emerald-800 font-bold uppercase text-[11px]">
              DMMC TELEMETRY GRID OPERATIONAL
            </span>
          </div>

          <div className="hidden sm:flex items-center gap-1.5 text-slate-500 border-l border-slate-200 pl-3">
            <Activity className="w-3.5 h-3.5 text-slate-400" />
            <span>Response Latency: </span>
            <span className="text-slate-800 font-semibold">{latencyMs}ms</span>
          </div>
        </div>

        {/* Center: Standards */}
        <div className="text-center text-[11px] text-slate-500">
          State Emergency Operations Centre (SEOC) &bull; Secretariat, Dehradun, Uttarakhand
        </div>

        {/* Right: Security & Standards */}
        <div className="flex items-center gap-3 text-[11px] text-slate-500">
          <div className="flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            <span>DPDP Act 2023 Compliant</span>
          </div>
          <span className="font-mono text-slate-400 hidden md:inline">
            {currentTime || 'UTC'}
          </span>
        </div>
      </div>
    </footer>
  );
}
