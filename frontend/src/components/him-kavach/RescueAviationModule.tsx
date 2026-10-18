'use client';

import React, { useState, useEffect } from 'react';
import { Wind, CloudRain, CheckCircle2, AlertTriangle, XCircle, Navigation, RefreshCw, Compass, ArrowUpRight } from 'lucide-react';

interface HelipadWeather {
  helipadId: string;
  name: string;
  district: string;
  elevationM: number;
  coordinates: [number, number];
  visibilityKm: number;
  windSpeedKnots: number;
  windGustsKnots: number;
  cloudCeilingAglM: number;
  freezingLevelM: number;
  flightStatus: 'SAFE_TO_FLY' | 'MARGINAL' | 'GROUNDED';
  suitableAircraft: string;
  currentWindow: string;
  nextRiskFactor: string;
}

export function RescueAviationModule() {
  const [helipads, setHelipads] = useState<HelipadWeather[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedHelipad, setSelectedHelipad] = useState<string>('HP-GAUCHER-SDRF');

  const fetchAviationData = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/v1/aviation/weather-windows');
      if (res.ok) {
        const d = await res.json();
        setHelipads(d.helipads || []);
      }
    } catch (err) {
      console.error('Failed to load aviation data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAviationData();
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'SAFE_TO_FLY':
        return <CheckCircle2 className="w-4 h-4 text-emerald-400" />;
      case 'MARGINAL':
        return <AlertTriangle className="w-4 h-4 text-amber-400" />;
      case 'GROUNDED':
        return <XCircle className="w-4 h-4 text-red-500" />;
      default:
        return null;
    }
  };

  const getStatusPill = (status: string) => {
    switch (status) {
      case 'SAFE_TO_FLY':
        return (
          <span className="px-2 py-0.5 rounded bg-emerald-950 border border-emerald-500/50 text-emerald-300 font-mono text-[10px] font-bold">
            SAFE TO FLY
          </span>
        );
      case 'MARGINAL':
        return (
          <span className="px-2 py-0.5 rounded bg-amber-950 border border-amber-500/50 text-amber-300 font-mono text-[10px] font-bold">
            MARGINAL (RISK)
          </span>
        );
      case 'GROUNDED':
        return (
          <span className="px-2 py-0.5 rounded bg-red-950 border border-red-500/50 text-red-300 font-mono text-[10px] font-bold animate-pulse">
            GROUNDED (NO-FLY)
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-sky-950/40 to-slate-900 border border-sky-500/40 rounded-xl p-5 shadow-lg">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="p-1.5 rounded-lg bg-sky-500/20 text-sky-400 border border-sky-400/30">
                <Navigation className="w-5 h-5" />
              </span>
              <h3 className="text-lg font-black text-white tracking-tight flex items-center gap-2">
                <span>हेलिकॉप्टर एवं रेस्क्यू ड्रोन मौसम-खिड़की विश्लेषक</span>
                <span className="text-xs font-mono font-bold bg-sky-600/40 text-sky-300 border border-sky-500/50 px-2 py-0.5 rounded">
                  SDRF &amp; IAF Chinook Flight Safety
                </span>
              </h3>
            </div>
            <p className="text-xs sm:text-sm text-slate-300 max-w-3xl leading-relaxed">
              Provides real-time **2-Hour Rescue Aviation Windows** for Indian Air Force (Chinook, Mi-17 V5), SDRF, and civil mountain evacuation helicopters. Continuously evaluates valley venturi wind shear, horizontal visibility, and cloud base height (AGL) to prevent fatal mountain aviation incidents in steep gorges like Kedarnath, Badrinath, and Gaucher.
            </p>
          </div>

          <button
            onClick={fetchAviationData}
            disabled={loading}
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-sky-300 rounded-lg font-mono text-xs font-bold transition flex items-center gap-1.5 border border-sky-500/30 w-fit"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Update Aviation Telemetry</span>
          </button>
        </div>
      </div>

      {/* Helipads Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {helipads.map((h) => {
          const isSelected = selectedHelipad === h.helipadId;

          return (
            <div
              key={h.helipadId}
              onClick={() => setSelectedHelipad(h.helipadId)}
              className={`p-4 rounded-xl border cursor-pointer transition-all ${
                isSelected
                  ? 'bg-sky-950/40 border-sky-500 ring-1 ring-sky-400 shadow-lg'
                  : 'bg-slate-900 border-slate-800 hover:bg-slate-850'
              }`}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="space-y-0.5">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-bold text-white">{h.name}</span>
                  </div>
                  <div className="text-[11px] text-slate-400 font-mono">
                    {h.district} &bull; Elev: <strong>{h.elevationM}m</strong>
                  </div>
                </div>
                {getStatusPill(h.flightStatus)}
              </div>

              {/* Weather Telemetry Row */}
              <div className="grid grid-cols-3 gap-2 mt-3 pt-3 border-t border-slate-800 text-center font-mono">
                <div className="p-2 bg-slate-950 rounded-lg">
                  <span className="block text-[9px] text-slate-400">VISIBILITY</span>
                  <span className={`block text-xs font-bold ${h.visibilityKm < 3 ? 'text-red-400' : 'text-slate-200'}`}>
                    {h.visibilityKm} km
                  </span>
                </div>

                <div className="p-2 bg-slate-950 rounded-lg">
                  <span className="block text-[9px] text-slate-400">WIND GUSTS</span>
                  <span className={`block text-xs font-bold ${h.windGustsKnots > 20 ? 'text-red-400' : 'text-slate-200'}`}>
                    {h.windGustsKnots} kts
                  </span>
                </div>

                <div className="p-2 bg-slate-950 rounded-lg">
                  <span className="block text-[9px] text-slate-400">CLOUD BASE</span>
                  <span className={`block text-xs font-bold ${h.cloudCeilingAglM < 500 ? 'text-red-400' : 'text-slate-200'}`}>
                    {h.cloudCeilingAglM}m AGL
                  </span>
                </div>
              </div>

              {/* 2-Hour Aviation Window */}
              <div className="mt-3 p-2.5 rounded-lg bg-slate-950/70 border border-slate-800 space-y-1">
                <div className="flex items-center justify-between text-[11px]">
                  <span className="text-slate-400 font-mono">Safe Flight Window:</span>
                  <span className="text-white font-mono font-bold text-[10px]">{h.currentWindow}</span>
                </div>
                <div className="text-[10px] text-slate-400 leading-tight">
                  Next Risk: <span className="text-amber-300/80">{h.nextRiskFactor}</span>
                </div>
                <div className="text-[10px] text-slate-500 font-mono pt-1 border-t border-slate-850">
                  Approved: {h.suitableAircraft}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
