'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  Home, 
  Map, 
  BarChart3, 
  Waves, 
  Radio, 
  Building2, 
  ShieldCheck, 
  PhoneCall, 
  Globe2, 
  Volume2, 
  Type, 
  Search,
  ExternalLink,
  ChevronDown
} from 'lucide-react';
import { GlobalSearchBar } from './GlobalSearchBar';

interface GovHeaderNICProps {
  onOpenSources?: () => void;
}

export function GovHeaderNIC({ onOpenSources }: GovHeaderNICProps) {
  const pathname = usePathname();
  const [fontSizeOffset, setFontSizeOffset] = useState(0);
  const [selectedLanguage, setSelectedLanguage] = useState('English');

  const navMenuItems = [
    { href: '/', label: 'HOME (SITUATION ROOM)', exact: true },
    { href: '/gis-portal', label: 'GIS INUNDATION MAP' },
    { href: '/dashboard', label: 'CWC HYDRO-TELEMETRY' },
    { href: '/analyst', label: 'CASCADE WAVE MODEL' },
    { href: '/broadcast', label: 'CAP BROADCASTER (SMS)', badge: '7 DIALECTS' },
    { href: '/shelters', label: 'RELIEF SHELTERS' },
    { href: '/admin', label: 'AUDIT & SECURITY LEDGER' },
  ];

  return (
    <header className="sticky top-0 z-50 shadow-2xl font-sans">
      
      {/* ========================================================================= */}
      {/* TIER 1: OFFICIAL GOVERNMENT METADATA & ACCESSIBILITY BAR (GIGW 3.0)        */}
      {/* ========================================================================= */}
      <div className="bg-[#0B1E2E] text-slate-300 px-4 lg:px-8 py-1 flex flex-wrap items-center justify-between text-[11px] font-mono border-b border-slate-700/60">
        
        {/* Left: Official Government of India Affiliation */}
        <div className="flex items-center gap-2">
          <span className="text-sm">🇮🇳</span>
          <span className="font-semibold text-slate-200">
            भारत सरकार &bull; Government of India
          </span>
          <span className="text-slate-500 hidden sm:inline">|</span>
          <span className="text-slate-400 hidden sm:inline">
            गृह मंत्रालय &bull; Ministry of Home Affairs
          </span>
        </div>

        {/* Right: Accessibility Controls (A-, A, A+), Text-to-Speech, Language */}
        <div className="flex items-center gap-3">
          <a href="#main-content" className="sr-only focus:not-sr-only text-sky-300 underline mr-2">
            Skip to Main Content
          </a>

          {/* Font Size Resizer (GIGW 3.0 Standard) */}
          <div className="hidden sm:flex items-center gap-1 border border-slate-700 rounded px-1.5 py-0.5 bg-slate-900/80 text-[10px]">
            <button
              onClick={() => setFontSizeOffset(-1)}
              className="px-1 hover:text-white font-bold"
              title="Decrease Font Size"
            >
              A-
            </button>
            <span className="text-slate-600">|</span>
            <button
              onClick={() => setFontSizeOffset(0)}
              className="px-1 hover:text-white font-bold"
              title="Normal Font Size"
            >
              A
            </button>
            <span className="text-slate-600">|</span>
            <button
              onClick={() => setFontSizeOffset(1)}
              className="px-1 hover:text-white font-bold"
              title="Increase Font Size"
            >
              A+
            </button>
          </div>

          {/* Screen Reader & Provenance */}
          {onOpenSources && (
            <button
              onClick={onOpenSources}
              className="text-[10px] text-sky-400 hover:text-sky-300 font-bold hidden md:inline"
            >
              [PROVENANCE &amp; OPEN DATA]
            </button>
          )}

          {/* Language Switcher Dropdown */}
          <div className="flex items-center gap-1 border border-slate-700 rounded px-1.5 py-0.5 bg-slate-900/80">
            <Globe2 className="w-3 h-3 text-sky-400" />
            <select
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value)}
              className="bg-transparent text-slate-200 text-[10px] font-mono focus:outline-none cursor-pointer"
            >
              <option value="English" className="bg-slate-900 text-white">English</option>
              <option value="Hindi" className="bg-slate-900 text-white">हिंदी (Hindi)</option>
              <option value="Garhwali" className="bg-slate-900 text-white">गढ़वाली (Garhwali)</option>
              <option value="Kumaoni" className="bg-slate-900 text-white">कुमाऊँनी (Kumaoni)</option>
              <option value="Sanskrit" className="bg-slate-900 text-white">संस्कृतम् (Sanskrit)</option>
            </select>
          </div>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* TIER 2: NATIONAL EMBLEM & OFFICIAL BRANDING HEADER (CRISP WHITE BACKGROUND) */}
      {/* ========================================================================= */}
      <div className="bg-[#FFFFFF] text-slate-900 px-4 lg:px-8 py-3 flex flex-wrap items-center justify-between gap-4 border-b border-slate-200">
        
        {/* Left: State Emblem of India + Official NDMA Bilingual Identity */}
        <div className="flex items-center gap-3.5">
          {/* Ashoka Lion Capital Emblem */}
          <div className="flex-shrink-0">
            <svg
              className="w-12 h-14 text-slate-900"
              viewBox="0 0 100 120"
              fill="currentColor"
              aria-label="National Emblem of India"
            >
              {/* Stylized Authentic Ashoka Capital Silhouette */}
              <circle cx="50" cy="18" r="12" fill="#0B3C5D" />
              <rect x="42" y="32" width="16" height="35" rx="3" fill="#0B3C5D" />
              <circle cx="28" cy="24" r="9" fill="#0B3C5D" />
              <circle cx="72" cy="24" r="9" fill="#0B3C5D" />
              <path d="M 20 70 Q 50 82 80 70 L 85 92 Q 50 102 15 92 Z" fill="#0B3C5D" />
              {/* Ashoka Chakra Base */}
              <circle cx="50" cy="85" r="7" fill="#FFFFFF" stroke="#0B3C5D" strokeWidth="2" />
              <rect x="25" y="98" width="50" height="6" rx="2" fill="#FF9933" />
              <text x="50" y="116" fontSize="10" fontWeight="bold" textAnchor="middle" fill="#0B3C5D">
                सत्यमेव जयते
              </text>
            </svg>
          </div>

          <div className="flex flex-col">
            <span className="text-xs font-extrabold text-[#0B3C5D] tracking-wide uppercase">
              राष्ट्रीय आपदा प्रबंधन प्राधिकरण
            </span>
            <Link href="/" className="no-underline">
              <h1 className="text-base sm:text-lg lg:text-xl font-black text-[#0B3C5D] tracking-tight leading-tight hover:text-[#0A2540]">
                National Disaster Management Authority
              </h1>
            </Link>
            <span className="text-[11px] font-semibold text-slate-600">
              Government of India &bull; Ministry of Home Affairs &bull; SIH Problem Statement #192
            </span>
          </div>
        </div>

        {/* Center: Search input */}
        <div className="hidden xl:block max-w-xs w-full">
          <GlobalSearchBar />
        </div>

        {/* Right: Digital India, Azadi Ka Amrit Mahotsav, and 24x7 Control Room Badge */}
        <div className="flex items-center gap-4">
          
          {/* Official Azadi Ka Amrit Mahotsav Badge Placeholder */}
          <div className="hidden sm:flex flex-col items-center justify-center p-1.5 border border-slate-200 rounded bg-slate-50 text-center font-mono">
            <span className="text-[9px] font-black text-[#FF9933] leading-none">75th</span>
            <span className="text-[8px] font-bold text-[#0B3C5D] leading-none uppercase mt-0.5">Azadi Ka</span>
            <span className="text-[8px] font-bold text-[#138808] leading-none uppercase">Amrit Mahotsav</span>
          </div>

          {/* Digital India Badge Placeholder */}
          <div className="hidden md:flex flex-col items-center justify-center p-1.5 border border-slate-200 rounded bg-slate-50 text-center font-mono">
            <span className="text-[9px] font-black text-[#0B3C5D] tracking-wider leading-none">Digital India</span>
            <span className="text-[7px] text-slate-500 uppercase mt-0.5">Power To Empower</span>
          </div>

          {/* 24x7 National Control Room Badge */}
          <div className="flex flex-col text-right font-mono bg-red-50 border border-red-200 px-3 py-1.5 rounded text-xs">
            <div className="flex items-center justify-end gap-1 text-red-700 font-bold">
              <PhoneCall className="w-3.5 h-3.5 animate-pulse" />
              <span>NDMA 24x7: 1078</span>
            </div>
            <span className="text-[10px] text-slate-600">State EOC: 1070 | NATL: 112</span>
          </div>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* 3PX OFFICIAL INDIAN TRICOLOR COMPLIANCE LINE                              */}
      {/* ========================================================================= */}
      <div className="tricolor-ribbon" />

      {/* ========================================================================= */}
      {/* TIER 3: MAIN NAVY BLUE NAVBAR RIBBON (#0B3C5D / #0A2540)                  */}
      {/* ========================================================================= */}
      <nav className="bg-[#0B3C5D] border-b border-[#082A42] px-4 lg:px-8 flex items-center justify-between overflow-x-auto scrollbar-none shadow-md">
        <div className="flex items-center gap-1 py-0.5 min-w-max">
          {navMenuItems.map((item) => {
            const isActive = item.exact ? pathname === item.href : pathname.startsWith(item.href);

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-1.5 px-3.5 py-2.5 font-sans font-bold text-xs tracking-wider transition-all relative ${
                  isActive
                    ? 'bg-[#071D30] text-[#FFFFFF] shadow-inner'
                    : 'text-slate-100 hover:text-white hover:bg-[#0E4C75]'
                }`}
              >
                <span>{item.label}</span>
                {item.badge && (
                  <span className="text-[8px] font-mono px-1 py-0.2 rounded bg-amber-400 text-slate-900 font-extrabold ml-1">
                    {item.badge}
                  </span>
                )}
                {/* Active Highlight Underline */}
                {isActive && (
                  <span className="absolute bottom-0 left-0 right-0 h-1 bg-[#FF9933]" />
                )}
              </Link>
            );
          })}
        </div>

        {/* Official Status Live Indicator */}
        <div className="hidden lg:flex items-center gap-2 pl-4 text-emerald-300 font-mono text-[11px]">
          <span className="inline-block w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
          <span className="font-bold">ALL SYSTEMS OPERATIONAL &bull; CWC / IMD ONLINE</span>
        </div>
      </nav>
    </header>
  );
}
export default GovHeaderNIC;
