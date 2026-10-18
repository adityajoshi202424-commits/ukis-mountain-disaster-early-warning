'use client';

import React, { useState, useEffect } from 'react';
import { Server, Database, Shield, Zap, RefreshCw, AlertTriangle, CheckCircle2, ArrowRight, Radio, Cloud } from 'lucide-react';

export function FailoverArchitectureModule() {
  const [simulateCut, setSimulateCut] = useState(false);
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const fetchStatus = async (cut = simulateCut) => {
    setLoading(true);
    try {
      const res = await fetch(`/api/v1/failover/status?simulate_cut=${cut}`);
      if (res.ok) {
        const d = await res.json();
        setData(d);
      }
    } catch (err) {
      console.error('Failed to load failover telemetry', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, [simulateCut]);

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-emerald-950/40 to-slate-900 border border-emerald-500/40 rounded-xl p-5 shadow-lg">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="p-1.5 rounded-lg bg-emerald-500/20 text-emerald-400 border border-emerald-400/30">
                <Server className="w-5 h-5" />
              </span>
              <h3 className="text-lg font-black text-white tracking-tight flex items-center gap-2">
                <span>गेटवे, सर्वर एवं डेटाबेस शून्य-डाउनटाइम फेकलओवर आर्किटेक्चर</span>
                <span className="text-xs font-mono font-bold bg-emerald-600/40 text-emerald-300 border border-emerald-500/50 px-2 py-0.5 rounded">
                  UKSDC + MeghRaj Active-Active DR
                </span>
              </h3>
            </div>
            <p className="text-xs sm:text-sm text-slate-300 max-w-3xl leading-relaxed">
              Designed for catastrophic Himalayan conditions when valley optical fiber severs and public traffic spikes 100x. Operates an **Active-Active Multi-Region Grid** between the **Uttarakhand State Data Centre (UKSDC ITDA Dehradun)** and **GI Cloud MeghRaj (NIC National Data Centre)** with automatic Patroni + etcd failover achieving an <strong className="text-emerald-400">RTO &lt; 10s</strong> and <strong className="text-emerald-400">RPO = 0</strong>.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setSimulateCut(!simulateCut)}
              className={`px-3 py-2 rounded-lg font-mono text-xs font-bold transition flex items-center gap-1.5 border ${
                simulateCut
                  ? 'bg-rose-600 hover:bg-rose-700 text-white border-rose-400 shadow-md animate-pulse'
                  : 'bg-slate-800 hover:bg-slate-700 text-emerald-300 border-emerald-500/40'
              }`}
            >
              <AlertTriangle className="w-4 h-4" />
              <span>{simulateCut ? 'Severance Active: MeghRaj DR Live' : 'Simulate UKSDC Fiber Severance'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Target Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-1">
          <span className="text-[10px] font-mono uppercase text-slate-400">Recovery Time Objective (RTO)</span>
          <div className="text-2xl font-black text-emerald-400 font-mono">&lt; 10s</div>
          <span className="text-[10px] text-slate-500 font-mono">BGP Anycast Cloud DNS switchover</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-1">
          <span className="text-[10px] font-mono uppercase text-slate-400">Recovery Point Objective (RPO)</span>
          <div className="text-2xl font-black text-emerald-400 font-mono">0 sec</div>
          <span className="text-[10px] text-slate-500 font-mono">Synchronous PostgreSQL streaming</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-1">
          <span className="text-[10px] font-mono uppercase text-slate-400">Public CDN Edge Caching</span>
          <div className="text-2xl font-black text-sky-400 font-mono">98.4%</div>
          <span className="text-[10px] text-slate-500 font-mono">5M citizens cannot stall SEOC servers</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-1">
          <span className="text-[10px] font-mono uppercase text-slate-400">Database Consensus Engine</span>
          <div className="text-xs font-mono font-bold text-amber-400 bg-amber-950/80 border border-amber-500/40 px-2 py-1.5 rounded mt-1">
            Patroni 3.2 + etcd RAFT
          </div>
          <span className="text-[10px] text-slate-500 font-mono">Zero split-brain guarantee</span>
        </div>
      </div>

      {/* 3 Core Architecture Pillars: Ingestion, Compute, Database */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 1. IoT Ingestion Gateway Failover */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
            <Radio className="w-4 h-4 text-emerald-400" />
            <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-white">
              1. Sensor Ingestion Failover Matrix
            </h4>
          </div>

          <div className="space-y-3 font-mono text-xs">
            <div className={`p-3 rounded-lg border ${simulateCut ? 'bg-red-950/40 border-red-800 text-red-300' : 'bg-slate-950 border-slate-800 text-slate-300'}`}>
              <div className="flex items-center justify-between">
                <span className="font-bold">PRIMARY: 4G/5G MQTT + SWAN</span>
                <span className={`text-[10px] px-1.5 py-0.2 rounded font-bold ${simulateCut ? 'bg-red-800 text-white' : 'bg-emerald-950 text-emerald-400'}`}>
                  {simulateCut ? 'FIBER SEVERED' : 'ONLINE (24ms)'}
                </span>
              </div>
              <p className="text-[11px] text-slate-400 mt-1 font-sans">
                High-speed valley cellular telemetry through state wide area network.
              </p>
            </div>

            <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg text-slate-300">
              <div className="flex items-center justify-between">
                <span className="font-bold text-emerald-300">FAILOVER 1: LoRaWAN MESH</span>
                <span className="text-[10px] bg-emerald-950 text-emerald-400 border border-emerald-500/40 px-1.5 py-0.2 rounded font-bold">
                  ACTIVE (140ms)
                </span>
              </div>
              <p className="text-[11px] text-slate-400 mt-1 font-sans">
                Peer-to-peer valley sensors relay packets to hilltop solar gateway outside slide zone.
              </p>
            </div>

            <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg text-slate-300">
              <div className="flex items-center justify-between">
                <span className="font-bold text-sky-300">FAILOVER 2: ISRO INSAT-3DR VSAT</span>
                <span className="text-[10px] bg-sky-950 text-sky-400 border border-sky-500/40 px-1.5 py-0.2 rounded font-bold">
                  HOT STANDBY (0% Loss)
                </span>
              </div>
              <p className="text-[11px] text-slate-400 mt-1 font-sans">
                Direct satellite burst telemetry for high-altitude GLOF glacial lakes (Vasundhara Tal).
              </p>
            </div>
          </div>
        </div>

        {/* 2. Server & Compute Failover */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
            <Cloud className="w-4 h-4 text-sky-400" />
            <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-white">
              2. Server &amp; Compute Failover
            </h4>
          </div>

          <div className="space-y-3 font-mono text-xs">
            <div className={`p-3 rounded-lg border ${simulateCut ? 'bg-red-950/40 border-red-800 text-red-300' : 'bg-slate-950 border-slate-800 text-slate-300'}`}>
              <div className="flex items-center justify-between">
                <span className="font-bold">PRIMARY: UKSDC ITDA Dehradun</span>
                <span className={`text-[10px] px-1.5 py-0.2 rounded font-bold ${simulateCut ? 'bg-red-800 text-white' : 'bg-emerald-950 text-emerald-400'}`}>
                  {simulateCut ? 'DISCONNECTED' : 'PRIMARY ACTIVE'}
                </span>
              </div>
              <p className="text-[11px] text-slate-400 mt-1 font-sans">
                Seismic Zone IV facility. Runs internal SEOC 1070 video wall and AI inference.
              </p>
            </div>

            <div className={`p-3 rounded-lg border ${simulateCut ? 'bg-emerald-950/60 border-emerald-500 text-emerald-300 ring-1 ring-emerald-400' : 'bg-slate-950 border-slate-800 text-slate-300'}`}>
              <div className="flex items-center justify-between">
                <span className="font-bold">DR NODE: GI Cloud (MeghRaj NIC)</span>
                <span className={`text-[10px] px-1.5 py-0.2 rounded font-bold ${simulateCut ? 'bg-emerald-600 text-white animate-pulse' : 'bg-slate-800 text-slate-400'}`}>
                  {simulateCut ? 'PROMOTED TO MASTER' : 'HOT STANDBY SYNC'}
                </span>
              </div>
              <p className="text-[11px] text-slate-400 mt-1 font-sans">
                National Data Centre (Delhi/Hyderabad). Geographically dispersed in Seismic Zone II.
              </p>
            </div>

            <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg text-slate-300">
              <div className="flex items-center justify-between">
                <span className="font-bold text-amber-300">EDGE CDN ISOLATION</span>
                <span className="text-[10px] bg-amber-950 text-amber-400 border border-amber-500/40 px-1.5 py-0.2 rounded font-bold">
                  ACTIVE (98.4% Hit)
                </span>
              </div>
              <p className="text-[11px] text-slate-400 mt-1 font-sans">
                Public website is cached at edge; high public traffic cannot slow down SEOC dispatch.
              </p>
            </div>
          </div>
        </div>

        {/* 3. Database High-Availability */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
            <Database className="w-4 h-4 text-amber-400" />
            <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-white">
              3. Distributed Database HA
            </h4>
          </div>

          <div className="space-y-3 font-mono text-xs">
            <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg text-slate-300 space-y-1">
              <div className="text-[10px] text-amber-400 uppercase font-bold">PostgreSQL 16 + PostGIS</div>
              <div className="text-xs text-white font-bold">
                {simulateCut ? 'MeghRaj Standby Promoted to Master' : 'UKSDC Dehradun (Primary Master)'}
              </div>
              <p className="text-[11px] text-slate-400 font-sans">
                Managed by Patroni with etcd consensus. Synchronous streaming replication.
              </p>
            </div>

            <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg text-slate-300 space-y-1">
              <div className="text-[10px] text-amber-400 uppercase font-bold">TimescaleDB Hyper-Tables</div>
              <div className="text-xs text-white font-bold">Hourly Automated Telemetry Chunks</div>
              <p className="text-[11px] text-slate-400 font-sans">
                High-frequency rainfall and river gauge writes never lock geospatial query tables.
              </p>
            </div>

            <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg text-slate-300 space-y-1">
              <div className="text-[10px] text-amber-400 uppercase font-bold">PgBouncer Connection Pooling</div>
              <div className="text-xs text-white font-bold">5,000 Concurrent Officer &amp; Sensor Pools</div>
              <p className="text-[11px] text-slate-400 font-sans">
                Transaction pooling prevents database connection starvation during disaster surges.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
