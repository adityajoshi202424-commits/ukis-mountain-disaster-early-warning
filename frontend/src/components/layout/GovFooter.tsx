'use client';

import React from 'react';
import Link from 'next/link';
import { ShieldCheck, PhoneCall, ExternalLink } from 'lucide-react';

export function GovFooter() {
  return (
    <footer className="bg-slate-100 border-t border-slate-300 text-slate-600 text-xs mt-auto">
      {/* 4px Official Indian Tricolor Ribbon */}
      <div className="h-1 w-full bg-gradient-to-r from-[#FF9933] via-[#FFFFFF] to-[#138808]" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8 grid grid-cols-1 md:grid-cols-4 gap-6">
        {/* Col 1: Government Identity */}
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-slate-900 font-extrabold text-sm">
            <span>🇮🇳</span>
            <span>DMMC &bull; Govt. of Uttarakhand</span>
          </div>
          <p className="text-slate-600 leading-relaxed text-[11px]">
            Disaster Mitigation and Management Centre (DMMC), Secretariat, Subhash Road, Dehradun, Uttarakhand 248001.
          </p>
          <div className="text-[11px] text-emerald-800 font-bold flex items-center gap-1.5 pt-1">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-700" />
            <span>NDMA &bull; USDMA Official Architecture</span>
          </div>
        </div>

        {/* Col 2: Citizen Navigation */}
        <div className="space-y-2 text-[11px]">
          <span className="text-slate-900 font-bold block uppercase tracking-wider text-xs">
            Public Services
          </span>
          <div>
            <Link href="/" className="hover:text-blue-700 font-medium">
              Active Alerts &amp; Warnings
            </Link>
          </div>
          <div>
            <Link href="/shelters" className="hover:text-blue-700 font-medium">
              Live Shelters &amp; High-Ground Map
            </Link>
          </div>
          <div>
            <Link href="/guidebook" className="hover:text-blue-700 font-medium">
              Emergency Survival Guidebook
            </Link>
          </div>
          <div>
            <Link href="/him-kavach" className="hover:text-blue-700 font-bold text-indigo-900">
              🛡️ HIM-KAVACH XAI Platform (UKIS)
            </Link>
          </div>
          <div>
            <Link href="/admin" className="text-slate-500 hover:text-slate-800">
              DMMC Staff Control Room (Restricted)
            </Link>
          </div>
        </div>

        {/* Col 3: Institutional Data Providers */}
        <div className="space-y-1.5 text-[11px]">
          <span className="text-slate-900 font-bold block uppercase tracking-wider text-xs mb-2">
            Sensor Data Feeds
          </span>
          <p className="text-slate-600">Central Water Commission (CWC Gauges)</p>
          <p className="text-slate-600">India Meteorological Department (IMD)</p>
          <p className="text-slate-600">IIT Roorkee Seismic Telemetry</p>
          <p className="text-slate-600">DGRE Avalanche Warning System</p>
          <p className="text-slate-600">ISRO NRSC Bhuvan Spatial Services</p>
        </div>

        {/* Col 4: 24x7 Helplines & Compliance */}
        <div className="space-y-2">
          <span className="text-slate-900 font-bold block uppercase tracking-wider text-xs">
            24x7 Emergency Helplines
          </span>
          <div className="p-3 bg-white border border-slate-200 rounded-md space-y-1.5 font-mono text-xs">
            <div className="flex justify-between">
              <span className="text-slate-600">Police &amp; Emergency:</span>
              <strong className="text-red-700">112</strong>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-600">State Control (SEOC):</span>
              <strong className="text-slate-900">1070</strong>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-600">District Ops (DEOC):</span>
              <strong className="text-slate-900">1077</strong>
            </div>
          </div>

          <div className="flex flex-wrap gap-1.5 pt-1 text-[10px] font-mono">
            <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-900 border border-emerald-300 font-bold">
              ✓ GIGW 3.0 Validated
            </span>
            <span className="px-2 py-0.5 rounded bg-blue-100 text-blue-900 border border-blue-300 font-bold">
              ✓ STQC Audited
            </span>
          </div>
        </div>
      </div>

      <div className="border-t border-slate-200 py-3 text-center text-[11px] text-slate-500 bg-slate-200/50 space-y-0.5">
        <div>
          &copy; 2026 Disaster Mitigation and Management Centre (DMMC), Government of Uttarakhand. Developed in accordance with GIGW 3.0, NDMA and DPDP Act 2023 guidelines.
        </div>
        <div className="text-[10px] text-slate-400">
          Hosted at UKSDC (ITDA Dehradun) with Active-Active Failover on MeghRaj GI Cloud (NIC National Data Centre).
        </div>
      </div>
    </footer>
  );
}
