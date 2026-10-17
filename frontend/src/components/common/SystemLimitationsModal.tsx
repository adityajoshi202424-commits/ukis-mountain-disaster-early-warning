'use client';

import React, { useState, useEffect } from 'react';
import { ShieldAlert, AlertTriangle, Satellite, Database, CheckCircle2, XCircle, Clock, MapPin, X } from 'lucide-react';

interface SystemLimitationsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function SystemLimitationsModal({ isOpen, onClose }: SystemLimitationsModalProps) {
  const [activeTab, setActiveTab] = useState<'limitations' | 'coverage' | 'tiers' | 'latencies'>('limitations');
  const [reportData, setReportData] = useState<any>(null);

  useEffect(() => {
    if (!isOpen) return;
    fetch('/api/v1/system/limitations')
      .then((res) => res.json())
      .then((data) => setReportData(data))
      .catch((err) => {
        console.error('Failed to fetch limitations report:', err);
      });
  }, [isOpen]);

  if (!isOpen) return null;

  const disclaimer = reportData?.probabilistic_disclaimer || (
    'All hazard risk scores and arrival predictions are probabilistic computational estimates intended strictly for decision support by certified emergency managers (SDMA/DDMA/SDRF). They DO NOT constitute certainty and are not a replacement for official IMD, NDMA, or CWC warning bulletins.'
  );

