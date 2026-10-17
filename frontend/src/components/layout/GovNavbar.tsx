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
  ShieldCheck, 
  Building2, 
  PhoneCall, 
  AlertTriangle,
  Info,
  Search,
  Globe2,
  ExternalLink
} from 'lucide-react';
import { GlobalSearchBar } from './GlobalSearchBar';

interface GovNavbarProps {
  onOpenSources?: () => void;
}

export function GovNavbar({ onOpenSources }: GovNavbarProps) {
  const pathname = usePathname();
  const [selectedLang, setSelectedLang] = useState('English');

  const navLinks = [
    { href: '/', label: 'Himalayan GIS Command', hindi: 'हिमालयी जीआईएस कमान', icon: Home, exact: true },
    { href: '/dashboard', label: 'Telemetry & Field Reports', hindi: 'फील्ड रिपोर्ट एवं हाइड्रोलॉजी', icon: BarChart3 },
    { href: '/gis-portal', label: 'GIS Hazard Portal', hindi: 'स्थानिक आपदा मानचित्र', icon: Map },
    { href: '/simulation', label: 'Chamoli GLOF Replay', hindi: 'चमोली आपदा पुनरावृत्ति', icon: Waves, badge: 'ZERO LEAKAGE' },
    { href: '/shelters', label: 'Safe Havens & Shelters', hindi: 'राहत शिविर एवं लॉजिस्टिक्स', icon: Building2 },
    { href: '/broadcast', label: 'CAP & DLT SMS Studio', hindi: 'आपातकालीन चेतावनी', icon: Radio, badge: 'OASIS CAP' },
    { href: '/analyst', label: 'Prioritization Matrix', hindi: 'प्राथमिकता मैट्रिक्स', icon: ShieldCheck },
    { href: '/admin', label: 'System Limitations & Audit', hindi: 'प्रणाली सीमाएं एवं ऑडिट', icon: Info },
  ];

  return (
    <header className="sticky top-0 z-50 bg-white border-b border-slate-200 shadow-sm">
      {/* Top Tricolor Bar of India */}
      <div className="h-1 w-full bg-gradient-to-r from-[#ff9933] via-[#ffffff] to-[#138808]" />

      {/* Official Government Identity Banner */}
      <div className="px-4 lg:px-8 py-2.5 bg-white border-b border-slate-100 flex flex-wrap items-center justify-between gap-3 text-xs">
        {/* Left: National / State Identity */}
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-9 h-9 rounded-lg bg-slate-100 border border-slate-200 text-lg shadow-xs">
            🇮🇳
          </div>
          <div className="flex flex-col leading-tight">
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-slate-900 uppercase tracking-wide text-[12px]">
                उत्तराखंड शासन &bull; Government of Uttarakhand
              </span>
              <span className="text-[10px] text-blue-800 font-semibold px-2 py-0.5 border border-blue-200 rounded-full bg-blue-50">
                DMMC &bull; USDMA Official
              </span>
            </div>
            <span className="text-[11px] text-slate-600 font-medium">
              Disaster Mitigation and Management Centre &bull; State Early-Warning Platform
            </span>
          </div>
        </div>

        {/* Center: Search Bar */}
        <div className="hidden md:block max-w-xs w-full">
          <GlobalSearchBar />
        </div>

        {/* Right: Helplines */}
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2 font-mono text-[11px] text-red-800 bg-red-50 border border-red-200 px-3 py-1.5 rounded-md font-bold">
            <PhoneCall className="w-3.5 h-3.5 text-red-600 animate-pulse" />
            <span>EMERGENCY: <strong>112</strong></span>
            <span className="text-slate-300">|</span>
            <span>USDMA: <strong>1070</strong></span>
          </div>

          <Link
            href="/emergency"
            className="flex items-center gap-1.5 text-[11px] font-bold text-white bg-red-700 hover:bg-red-800 px-3 py-1.5 rounded-md shadow-sm transition-colors"
          >
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>ACTIVE ALERTS</span>
          </Link>
        </div>
      </div>

      {/* Main Clean Government Horizontal Navigation Menu */}
      <nav className="px-4 lg:px-8 bg-slate-50 border-b border-slate-200 flex items-center justify-between overflow-x-auto scrollbar-none">
        <div className="flex items-center gap-1 py-1 min-w-max">
          {[
            { href: '/emergency', label: 'Citizen Active Alerts', hindi: 'सक्रिय आपदा चेतावनियाँ', icon: AlertTriangle },
            { href: '/', label: 'Overview & GIS Command', hindi: 'कमान केंद्र', icon: Home, exact: true },
            { href: '/shelters', label: 'Evacuation Shelters', hindi: 'राहत शिविर', icon: Building2 },
            { href: '/gis-portal', label: 'Himalayan Hazard Map', hindi: 'आपदा मानचित्र', icon: Map },
            { href: '/dashboard', label: 'Sensor Telemetry', hindi: 'सेंसर डेटा', icon: BarChart3 },
            { href: '/admin', label: 'DMMC Ops Control Room', hindi: 'नियंत्रण कक्ष', icon: ShieldCheck },
          ].map((item) => {
            const isActive = item.exact ? pathname === item.href : pathname.startsWith(item.href);
            const Icon = item.icon;

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-2 px-3.5 py-2 rounded-md text-xs font-semibold transition-all relative ${
                  isActive
                    ? 'bg-white text-blue-900 border border-slate-300 shadow-xs font-bold'
                    : 'text-slate-700 hover:text-slate-900 hover:bg-slate-200/70 border border-transparent'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-blue-700' : 'text-slate-500'}`} />
                <div className="flex flex-col text-left">
                  <span className="leading-tight">{item.label}</span>
                  <span className="text-[10px] text-slate-500 font-normal leading-tight hidden lg:block">
                    {item.hindi}
                  </span>
                </div>
              </Link>
            );
          })}
        </div>

        {/* Live Operational Indicator */}
        <div className="hidden xl:flex items-center gap-2 pl-4 border-l border-slate-200 font-mono text-[11px] text-emerald-800 font-semibold bg-emerald-50/80 px-2.5 py-1 rounded-md">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-500 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-600"></span>
          </span>
          <span>SYSTEM ONLINE &bull; 24/7 MONITORING</span>
        </div>
      </nav>
    </header>
  );
}
export default GovNavbar;
