'use client';

import React, { useState, useEffect } from 'react';
import { Cpu, ShieldCheck, AlertTriangle, Clock, Radio, CheckCircle2, XCircle, Volume2, FileCode, Play, RotateCcw } from 'lucide-react';

export function AiDetectionPipelineModule() {
  const [activeStep, setActiveStep] = useState<number>(1);
  const [antiAlarmToggle, setAntiAlarmToggle] = useState<'GLITCH' | 'CORROBORATED'>('GLITCH');
  const [hitlTimerSeconds, setHitlTimerSeconds] = useState<number>(180);
  const [hitlTimerRunning, setHitlTimerRunning] = useState<boolean>(true);
  const [officerApproved, setOfficerApproved] = useState<boolean>(false);
  const [capXmlOpen, setCapXmlOpen] = useState<boolean>(false);

  // 3-Minute (180s) Auto-Escalation Countdown
  useEffect(() => {
    let interval: any = null;
    if (hitlTimerRunning && hitlTimerSeconds > 0 && !officerApproved) {
      interval = setInterval(() => {
        setHitlTimerSeconds((prev) => prev - 1);
      }, 1000);
    } else if (hitlTimerSeconds === 0 && !officerApproved) {
      // Auto-escalated to sirens
    }
    return () => clearInterval(interval);
  }, [hitlTimerRunning, hitlTimerSeconds, officerApproved]);

  const resetTimer = () => {
    setHitlTimerSeconds(180);
    setOfficerApproved(false);
    setHitlTimerRunning(true);
  };

  const sampleCapXml = `<?xml version="1.0" encoding="UTF-8"?>
<alert xmlns="urn:oasis:names:tc:emergency:cap:1.2">
  <identifier>IN-UK-USDMA-GLOF-CHAMOLI-${Date.now()}</identifier>
  <sender>seoc.dehradun@uk.gov.in</sender>
  <sent>${new Date().toISOString()}</sent>
  <status>Actual</status>
  <msgType>Alert</msgType>
  <scope>Public</scope>
  <info>
    <category>Geo</category>
    <event>Glacial Lake Outburst Flood (GLOF) &amp; Flash Flood</event>
    <urgency>Immediate</urgency>
    <severity>Extreme</severity>
    <certainty>Observed</certainty>
    <headline>RED ALERT: Vasundhara Tal Glacial Breach - Evacuate Alaknanda Riverbed</headline>
    <description>1,450 m³/s surge bore traveling downstream at 8.5 m/s. Wave ETA to Tapovan is 28 minutes.</description>
    <instruction>Immediately move to permanent high-ground shelters. Do not approach riverbanks. Dial 112 for rescue.</instruction>
    <area>
      <areaDesc>Chamoli Micro-Watersheds: Mana, Badrinath, Tapovan, Joshimath Marwari</areaDesc>
      <circle>30.795,79.435,12.0</circle>
    </area>
  </info>
</alert>`;

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-rose-950/40 to-slate-900 border border-rose-500/40 rounded-xl p-5 shadow-lg">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="p-1.5 rounded-lg bg-rose-500/20 text-rose-400 border border-rose-400/30">
                <Cpu className="w-5 h-5" />
              </span>
              <h3 className="text-lg font-black text-white tracking-tight flex items-center gap-2">
                <span>AI पहचान-से-अधिसूचना संपूर्ण पाइपलाइन (Detection-to-Notification Workflow)</span>
                <span className="text-xs font-mono font-bold bg-rose-600/40 text-rose-300 border border-rose-500/50 px-2 py-0.5 rounded">
                  NDMA &amp; USDMA SOP Compliant
                </span>
              </h3>
            </div>
            <p className="text-xs sm:text-sm text-slate-300 max-w-3xl leading-relaxed">
              Step-by-step engineering pipeline demonstrating how the AI detects multi-hazard disasters, filters broken sensor false alarms via cross-validation, enforces a **3-Minute Human-in-the-Loop (HITL) Auto-Escalation Window**, and pushes standardized **OASIS CAP v1.2** XML packets across all channels.
            </p>
          </div>

          <div className="flex items-center gap-1.5 bg-slate-950 border border-slate-800 p-1 rounded-lg text-xs font-mono">
            {[1, 2, 3, 4, 5].map((step) => (
              <button
                key={step}
                onClick={() => setActiveStep(step)}
                className={`px-3 py-1 rounded transition-all font-bold ${
                  activeStep === step ? 'bg-rose-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'
                }`}
              >
                Step {step}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Pipeline 5-Step Visual Stepper Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
        {[
          {
            num: 1,
            title: '1. Ingestion',
            sub: 'Telemetry Streams',
            desc: 'IMD Doppler dBZ + CWC Acoustic Gauges + Piezometers',
          },
          {
            num: 2,
            title: '2. Inference',
            sub: 'Two-Stage AI',
            desc: 'XGBoost Susceptibility + LSTM Temporal Surge Model',
          },
          {
            num: 3,
            title: '3. Anti-Panic',
            sub: 'Cross-Validation',
            desc: 'Neighbor Sensor & Radar checks filter broken telemetry',
          },
          {
            num: 4,
            title: '4. HITL 3-Min',
            sub: 'Escalation Timer',
            desc: 'Duty Officer approval window before siren auto-fire',
          },
          {
            num: 5,
            title: '5. Multi-CAP',
            sub: 'Omni-Channel Broadcast',
            desc: 'CBS 4370 + IVR Audio Calls + LoRaWAN 120dB Sirens',
          },
        ].map((item) => (
          <button
            key={item.num}
            onClick={() => setActiveStep(item.num)}
            className={`p-3.5 rounded-xl border text-left transition-all ${
              activeStep === item.num
                ? 'bg-rose-950/60 border-rose-500 text-white ring-1 ring-rose-400 shadow-md'
                : 'bg-slate-900 border-slate-800 text-slate-300 hover:bg-slate-850'
            }`}
          >
            <div className="text-[10px] font-mono font-bold text-rose-400">0{item.num} PIPELINE</div>
            <div className="text-xs font-bold text-white mt-0.5">{item.title}</div>
            <div className="text-[10px] font-mono text-slate-400">{item.sub}</div>
            <div className="text-[10px] text-slate-500 mt-1 line-clamp-2">{item.desc}</div>
          </button>
        ))}
      </div>

      {/* Step Inspector Detail Panes */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl space-y-6">
        {activeStep === 1 && (
          <div className="space-y-4">
            <h4 className="text-sm font-bold text-white flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-rose-500 animate-ping" />
              <span>Step 1: Multi-Stream Continuous Anomaly Ingestion (Every 5–15 Minutes)</span>
            </h4>
            <p className="text-xs text-slate-300 leading-relaxed max-w-3xl">
              The backend continuously aggregates multi-source mountain telemetry from autonomous ground IoT stations and airborne remote sensing:
            </p>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-3 font-mono text-xs">
              <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg space-y-1">
                <span className="text-[10px] text-rose-400 uppercase">IMD Doppler Radar</span>
                <span className="block text-sm font-bold text-white">48.5 dBZ Reflectivity</span>
                <span className="text-[10px] text-slate-500">Cloudburst convective cell detected</span>
              </div>
              <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg space-y-1">
                <span className="text-[10px] text-rose-400 uppercase">CWC Acoustic Gauge</span>
                <span className="block text-sm font-bold text-white">+1.65 m/hr River Surge</span>
                <span className="text-[10px] text-slate-500">Alaknanda gauge rate of rise</span>
              </div>
              <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg space-y-1">
                <span className="text-[10px] text-rose-400 uppercase">Ground Piezometer</span>
                <span className="block text-sm font-bold text-white">185 kPa Pore Pressure</span>
                <span className="text-[10px] text-slate-500">Hydrostatic saturation in Joshimath</span>
              </div>
              <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg space-y-1">
                <span className="text-[10px] text-rose-400 uppercase">Biaxial Tiltmeter</span>
                <span className="block text-sm font-bold text-white">4.2 mm/hr Creep Rate</span>
                <span className="text-[10px] text-slate-500">Toe-slope shear displacement</span>
              </div>
            </div>
          </div>
        )}

        {activeStep === 2 && (
          <div className="space-y-4">
            <h4 className="text-sm font-bold text-white">
              Step 2: Two-Stage AI Ensemble Inference (Spatial Susceptibility + Temporal Surge)
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
              <div className="p-4 bg-slate-950 border border-slate-800 rounded-xl space-y-2">
                <span className="text-amber-400 font-bold block uppercase">
                  Model 1: Spatial Susceptibility (XGBoost + TreeSHAP)
                </span>
                <p className="text-slate-300 font-sans leading-relaxed text-xs">
                  Evaluates static 30m DEM slope gradients, proximity to the Main Central Thrust (MCT) fault line, Topographic Wetness Index (TWI), and 72-hour antecedent soil moisture to establish baseline failure probability (0–100%).
                </p>
                <div className="p-2.5 bg-slate-900 rounded border border-slate-800 text-[11px] text-slate-300">
                  Current Model 1 Baseline Score: <strong className="text-amber-400">78% Susceptibility</strong>
                </div>
              </div>

              <div className="p-4 bg-slate-950 border border-slate-800 rounded-xl space-y-2">
                <span className="text-sky-400 font-bold block uppercase">
                  Model 2: Temporal Surge (Bi-Directional LSTM)
                </span>
                <p className="text-slate-300 font-sans leading-relaxed text-xs">
                  Processes live 15-minute sliding windows of upstream rainfall velocity, radar dBZ delta, and river hydrographs. Triggers temporal breach alert if rate-of-rise exceeds 0.5m in 15 minutes.
                </p>
                <div className="p-2.5 bg-slate-900 rounded border border-slate-800 text-[11px] text-slate-300">
                  Current Model 2 Temporal Trend: <strong className="text-sky-400">1.65 m/hr Rapid Surge</strong>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeStep === 3 && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-bold text-white flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span>Step 3: Anti-False-Alarm Cross-Validation Gate (Prevents Public Panic)</span>
              </h4>
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-400 font-mono">Test Scenario:</span>
                <button
                  onClick={() => setAntiAlarmToggle('GLITCH')}
                  className={`px-3 py-1 rounded text-xs font-mono font-bold ${
                    antiAlarmToggle === 'GLITCH' ? 'bg-amber-600 text-white' : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  Isolated Sensor Spike (Glitch)
                </button>
                <button
                  onClick={() => setAntiAlarmToggle('CORROBORATED')}
                  className={`px-3 py-1 rounded text-xs font-mono font-bold ${
                    antiAlarmToggle === 'CORROBORATED' ? 'bg-rose-600 text-white' : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  Corroborated Multi-Sensor Surge
                </button>
              </div>
            </div>

            {antiAlarmToggle === 'GLITCH' ? (
              <div className="p-4 bg-amber-950/30 border border-amber-600/50 rounded-xl space-y-2">
                <div className="flex items-center gap-2 text-amber-400 font-bold text-xs font-mono">
                  <AlertTriangle className="w-4 h-4" />
                  <span>ANTI-FALSE-ALARM FILTER ACTIVATED: ISOLATED TILETMETER 99% ANOMALY</span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed font-sans">
                  Tiltmeter #UK-TILT-04 spiked to 99% slope creep. The AI checked adjacent sensors: Rainfall = 0.0mm, Piezometer = Nominal, River acoustic = Normal. <strong>Action: Suppressed public disaster alert.</strong> Auto-created <em>ITDA Maintenance Ticket #ITDA-HW-9021</em> for field technician inspection without causing pilgrim panic.
                </p>
                <div className="text-[11px] font-mono text-emerald-400 bg-slate-950 p-2 rounded border border-slate-800">
                  ✓ Result: 0% False Evacuation Orders Issued &bull; Highway Traffic Remains Open
                </div>
              </div>
            ) : (
              <div className="p-4 bg-red-950/40 border border-red-600 rounded-xl space-y-2">
                <div className="flex items-center gap-2 text-red-400 font-bold text-xs font-mono">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>MULTI-CORROBORATED HAZARD TRIGGER CONFIRMED</span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed font-sans">
                  Tiltmeter #UK-TILT-04 (4.2 mm/hr) is corroborated by 48 dBZ Radar rainfall (65mm/hr) and CWC River Gauge (+1.65 m/hr). Confidence Score: <strong>96.8%</strong>. Event promoted to <strong>Confirmed Hazard Trigger</strong> for SEOC Duty Officer escalation.
                </p>
              </div>
            )}
          </div>
        )}

        {activeStep === 4 && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-bold text-white flex items-center gap-2">
                <Clock className="w-4 h-4 text-amber-400" />
                <span>Step 4: Tiered Escalation &amp; 3-Minute Human-in-the-Loop (HITL) Window</span>
              </h4>
              <button
                onClick={resetTimer}
                className="text-xs font-mono text-slate-400 hover:text-white flex items-center gap-1"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Reset 180s Timer</span>
              </button>
            </div>

            {/* 3-Minute Live Auto-Escalation Countdown */}
            <div className="p-4 bg-slate-950 border border-slate-800 rounded-xl space-y-3">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-slate-400">SEOC Video Wall Mandatory Approval Timer:</span>
                <span className="text-base font-black font-mono text-amber-400">
                  {Math.floor(hitlTimerSeconds / 60)}:{(hitlTimerSeconds % 60).toString().padStart(2, '0')} remaining
                </span>
              </div>

              {/* Progress Bar */}
              <div className="w-full h-3 bg-slate-900 rounded-full overflow-hidden p-0.5 border border-slate-800">
                <div
                  className={`h-full rounded-full transition-all duration-1000 ${
                    hitlTimerSeconds > 60 ? 'bg-amber-500' : 'bg-red-600 animate-pulse'
                  }`}
                  style={{ width: `${(hitlTimerSeconds / 180) * 100}%` }}
                />
              </div>

              <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
                <div className="text-xs text-slate-300 font-sans max-w-xl">
                  {officerApproved ? (
                    <span className="text-emerald-400 font-bold flex items-center gap-1.5">
                      <CheckCircle2 className="w-4 h-4" />
                      SEOC Duty Officer Authorized Dispatch at {new Date().toLocaleTimeString()}
                    </span>
                  ) : hitlTimerSeconds === 0 ? (
                    <span className="text-red-400 font-bold flex items-center gap-1.5 animate-pulse">
                      <AlertTriangle className="w-4 h-4" />
                      180s Expired! Automated Safety Fail-Safe Triggered: Alpine Valley Sirens Fired Autonomously!
                    </span>
                  ) : (
                    <span>
                      If duty officer does not acknowledge or approve within 180 seconds, system automatically sounds river sirens to protect lives.
                    </span>
                  )}
                </div>

                {!officerApproved && hitlTimerSeconds > 0 && (
                  <button
                    onClick={() => {
                      setOfficerApproved(true);
                      setHitlTimerRunning(false);
                    }}
                    className="px-4 py-2 bg-red-700 hover:bg-red-800 text-white font-bold text-xs uppercase rounded-lg shadow-lg transition"
                  >
                    Approve &amp; Broadcast CAP v1.2 Payload
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {activeStep === 5 && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-bold text-white flex items-center gap-2">
                <Radio className="w-4 h-4 text-emerald-400" />
                <span>Step 5: Multi-Channel Common Alerting Protocol (CAP v1.2) Broadcast</span>
              </h4>
              <button
                onClick={() => setCapXmlOpen(!capXmlOpen)}
                className="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-xs font-mono flex items-center gap-1.5 border border-slate-700"
              >
                <FileCode className="w-3.5 h-3.5 text-amber-400" />
                <span>{capXmlOpen ? 'Hide CAP XML' : 'View OASIS CAP v1.2 XML'}</span>
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-slate-950 border border-slate-800 rounded-xl space-y-2">
                <span className="text-xs font-bold text-white flex items-center gap-1.5">
                  <Radio className="w-4 h-4 text-red-500 animate-pulse" />
                  <span>1. NDMA SACHET / CBS 4370</span>
                </span>
                <p className="text-[11px] text-slate-400 leading-snug">
                  Zero-data cell-tower emergency ringtone override dispatched to all active Android &amp; iOS devices inside the Chamoli geofence in Hindi and English.
                </p>
                <div className="text-[10px] font-mono text-emerald-400">Status: Dispatched (48,200 devices)</div>
              </div>

              <div className="p-4 bg-slate-950 border border-slate-800 rounded-xl space-y-2">
                <span className="text-xs font-bold text-white flex items-center gap-1.5">
                  <Volume2 className="w-4 h-4 text-amber-400" />
                  <span>2. Automated Multilingual IVR</span>
                </span>
                <p className="text-[11px] text-slate-400 leading-snug">
                  Pre-recorded Text-to-Speech voice telephone calls dialed to Gram Pradhans and Apda Mitras in <strong>Hindi, Garhwali, and Kumaoni</strong> dialects.
                </p>
                <div className="text-[10px] font-mono text-emerald-400">Status: Dialing 84 Nodal Officials</div>
              </div>

              <div className="p-4 bg-slate-950 border border-slate-800 rounded-xl space-y-2">
                <span className="text-xs font-bold text-white flex items-center gap-1.5">
                  <AlertTriangle className="w-4 h-4 text-rose-400" />
                  <span>3. LoRaWAN / VSAT Sirens</span>
                </span>
                <p className="text-[11px] text-slate-400 leading-snug">
                  Hardware RF signal actuated to solar-backed 120dB acoustic sirens along riverbanks at Tapovan, Joshimath, and Karnaprayag.
                </p>
                <div className="text-[10px] font-mono text-emerald-400">Status: 24 Sirens Warbling</div>
              </div>
            </div>

            {capXmlOpen && (
              <div className="p-3 bg-slate-950 border border-slate-800 rounded-xl overflow-x-auto text-[11px] font-mono text-emerald-300">
                <pre>{sampleCapXml}</pre>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