  const whatWeDoNotClaim = reportData?.what_this_system_does_not_claim || [
    'Does NOT claim state-wide real-time InSAR slope monitoring (Sentinel-1 coherence is strictly prototype-scoped to 3 pilot slopes).',
    'Does NOT claim real-time optical lake monitoring during monsoonal cloud overcast (optical NDWI fails visibly when cloud cover > 30%).',
    'Does NOT claim instantaneous satellite rainfall (NASA GPM IMERG has a 4-hour product latency and 0.1° coarse resolution).',
    'Does NOT claim guaranteed public SMS delivery during fiber cuts or cellular tower power collapse (voice/satellite fallback is Tier 4).',
    'Does NOT claim deterministic certainty for slope failures (all outputs express calibrated probabilities with SHAP feature attributions).',
  ];

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="bg-white border border-slate-200 rounded-2xl w-full max-w-4xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden font-sans text-slate-900"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-amber-100 border border-amber-300 rounded-xl text-amber-800">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900 tracking-tight flex items-center gap-2">
                <span>SYSTEM LIMITATIONS &amp; OPERATIONAL SCOPE</span>
                <span className="px-2 py-0.5 bg-amber-100 text-amber-900 border border-amber-300 rounded text-[10px] font-bold">
                  UKIS ADDENDUM v2
                </span>
              </h2>
              <p className="text-xs text-slate-600">
                Institutional Defense Layer &bull; Honest Capabilities &bull; What This Platform Does Not Claim
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-500 hover:text-slate-800 hover:bg-slate-200/60 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-slate-200 bg-slate-100/70 px-6 gap-2 text-xs font-semibold">
          <button
            onClick={() => setActiveTab('limitations')}
            className={`py-3 px-3 border-b-2 font-bold transition-all ${
              activeTab === 'limitations'
                ? 'border-blue-900 text-blue-950 bg-white rounded-t-md shadow-sm'
                : 'border-transparent text-slate-600 hover:text-slate-900 hover:bg-slate-200/50'
            }`}
          >
            1. WHAT WE DO NOT CLAIM
          </button>
          <button
            onClick={() => setActiveTab('coverage')}
            className={`py-3 px-3 border-b-2 font-bold transition-all ${
              activeTab === 'coverage'
                ? 'border-blue-900 text-blue-950 bg-white rounded-t-md shadow-sm'
                : 'border-transparent text-slate-600 hover:text-slate-900 hover:bg-slate-200/50'
            }`}
          >
            2. WATERSHED COVERAGE
          </button>
          <button
            onClick={() => setActiveTab('tiers')}
            className={`py-3 px-3 border-b-2 font-bold transition-all ${
              activeTab === 'tiers'
                ? 'border-blue-900 text-blue-950 bg-white rounded-t-md shadow-sm'
                : 'border-transparent text-slate-600 hover:text-slate-900 hover:bg-slate-200/50'
            }`}
          >
            3. FEATURE MATURITY TIERS
          </button>
          <button
            onClick={() => setActiveTab('latencies')}
            className={`py-3 px-3 border-b-2 font-bold transition-all ${
              activeTab === 'latencies'
                ? 'border-blue-900 text-blue-950 bg-white rounded-t-md shadow-sm'
                : 'border-transparent text-slate-600 hover:text-slate-900 hover:bg-slate-200/50'
            }`}
          >
            4. DATA SOURCE LATENCIES
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1 text-sm bg-white text-slate-900">
          {/* Tab 1: Limitations & Disclaimers */}
          {activeTab === 'limitations' && (
            <div className="space-y-4">
              <div className="p-4 bg-amber-50 border border-amber-300 rounded-xl space-y-2">
                <span className="text-xs font-bold text-amber-900 uppercase tracking-wide flex items-center gap-1.5">
                  <AlertTriangle className="w-4 h-4" />
                  MANDATORY LEGAL &amp; OPERATIONAL DISCLAIMER
                </span>
                <p className="text-xs text-amber-950 leading-relaxed font-sans">
                  {disclaimer}
                </p>
              </div>

              <div className="space-y-2">
                <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                  EXPLICIT BOUNDARIES: WHAT THIS SYSTEM DOES NOT CLAIM
                </h3>
                <div className="space-y-2">
                  {whatWeDoNotClaim.map((item: string, idx: number) => (
                    <div
                      key={idx}
                      className="p-3 bg-slate-50 border border-slate-200 rounded-lg flex items-start gap-3 text-xs"
                    >
                      <XCircle className="w-4 h-4 text-red-600 flex-shrink-0 mt-0.5" />
                      <span className="text-slate-800 font-sans">{item}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="p-3.5 bg-blue-50 border border-blue-200 rounded-lg text-xs text-blue-950">
                <span className="font-bold">CORE POSITIONING: </span>
                Explainability + Real Authoritative Data + Actionable Output + Honest Limitations.
                We refuse to oversell technology we did not stand up.
              </div>
            </div>
          )}

          {/* Tab 2: Watershed Coverage Matrix */}
          {activeTab === 'coverage' && (
            <div className="space-y-4">
              <div className="text-xs text-slate-600">
                Audited spatial sensor &amp; satellite coverage across Uttarakhand high-risk corridors:
              </div>
              <div className="space-y-2.5">
                {(reportData?.watershed_coverage_matrix || []).map((row: any, i: number) => {
                  const isFull = row.coverage_level === 'FULL_TELEMETRY';
                  const isPartial = row.coverage_level === 'PARTIAL_SATELLITE_ONLY';
                  return (
                    <div
                      key={i}
                      className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl space-y-1.5 text-xs"
                    >
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <span className="font-bold text-slate-900 flex items-center gap-1.5">
                          <MapPin className="w-3.5 h-3.5 text-blue-700" />
                          {row.watershed_or_corridor} ({row.district})
                        </span>
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                            isFull
                              ? 'bg-emerald-100 text-emerald-900 border-emerald-300'
                              : isPartial
                              ? 'bg-amber-100 text-amber-900 border-amber-300'
                              : 'bg-red-100 text-red-900 border-red-300'
                          }`}
                        >
                          {row.coverage_level}
                        </span>
                      </div>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px] text-slate-600 pt-1">
                        <div>
                          <span className="font-semibold text-slate-700">Ground Sensors: </span>
                          {row.ground_sensors}
                        </div>
                        <div>
                          <span className="font-semibold text-slate-700">Satellites: </span>
                          {row.satellite_layers}
                        </div>
                      </div>
                      <div className="text-[11px] text-slate-600 pt-1 border-t border-slate-200">
                        {row.operational_notes}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Tab 3: Feature Maturity Tiers */}
          {activeTab === 'tiers' && (
            <div className="space-y-4">
              <div className="text-xs text-slate-600">
                All 24 system features classified by operational maturity:
              </div>
              <div className="space-y-2">
                {(reportData?.feature_maturity_tiers || []).map((feat: any, idx: number) => {
                  const isLive = feat.operational_maturity === 'LIVE_OPERATIONAL';
                  const isProto = feat.operational_maturity === 'PROTOTYPE_SCOPE';
                  return (
                    <div
                      key={idx}
                      className="p-3.5 bg-slate-50 border border-slate-200 rounded-lg flex flex-wrap items-center justify-between gap-2 text-xs"
                    >
                      <div className="space-y-0.5 max-w-xl">
                        <span className="text-slate-900 font-bold block">
                          #{feat.item_number}. {feat.name}
                        </span>
                        <span className="text-[11px] text-slate-600 block">
                          {feat.scope_statement}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 bg-white border border-slate-300 text-slate-700 rounded text-[10px] font-bold shadow-sm">
                          {feat.tier}
                        </span>
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                            isLive
                              ? 'bg-emerald-100 text-emerald-900 border-emerald-300'
                              : isProto
                              ? 'bg-blue-100 text-blue-900 border-blue-300'
                              : 'bg-slate-200 text-slate-700 border-slate-300'
                          }`}
                        >
                          {feat.operational_maturity}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Tab 4: Data Latency Matrix */}
          {activeTab === 'latencies' && (
            <div className="space-y-4">
              <div className="text-xs text-slate-600">
                Realistic latency specifications for external telemetry and satellite passes:
              </div>
              <div className="space-y-2.5">
                {(reportData?.data_latency_matrix || []).map((lat: any, idx: number) => (
                  <div
                    key={idx}
                    className="p-3.5 bg-slate-50 border border-slate-200 rounded-xl space-y-1 text-xs"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <span className="font-bold text-slate-900 flex items-center gap-1.5">
                        <Satellite className="w-3.5 h-3.5 text-blue-700" />
                        {lat.source_name}
                      </span>
                      <span className="px-2 py-0.5 bg-blue-100 text-blue-900 border border-blue-300 rounded text-[10px] font-bold">
                        {lat.provider}
                      </span>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px] text-slate-600 pt-1">
                      <div>
                        <span className="font-semibold text-slate-700">Cadence: </span>
                        {lat.update_cadence}
                      </div>
                      <div>
                        <span className="font-semibold text-slate-700">Latency: </span>
                        <span className="text-amber-800 font-bold">{lat.typical_latency}</span>
                      </div>
                    </div>
                    <div className="text-[11px] text-slate-600 pt-1 border-t border-slate-200">
                      {lat.operational_implication}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-slate-200 bg-slate-50 flex items-center justify-between text-xs text-slate-600">
          <span>UKIS 2026 Problem Statement P-011</span>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-blue-900 hover:bg-blue-800 text-white font-bold rounded-lg transition-colors text-xs shadow-sm"
          >
            DISMISS PANEL
          </button>
        </div>
      </div>
    </div>
  );
}
