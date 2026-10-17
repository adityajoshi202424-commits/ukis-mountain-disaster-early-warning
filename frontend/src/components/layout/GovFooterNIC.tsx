'use client';

import React from 'react';
import Link from 'next/link';
import { ShieldCheck, PhoneCall, Mail, MapPin, ExternalLink, Globe } from 'lucide-react';

export function GovFooterNIC() {
  return (
    <footer className="bg-[#0B1E2E] text-slate-300 font-sans text-xs border-t-2 border-[#0B3C5D]">
      {/* Top 3px Tricolor Line */}
      <div className="tricolor-ribbon" />

      {/* Main 3-Column Governance Footer Block */}
      <div className="max-w-7xl mx-auto px-4 lg:px-8 py-10 grid grid-cols-1 md:grid-cols-3 gap-8">
        
        {/* ========================================================================= */}
        {/* COLUMN 1: OFFICIAL OFFICE ADDRESS & CONTACT HELPLINES                     */}
        {/* ========================================================================= */}
        <div className="space-y-3">
          <div className="flex items-center gap-2 text-white font-bold text-sm border-b border-slate-700/80 pb-2">
            <span>🇮🇳</span>
            <span>NATIONAL DISASTER MANAGEMENT AUTHORITY</span>
          </div>

          <div className="space-y-2 text-slate-300 text-xs">
            <div className="flex items-start gap-2">
              <MapPin className="w-4 h-4 text-[#FF9933] shrink-0 mt-0.5" />
              <span>
                NDMA Bhawan, A-1, Safdarjung Enclave,<br />
                New Delhi - 110029, India
              </span>
            </div>

            <div className="flex items-center gap-2">
              <PhoneCall className="w-4 h-4 text-[#FF9933] shrink-0" />
              <span>
                Control Room: <strong>1078</strong> | +91-11-26701728
              </span>
            </div>

            <div className="flex items-center gap-2">
              <Mail className="w-4 h-4 text-[#FF9933] shrink-0" />
              <span>Email: controlroom@ndma.gov.in</span>
            </div>
          </div>

          <div className="text-[11px] text-emerald-400 flex items-center gap-1.5 pt-1">
            <ShieldCheck className="w-4 h-4" />
            <span>GIGW 3.0 &amp; MeitY Guidelines Compliant</span>
          </div>
        </div>

        {/* ========================================================================= */}
        {/* COLUMN 2: CORE GOVERNMENT WEB FRAMEWORK POLICIES & LINKS                  */}
        {/* ========================================================================= */}
        <div className="space-y-3">
          <div className="text-white font-bold text-sm border-b border-slate-700/80 pb-2 uppercase tracking-wide">
            POLICIES &amp; MANDATORY DISCLOSURES
          </div>

          <ul className="space-y-1.5 text-xs text-slate-300">
            <li>
              <Link href="/" className="hover:text-sky-300 transition-colors flex items-center gap-1.5">
                <span>&bull;</span> Terms of Use &amp; Conditions
              </Link>
            </li>
            <li>
              <Link href="/" className="hover:text-sky-300 transition-colors flex items-center gap-1.5">
                <span>&bull;</span> Privacy &amp; Data Protection Policy
              </Link>
            </li>
            <li>
              <Link href="/" className="hover:text-sky-300 transition-colors flex items-center gap-1.5">
                <span>&bull;</span> Hyperlinking Policy
              </Link>
            </li>
            <li>
              <Link href="/" className="hover:text-sky-300 transition-colors flex items-center gap-1.5">
                <span>&bull;</span> Copyright Policy
              </Link>
            </li>
            <li>
              <Link href="/" className="hover:text-sky-300 transition-colors flex items-center gap-1.5">
                <span>&bull;</span> Accessibility Statement &amp; GIGW 3.0 Compliance
              </Link>
            </li>
            <li>
              <Link href="/" className="hover:text-sky-300 transition-colors flex items-center gap-1.5">
                <span>&bull;</span> Help &amp; Comprehensive Sitemap
              </Link>
            </li>
          </ul>
        </div>

        {/* ========================================================================= */}
        {/* COLUMN 3: OFFICIAL TECHNICAL CREDIT & NIC HOSTING SEAL                   */}
        {/* ========================================================================= */}
        <div className="space-y-3">
          <div className="text-white font-bold text-sm border-b border-slate-700/80 pb-2 uppercase tracking-wide">
            NATIONAL INFORMATICS CENTRE (NIC)
          </div>

          <p className="text-xs text-slate-300 leading-relaxed">
            Website designed, developed and hosted by <strong>National Informatics Centre (NIC)</strong>, Ministry of Electronics &amp; Information Technology, Government of India.
          </p>

          <div className="p-3 bg-[#071522] border border-slate-700 rounded text-[11px] space-y-1 font-mono text-slate-400">
            <div>Content Owned &amp; Maintained by: <strong className="text-white">NDMA</strong></div>
            <div>Problem Statement: <strong className="text-sky-300">Smart India Hackathon #192</strong></div>
            <div>Last Reviewed &amp; Updated: <strong className="text-amber-300">31-Aug-2026</strong></div>
          </div>
        </div>

      </div>

      {/* Bottom Copyright Strip */}
      <div className="bg-[#06121D] py-3 px-4 lg:px-8 border-t border-slate-800 text-[11px] text-slate-400 flex flex-wrap items-center justify-between gap-2 font-mono">
        <div>
          &copy; {new Date().getFullYear()} National Disaster Management Authority (NDMA). All Rights Reserved.
        </div>
        <div>
          Official Portal of National Disaster Management Authority, Government of India
        </div>
      </div>
    </footer>
  );
}
export default GovFooterNIC;
