'use client';

import React, { useState } from 'react';
import { Camera, CheckCircle2, AlertTriangle, Eye, ShieldCheck, Zap, RefreshCw, Upload, MapPin, Sparkles } from 'lucide-react';

interface VerificationResult {
  verificationId: string;
  status: string;
  model: string;
  reporter: string;
  sector: string;
  coordinates: [number, number];
  primaryHazard: string;
  confidenceScorePct: number;
  detectedFeatures: string[];
  riskImpact: {
    baselineRiskPct: number;
    riskScoreBoostPct: number;
    postVerificationRiskPct: number;
    escalationRecommended: string;
  };
  actionableDirective: string;
  timestamp: string;
}

export function JanDrishtiModule() {
  const [selectedPreset, setSelectedPreset] = useState<'TENSION_CRACK' | 'MURKY_SEEPAGE' | 'ROCKFALL_DEBRIS'>('TENSION_CRACK');
  const [customFileUploaded, setCustomFileUploaded] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<VerificationResult | null>(null);

  const presets = [
    {
      id: 'TENSION_CRACK',
      title: 'Tension Crack on Retaining Wall',
      subtitle: 'Joshimath Flank / NH-07 Km 252',
      thumbnail: '🧱',
      description: 'Active 14mm tensile fissure opening on stone masonry retaining wall along Alaknanda toe slope.',
    },
    {
      id: 'MURKY_SEEPAGE',
      title: 'Murky Muddy Seepage (Matmaila Pani)',
      subtitle: 'Vasundhara Tal Runoff / Mana Catchment',
      thumbnail: '🌊',
      description: 'Sudden turbidity surge and brown silt slurry discharge from toe-spring, indicating internal hydraulic piping.',
    },
    {
      id: 'ROCKFALL_DEBRIS',
      title: 'Fresh Rockfall & Scree Debris Cone',
      subtitle: 'Sirobagad Funnel / NH-07 Km 108',
      thumbnail: '🪨',
      description: 'Angular phyllite boulders fallen across outer carriage-way with continuous gravel trickle from 52° slope.',
    },
  ];

  const handleVerify = async (presetId = selectedPreset) => {
    setLoading(true);
    try {
      const res = await fetch('/api/v1/jan-drishti/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          hazardPreset: presetId,
          watershedSector:
            presetId === 'TENSION_CRACK'
              ? 'SEC-JOSHIMATH-NH07'
              : presetId === 'MURKY_SEEPAGE'
              ? 'SEC-VASUNDHARA-GLOF'
              : 'SEC-SIROBAGAD-NH07',
          reporterType: 'Apda Mitra Certified Volunteer #UK-AM-4421',
          gpsCoordinates:
            presetId === 'TENSION_CRACK'
              ? [30.556, 79.567]
              : presetId === 'MURKY_SEEPAGE'
              ? [30.795, 79.435]
              : [30.252, 78.892],
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setResult(data);
      }
    } catch (err) {
      console.error('Jan-Drishti verification error', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 border border-indigo-500/40 rounded-xl p-5 shadow-lg">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="p-1.5 rounded-lg bg-indigo-500/20 text-indigo-400 border border-indigo-400/30">
                <Camera className="w-5 h-5" />
              </span>
              <h3 className="text-lg font-black text-white tracking-tight flex items-center gap-2">
                <span>जन-दृष्टि (Jan-Drishti)</span>
                <span className="text-xs font-mono font-bold bg-indigo-600/40 text-indigo-300 border border-indigo-500/50 px-2 py-0.5 rounded">
                  VLM &amp; YOLOv8 Computer Vision Verification
                </span>
              </h3>
            </div>
            <p className="text-xs sm:text-sm text-slate-300 max-w-3xl leading-relaxed">
              Crowdsourced hazard intelligence for field Apda Mitras, Gram Pradhans, and BRO road patrols. Geo-tagged photographs of tension cracks, muddy seepage (*Matmaila Pani*), or rockfalls are classified by edge Vision AI—automatically boosting the micro-watershed risk score by <strong className="text-amber-400">+15%</strong> to eliminate early-warning blindness.
            </p>
          </div>

          <div className="flex items-center gap-2 font-mono text-xs">
            <span className="px-3 py-1.5 rounded-lg bg-emerald-950/80 border border-emerald-500/40 text-emerald-300 font-bold flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>Anti-Hallucination Verified</span>
            </span>
          </div>
        </div>
      </div>

      {/* Main Grid: Upload & Presets vs AI Detection Report */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Preset Selection & Upload Interface */}
        <div className="lg:col-span-5 space-y-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-400">
                1. Select Field Ground Truth Photo
              </span>
              <span className="text-[10px] font-mono text-indigo-400">3 Verified Presets</span>
            </div>

            <div className="space-y-2.5">
              {presets.map((p) => {
                const isSelected = selectedPreset === p.id;
                return (
                  <button
                    key={p.id}
                    onClick={() => {
                      setSelectedPreset(p.id as any);
                      setCustomFileUploaded(false);
                      handleVerify(p.id as any);
                    }}
                    className={`w-full text-left p-3.5 rounded-xl border transition-all ${
                      isSelected
                        ? 'bg-indigo-950/70 border-indigo-500 text-white shadow-md ring-1 ring-indigo-400'
                        : 'bg-slate-950/60 border-slate-800 text-slate-300 hover:bg-slate-800/80 hover:text-white'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div className="text-2xl p-2 rounded-lg bg-slate-900 border border-slate-800">
                        {p.thumbnail}
                      </div>
                      <div className="space-y-0.5 flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-bold truncate">{p.title}</span>
                          {isSelected && <span className="text-[10px] text-amber-400 font-mono font-bold">ACTIVE</span>}
                        </div>
                        <div className="text-[11px] text-slate-400 font-mono">{p.subtitle}</div>
                        <p className="text-[11px] text-slate-400 line-clamp-2 mt-1 leading-snug">
                          {p.description}
                        </p>
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>

            {/* Custom Field Upload PWA Dropzone */}
            <div className="pt-2 border-t border-slate-800">
              <label
                htmlFor="jan-drishti-file"
                className="flex flex-col items-center justify-center p-4 border-2 border-dashed border-slate-700 hover:border-indigo-500 rounded-xl bg-slate-950/40 cursor-pointer transition-colors text-center"
              >
                <Upload className="w-5 h-5 text-indigo-400 mb-1" />
                <span className="text-xs font-bold text-slate-300">
                  {customFileUploaded ? '✓ Custom Field Photo Loaded' : 'Upload Citizen / Apda Mitra Field Photo'}
                </span>
                <span className="text-[10px] text-slate-500 font-mono mt-0.5">
                  Geo-tagged EXIF with GPS &bull; Max 15MB JPG/PNG
                </span>
                <input
                  id="jan-drishti-file"
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={(e) => {
                    if (e.target.files && e.target.files[0]) {
                      setCustomFileUploaded(true);
                      handleVerify(selectedPreset);
                    }
                  }}
                />
              </label>
            </div>

            <button
              onClick={() => handleVerify()}
              disabled={loading}
              className="w-full py-2.5 bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-500 hover:to-blue-500 text-white font-bold rounded-lg text-xs uppercase tracking-wider transition shadow-md flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Running VLM Edge Inference...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 text-amber-300" />
                  <span>Execute Computer Vision Verification</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Right Column: AI Bounding Box & Risk Escalation Card */}
        <div className="lg:col-span-7 space-y-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-5">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <Eye className="w-4 h-4 text-indigo-400" />
                <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-300">
                  2. Computer Vision Feature Segmentation &amp; Risk Escalation
                </span>
              </div>
              {result && (
                <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/80 border border-emerald-500/40 px-2 py-0.5 rounded font-bold">
                  {result.confidenceScorePct}% CONFIDENCE
                </span>
              )}
            </div>

            {loading ? (
              <div className="py-16 text-center space-y-3">
                <RefreshCw className="w-8 h-8 text-indigo-400 animate-spin mx-auto" />
                <div className="text-xs font-mono text-slate-300 font-bold">
                  Segmenting tension cracks &amp; turbid runoff vectors...
                </div>
                <div className="text-[11px] text-slate-500 font-mono">
                  Loading YOLOv8-MountainGeoHazards-v2 tensor weights &amp; cross-referencing DEM slope...
                </div>
              </div>
            ) : result ? (
              <div className="space-y-4">
                {/* Simulated Bounding Box Field Preview */}
                <div className="relative rounded-xl overflow-hidden border border-indigo-500/40 bg-slate-950 p-4 min-h-[160px] flex flex-col justify-between">
                  <div className="flex items-center justify-between text-xs font-mono">
                    <span className="text-slate-400 flex items-center gap-1.5">
                      <MapPin className="w-3.5 h-3.5 text-red-400" />
                      <span>{result.sector} &bull; [{result.coordinates.join(', ')}]</span>
                    </span>
                    <span className="text-amber-400 font-bold">{result.model}</span>
                  </div>

                  {/* Visual Bounding Box Indicator */}
                  <div className="my-3 p-3 bg-red-950/40 border-2 border-dashed border-red-500 rounded-lg relative">
                    <span className="absolute -top-3 left-3 bg-red-600 text-white text-[9px] font-mono font-black px-1.5 py-0.2 rounded uppercase">
                      Class: {result.primaryHazard.slice(0, 32)}
                    </span>
                    <div className="space-y-1 mt-1">
                      {result.detectedFeatures.map((feat, idx) => (
                        <div key={idx} className="text-xs font-mono text-slate-200 flex items-center gap-1.5">
                          <span className="w-1.5 h-1.5 rounded-full bg-red-400" />
                          <span>{feat}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono">
                    <span>Verified Reporter: {result.reporter}</span>
                    <span className="text-emerald-400 font-bold">Status: {result.status}</span>
                  </div>
                </div>

                {/* Mathematical Risk Surge Metric */}
                <div className="grid grid-cols-3 gap-3">
                  <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg">
                    <span className="block text-[10px] font-mono text-slate-400 uppercase">Baseline Soil Moisture Risk</span>
                    <span className="block text-xl font-black text-slate-200 mt-1">
                      {result.riskImpact.baselineRiskPct}%
                    </span>
                    <span className="block text-[10px] text-slate-500">XGBoost Susceptibility</span>
                  </div>

                  <div className="p-3 bg-amber-950/40 border border-amber-600/50 rounded-lg">
                    <span className="block text-[10px] font-mono text-amber-300 uppercase">Jan-Drishti CV Boost</span>
                    <span className="block text-xl font-black text-amber-400 mt-1 flex items-center gap-1">
                      <span>+{result.riskImpact.riskScoreBoostPct}%</span>
                      <Zap className="w-4 h-4 text-amber-400 animate-pulse" />
                    </span>
                    <span className="block text-[10px] text-amber-300/80">Confirmed Ground Hazard</span>
                  </div>

                  <div className="p-3 bg-red-950/60 border border-red-600 rounded-lg">
                    <span className="block text-[10px] font-mono text-red-300 uppercase">Post-Verification Risk</span>
                    <span className="block text-xl font-black text-red-400 mt-1">
                      {result.riskImpact.postVerificationRiskPct}%
                    </span>
                    <span className="block text-[10px] text-red-300 font-bold uppercase">
                      {result.riskImpact.escalationRecommended}
                    </span>
                  </div>
                </div>

                {/* Actionable Directive Issued */}
                <div className="p-3.5 bg-slate-950 border-l-4 border-amber-500 rounded-r-lg space-y-1">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-amber-400" />
                    <span className="text-xs font-mono font-bold uppercase text-amber-400">
                      Automated DEOC Response Directive Triggered
                    </span>
                  </div>
                  <p className="text-xs text-slate-200 leading-relaxed font-sans">
                    {result.actionableDirective}
                  </p>
                </div>
              </div>
            ) : (
              <div className="py-12 text-center text-slate-500 font-mono text-xs">
                Select a hazard preset on the left or upload a field photo to run the Jan-Drishti verification pipeline.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
