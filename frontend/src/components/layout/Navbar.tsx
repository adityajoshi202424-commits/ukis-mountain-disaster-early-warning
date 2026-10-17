'use client';

import React from 'react';
import Link from 'next/link';
import { GlobalSearchBar } from './GlobalSearchBar';
import { ShieldCheck, Info, ShieldAlert } from 'lucide-react';

interface NavbarProps {
  currentMode?: 'LIVE' | 'HISTORICAL' | 'REPLAY' | 'SIMULATION';
  onOpenSources?: () => void;
  onOpenLimitations?: () => void;
  onSelectSearch?: (result: any) => void;
}

export default function Navbar({ currentMode = 'REPLAY', onOpenSources, onOpenLimitations, onSelectSearch }: NavbarProps) {
  const getModeBadge = () => {
    switch (currentMode) {
      case 'LIVE':
        return {
          bg: 'rgba(16, 185, 129, 0.15)',
          border: 'rgba(16, 185, 129, 0.4)',
          color: '#34d399',
          shadow: '0 0 12px rgba(16, 185, 129, 0.25)',
          text: '● LIVE REAL-TIME OBSERVATIONS',
        };
      case 'SIMULATION':
        return {
          bg: 'rgba(239, 68, 68, 0.15)',
          border: 'rgba(239, 68, 68, 0.4)',
          color: '#f87171',
          shadow: '0 0 12px rgba(239, 68, 68, 0.25)',
          text: '⚠ SIMULATION / SCENARIO MODE',
        };
      case 'HISTORICAL':
      case 'REPLAY':
      default:
        return {
          bg: 'rgba(14, 165, 233, 0.15)',
          border: 'rgba(56, 189, 248, 0.4)',
          color: '#38bdf8',
          shadow: '0 0 12px rgba(14, 165, 233, 0.25)',
          text: '◷ ZERO-LEAKAGE HISTORICAL REPLAY',
        };
    }
  };

  const badge = getModeBadge();

  return (
    <header className="bg-slate-950/95 border-b border-sky-500/20 px-4 lg:px-6 py-3 flex flex-wrap items-center justify-between gap-4 sticky top-0 z-40 backdrop-blur-2xl shadow-xl">
      {/* Brand & Agency Title */}
      <div className="flex flex-col gap-0.5">
        <div className="flex items-center gap-2">
          <span className="text-sm">🇮🇳</span>
          <span className="font-mono text-[10px] font-bold tracking-widest text-sky-400 uppercase">
            UKIS 2026 &bull; PROBLEM STATEMENT P-011 &bull; USDMA UTTARAKHAND
          </span>
        </div>

        <Link href="/" className="no-underline group">
          <h1 className="text-base lg:text-lg font-extrabold bg-gradient-to-r from-white via-slate-100 to-sky-400 bg-clip-text text-transparent tracking-tight group-hover:to-sky-300 transition-all">
            AI Mountain Disaster Early-Warning Intelligence
          </h1>
        </Link>
        <span className="text-[11px] text-slate-400 font-mono">
          Mountain Hazards: Glacial Lakes (GLOF), Cloudbursts &amp; Slopes &bull; State of Uttarakhand
        </span>
      </div>

      {/* Global Interactive Search Bar */}
      <div className="flex-1 max-w-md mx-2 hidden sm:block">
        <GlobalSearchBar onSelectResult={onSelectSearch} />
      </div>

      {/* Right Controls, Limitations & Provenance */}
      <div className="flex items-center gap-3">
        <div
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-mono font-bold transition-all"
          style={{
            backgroundColor: badge.bg,
            border: `1px solid ${badge.border}`,
            color: badge.color,
            boxShadow: badge.shadow,
          }}
        >
          {badge.text}
        </div>

        {onOpenLimitations && (
          <button
            onClick={onOpenLimitations}
            className="flex items-center gap-1.5 bg-amber-950/80 hover:bg-amber-900 border border-amber-500/40 text-amber-200 px-3 py-1.5 rounded-lg text-xs font-mono font-semibold transition-all hover:border-amber-400"
            title="Inspect platform limitations, coverage scope, and feature tiers (UKIS Section 3.17)"
          >
            <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />
            <span>LIMITATIONS</span>
          </button>
        )}

        {onOpenSources && (
          <button
            onClick={onOpenSources}
            className="flex items-center gap-1.5 bg-slate-900/80 hover:bg-slate-800 border border-sky-500/30 text-slate-200 px-3 py-1.5 rounded-lg text-xs font-mono font-semibold transition-all hover:border-sky-400"
            title="Inspect verifiable external data sources & provenance"
          >
            <Info className="w-3.5 h-3.5 text-sky-400" />
            <span>PROVENANCE</span>
          </button>
        )}
      </div>
    </header>
  );
}

