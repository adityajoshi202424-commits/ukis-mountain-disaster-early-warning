'use client';

import React, { useState, useEffect } from 'react';
import { Waves, AlertTriangle, CheckCircle2, ShieldCheck, RefreshCw, ArrowDown, Activity, Radio } from 'lucide-react';

interface DamData {
  damId: string;
  name: string;
  river: string;
  operator: string;
  district: string;
  type: string;
  fullReservoirLevelM: number;
  currentWaterLevelM: number;
  storagePct: number;
  inflowM3s: number;
  outflowDischargeM3s: number;
  spillwayStatus: string;
  preDepletionProtocol: string;
  cushionCapacityM3: string;
  downstreamThreatLevel: string;
}

export function DamTelemetryModule() {
  const [dams, setDams] = useState<DamData[]>([]);
  const [loading, setLoading] = useState(false);
  const [simulatedCloudburst, setSimulatedCloudburst] = useState(false);

  const fetchDamData = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/v1/dams/telemetry');
      if (res.ok) {
        const d = await res.json();
        setDams(d.dams || []);
      }
    } catch (err) {
      console.error('Failed to load dam telemetry', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDamData();
  }, []);

  const getThreatBadge = (level: string) => {
    switch (level) {
      case 'CRITICAL':
        return <span className="px-2 py-0.5 rounded bg-red-950 border border-red-500 text-red-400 font-mono text-[10px] font-bold animate-pulse">CRITICAL SPILL</span>;
      case 'ELEVATED':
        return <span className="px-2 py-0.5 rounded bg-amber-950 border border-amber-500 text-amber-400 font-mono text-[10px] font-bold">PRE-RELEASE ACTIVE</span>;
      default:
        return <span className="px-2 py-0.5 rounded bg-emerald-950 border border-emerald-500 text-emerald-400 font-mono text-[10px] font-bold">NORMAL DISCHARGE</span>;
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-teal-950/40 to-slate-900 border border-teal-500/40 rounded-xl p-5 shadow-lg">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="p-1.5 rounded-lg bg-teal-500/20 text-teal-400 border border-teal-400/30">
                <Waves className="w-5 h-5" />
              </span>
              <h3 className="text-lg font-black text-white tracking-tight flex items-center gap-2">
                <span>बांध एवं बैराज टेलीमेट्री एकीकरण (Dam &amp; Barrage Intelligence)</span>
                <span className="text-xs font-mono font-bold bg-teal-600/40 text-teal-300 border border-teal-500/50 px-2 py-0.5 rounded">
                  State Dam Safety Organization (SDSO) Live
                </span>
              </h3>
            </div>
            <p className="text-xs sm:text-sm text-slate-300 max-w-3xl leading-relaxed">
              Monitors critical hydroelectric reservoirs across Alaknanda and Bhagirathi basins (Tehri, Srinagar, Tapovan, Vishnuprayag). When upstream high-altitude cloudbursts or glacial moraine breaches are detected, the system triggers an **Automated Pre-Depletion Release Protocol** 45–90 minutes in advance, creating storage cushions to prevent downstream dam overtopping and catastrophic river flooding in Rishikesh and Haridwar.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setSimulatedCloudburst(!simulatedCloudburst)}
              className={`px-3 py-2 rounded-lg font-mono text-xs font-bold transition flex items-center gap-1.5 border ${
                simulatedCloudburst
                  ? 'bg-teal-600 hover:bg-teal-700 text-white border-teal-400 shadow-md'
                  : 'bg-slate-800 hover:bg-slate-700 text-teal-300 border-teal-500/40'
              }`}
            >
              <Activity className="w-4 h-4" />
              <span>{simulatedCloudburst ? 'Simulated: 1,400 m³/s Cloudburst Inflow' : 'Trigger Pre-Depletion Protocol Test'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Dams Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {dams.map((dam) => {
          const isSrinagarOrTapovan = dam.damId.includes('SRINAGAR') || dam.damId.includes('TAPOVAN');
          const effectiveInflow = simulatedCloudburst && isSrinagarOrTapovan ? dam.inflowM3s + 650 : dam.inflowM3s;
          const effectiveStoragePct = simulatedCloudburst && isSrinagarOrTapovan ? Math.max(50, dam.storagePct - 12) : dam.storagePct;

          return (
            <div
              key={dam.damId}
              className="bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-xl p-4 space-y-3 shadow-md flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between gap-2">
                  <div className="space-y-0.5">
                    <span className="font-extrabold text-sm text-white">{dam.name}</span>
                    <div className="text-[11px] text-teal-400 font-mono">
                      {dam.river} &bull; {dam.district}
                    </div>
                  </div>
                  {getThreatBadge(simulatedCloudburst && isSrinagarOrTapovan ? 'ELEVATED' : dam.downstreamThreatLevel)}
                </div>

                <div className="text-[10px] text-slate-400 font-mono mt-1">
                  Operator: <strong>{dam.operator}</strong> &bull; {dam.type}
                </div>

                {/* Reservoir Level Gauge */}
                <div className="mt-3 pt-3 border-t border-slate-800 space-y-1.5">
                  <div className="flex items-center justify-between text-xs font-mono">
                    <span className="text-slate-400">Reservoir Water Level:</span>
                    <span className="font-bold text-slate-200">
                      {dam.currentWaterLevelM}m / {dam.fullReservoirLevelM}m FRL
                    </span>
                  </div>

                  <div className="w-full h-2.5 bg-slate-950 rounded-full overflow-hidden p-0.5 border border-slate-800">
                    <div
                      className={`h-full rounded-full transition-all duration-700 ${
                        effectiveStoragePct > 85 ? 'bg-red-500' : effectiveStoragePct > 70 ? 'bg-amber-500' : 'bg-teal-500'
                      }`}
                      style={{ width: `${Math.min(100, effectiveStoragePct)}%` }}
                    />
                  </div>

                  <div className="flex items-center justify-between text-[10px] font-mono text-slate-400">
                    <span>Capacity Used: <strong>{effectiveStoragePct}%</strong></span>
                    <span className="text-teal-300">Freeboard: {(dam.fullReservoirLevelM - dam.currentWaterLevelM).toFixed(1)}m</span>
                  </div>
                </div>

                {/* Hydro Inflow vs Outflow Rate */}
                <div className="grid grid-cols-2 gap-2 mt-3 pt-3 border-t border-slate-800 text-center font-mono">
                  <div className="p-2 bg-slate-950 rounded-lg">
                    <span className="block text-[9px] text-slate-400 uppercase">Current Inflow</span>
                    <span className="block text-xs font-bold text-slate-200 mt-0.5">
                      {effectiveInflow} m³/s
                    </span>
                  </div>

                  <div className="p-2 bg-slate-950 rounded-lg">
                    <span className="block text-[9px] text-slate-400 uppercase">Spillway Outflow</span>
                    <span className="block text-xs font-bold text-teal-300 mt-0.5">
                      {dam.outflowDischargeM3s} m³/s
                    </span>
                  </div>
                </div>
              </div>

              {/* Pre-Depletion Protocol Card */}
              <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 space-y-1 mt-2">
                <div className="flex items-center justify-between text-[11px]">
                  <span className="text-slate-400 font-mono">Protocol:</span>
                  <span className="text-amber-400 font-mono font-bold text-[10px]">
                    {simulatedCloudburst && isSrinagarOrTapovan ? 'PRE-DEPLETION DRAINAGE IN PROGRESS' : dam.preDepletionProtocol}
                  </span>
                </div>
                <p className="text-[10px] text-slate-300 leading-tight">
                  {dam.cushionCapacityM3}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
