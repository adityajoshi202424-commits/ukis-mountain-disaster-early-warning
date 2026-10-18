'use client';

import React, { useState, useEffect } from 'react';
import { Bus, MapPin, ShieldAlert, AlertTriangle, CheckCircle2, Sliders, Users, ArrowRight, RefreshCw, Car } from 'lucide-react';

interface TownCapacity {
  town: string;
  highwayKm: number;
  activeVehiclesEnRoute: number;
  holdingCapacityVehicles: number;
  currentOccupancyVehicles: number;
  availableCapacity: number;
  shelters: string;
  policeCheckpost: string;
  status: string;
  directive: string;
}

export function CharDhamBalancerModule() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [simulatedIncident, setSimulatedIncident] = useState(false);

  const fetchCapacity = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/v1/chardham/holding-balancer');
      if (res.ok) {
        const d = await res.json();
        setData(d);
      }
    } catch (err) {
      console.error('Failed to load Char Dham balancer data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCapacity();
  }, []);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'EVACUATE_CORRIDOR':
        return <span className="px-2 py-0.5 rounded bg-red-950 border border-red-500 text-red-400 font-mono text-[10px] font-bold">EVACUATE CORRIDOR</span>;
      case 'HOLD_AT_GATE':
        return <span className="px-2 py-0.5 rounded bg-amber-950 border border-amber-500 text-amber-400 font-mono text-[10px] font-bold">HOLD CONVOYS</span>;
      case 'NEAR_CAPACITY':
        return <span className="px-2 py-0.5 rounded bg-yellow-950 border border-yellow-500 text-yellow-300 font-mono text-[10px] font-bold">NEAR CAPACITY</span>;
      case 'RESTRICTED_FLOW':
        return <span className="px-2 py-0.5 rounded bg-blue-950 border border-blue-500 text-blue-300 font-mono text-[10px] font-bold">RESTRICTED FLOW</span>;
      default:
        return <span className="px-2 py-0.5 rounded bg-emerald-950 border border-emerald-500 text-emerald-400 font-mono text-[10px] font-bold">CONVOYS PERMITTED</span>;
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-amber-950/50 to-slate-900 border border-amber-500/40 rounded-xl p-5 shadow-lg">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="p-1.5 rounded-lg bg-amber-500/20 text-amber-400 border border-amber-400/30">
                <Bus className="w-5 h-5" />
              </span>
              <h3 className="text-lg font-black text-white tracking-tight flex items-center gap-2">
                <span>चारधाम यात्रा एवं पर्यटक धारण क्षमता नियंत्रक</span>
                <span className="text-xs font-mono font-bold bg-amber-600/40 text-amber-300 border border-amber-500/50 px-2 py-0.5 rounded">
                  UTDB Biometric Portal Synchronized
                </span>
              </h3>
            </div>
            <p className="text-xs sm:text-sm text-slate-300 max-w-3xl leading-relaxed">
              Dynamically monitors tourist vehicles registered via the **Uttarakhand Tourism Development Board (UTDB) Biometric Portal**. When upper corridors enter Yellow or Red threat tiers, the balancer identifies upstream police checkposts to halt convoys—ensuring towns like Srinagar, Devprayag, and Karnaprayag do not exceed their municipal shelter and food capacities.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setSimulatedIncident(!simulatedIncident)}
              className={`px-3 py-2 rounded-lg font-mono text-xs font-bold transition flex items-center gap-1.5 border ${
                simulatedIncident
                  ? 'bg-red-600 hover:bg-red-700 text-white border-red-400 shadow-md animate-pulse'
                  : 'bg-slate-800 hover:bg-slate-700 text-amber-400 border-amber-500/50'
              }`}
            >
              <AlertTriangle className="w-4 h-4" />
              <span>{simulatedIncident ? 'Simulated Red Alert: Joshimath' : 'Simulate Red Incident at Joshimath'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Aggregate Metrics Cards */}
      {data && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-1">
            <span className="text-[10px] font-mono uppercase text-slate-400">Total En Route Vehicles</span>
            <div className="text-2xl font-black text-white flex items-center gap-2">
              <Car className="w-5 h-5 text-indigo-400" />
              <span>{data.totalVehiclesInTransit.toLocaleString()}</span>
            </div>
            <span className="text-[10px] text-slate-500 font-mono">Buses, SUVs &amp; Private Cars</span>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-1">
            <span className="text-[10px] font-mono uppercase text-slate-400">Estimated Pilgrims</span>
            <div className="text-2xl font-black text-amber-400 flex items-center gap-2">
              <Users className="w-5 h-5 text-amber-400" />
              <span>{data.estimatedPilgrimsInTransit.toLocaleString()}</span>
            </div>
            <span className="text-[10px] text-slate-500 font-mono">Biometric registered count</span>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-1">
            <span className="text-[10px] font-mono uppercase text-slate-400">Corridor Capacity Load</span>
            <div className="text-2xl font-black text-slate-200 flex items-center gap-2">
              <span>{data.corridorLoadPct}%</span>
              <span className="text-xs font-mono font-bold text-amber-400">
                ({data.totalHoldingCapacity.toLocaleString()} Max)
              </span>
            </div>
            <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden mt-1">
              <div
                className={`h-full ${data.corridorLoadPct > 80 ? 'bg-red-500' : 'bg-emerald-500'}`}
                style={{ width: `${Math.min(100, data.corridorLoadPct)}%` }}
              />
            </div>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-1">
            <span className="text-[10px] font-mono uppercase text-slate-400">Overall Gate Strategy</span>
            <div className="text-xs font-mono font-bold text-emerald-400 bg-emerald-950/80 border border-emerald-500/40 px-2 py-1.5 rounded mt-1">
              {simulatedIncident ? 'HOLD_AT_RISHIKESH_BARRIER' : data.recommendedGateAction}
            </div>
            <span className="text-[10px] text-slate-500 font-mono">Automated DEOC directive</span>
          </div>
        </div>
      )}

      {/* Town-by-Town Highway Holding Matrix */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
        <div className="p-4 bg-slate-950/80 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <MapPin className="w-4 h-4 text-amber-400" />
            <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-300">
              NH-07 Badrinath Corridor Holding Capacity &amp; Police Checkposts
            </span>
          </div>
          <span className="text-[11px] font-mono text-slate-400">From Rishikesh (Km 0) to Joshimath (Km 252)</span>
        </div>

        {loading ? (
          <div className="py-12 text-center text-slate-400 font-mono text-xs flex items-center justify-center gap-2">
            <RefreshCw className="w-4 h-4 animate-spin text-amber-400" />
            <span>Fetching live checkpost telemetry...</span>
          </div>
        ) : (
          <div className="divide-y divide-slate-800 overflow-x-auto">
            {data?.towns.map((t: TownCapacity) => {
              const occupancyPct = Math.round((t.currentOccupancyVehicles / t.holdingCapacityVehicles) * 100);
              const isOverloaded = occupancyPct >= 90;

              return (
                <div key={t.town} className="p-4 hover:bg-slate-850 transition-colors flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                  <div className="space-y-1 min-w-[240px]">
                    <div className="flex items-center gap-2">
                      <span className="font-extrabold text-sm text-white">{t.town}</span>
                      <span className="text-[10px] font-mono bg-slate-800 text-slate-400 px-1.5 py-0.2 rounded">
                        Km {t.highwayKm}
                      </span>
                      {getStatusBadge(simulatedIncident && t.town.includes('Joshimath') ? 'EVACUATE_CORRIDOR' : t.status)}
                    </div>
                    <div className="text-[11px] text-slate-400 font-mono flex items-center gap-1.5">
                      <span>Gate: <strong>{t.policeCheckpost}</strong></span>
                    </div>
                    <div className="text-[11px] text-slate-400">
                      Shelters: <span className="text-slate-300">{t.shelters}</span>
                    </div>
                  </div>

                  {/* Occupancy Progress Bar */}
                  <div className="min-w-[200px] space-y-1">
                    <div className="flex items-center justify-between text-xs font-mono">
                      <span className="text-slate-400">Occupancy:</span>
                      <span className={`font-bold ${isOverloaded ? 'text-red-400' : 'text-slate-200'}`}>
                        {t.currentOccupancyVehicles} / {t.holdingCapacityVehicles} ({occupancyPct}%)
                      </span>
                    </div>
                    <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className={`h-full ${
                          occupancyPct >= 90 ? 'bg-red-500' : occupancyPct >= 70 ? 'bg-amber-500' : 'bg-emerald-500'
                        }`}
                        style={{ width: `${Math.min(100, occupancyPct)}%` }}
                      />
                    </div>
                    <span className="text-[10px] text-slate-500 font-mono">
                      Available: {t.availableCapacity} tourist vehicles
                    </span>
                  </div>

                  {/* Operational Police Directive */}
                  <div className="max-w-md bg-slate-950 p-2.5 rounded-lg border border-slate-800 text-xs text-slate-300">
                    <span className="block text-[10px] font-mono font-bold text-amber-400 uppercase">
                      Police Checkpost Directive
                    </span>
                    <p className="mt-0.5 leading-snug">
                      {simulatedIncident && t.town.includes('Rishikesh')
                        ? '🚨 CRITICAL OVERRIDE: Hold all Badrinath convoys at Tapovan barrier. Redirect tourists to Bharat Bhoomi holding camp.'
                        : t.directive}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
