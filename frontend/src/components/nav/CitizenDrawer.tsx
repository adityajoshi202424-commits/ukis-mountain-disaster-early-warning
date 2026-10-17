'use client';

import React from 'react';
import Link from 'next/link';
import { 
  X, 
  Globe, 
  ShieldCheck, 
  Users, 
  AlertCircle, 
  Wifi, 
  WifiOff, 
  PhoneCall, 
  Lock, 
  CheckCircle2, 
  Trash2 
} from 'lucide-react';
import { DmmcLocale } from '@/lib/dmmc_localization';

interface CitizenDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  currentLocale: DmmcLocale;
  onSelectLocale: (locale: DmmcLocale) => void;
  onOpenMarkSafe: () => void;
  onOpenReportHazard: () => void;
  onOpenFamilyLookup: () => void;
  lowBandwidth: boolean;
  onToggleLowBandwidth: () => void;
  lastSyncTime?: string;
}

export function CitizenDrawer({
  isOpen,
  onClose,
  currentLocale,
  onSelectLocale,
  onOpenMarkSafe,
  onOpenReportHazard,
  onOpenFamilyLookup,
  lowBandwidth,
  onToggleLowBandwidth,
  lastSyncTime,
}: CitizenDrawerProps) {
  if (!isOpen) return null;

  const languages: { code: DmmcLocale; label: string; native: string }[] = [
    { code: 'en-IN', label: 'English', native: 'English' },
    { code: 'hi-IN', label: 'Hindi', native: 'हिन्दी' },
    { code: 'gbm-IN', label: 'Garhwali', native: 'गढ़वाली' },
    { code: 'kfy-IN', label: 'Kumaoni', native: 'कुमाऊँनी' },
  ];

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs transition-opacity"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Drawer Panel */}
      <div className="relative w-full max-w-sm bg-white h-full shadow-2xl flex flex-col z-10 border-l border-slate-200">
        {/* Drawer Header */}
        <div className="p-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
          <div>
            <h2 className="text-sm font-bold text-slate-900">Citizen Services &amp; Tools</h2>
            <p className="text-xs text-slate-500">DMMC Uttarakhand Disaster Portal</p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-500 hover:text-slate-900 rounded-md hover:bg-slate-200 transition-colors"
            aria-label="Close menu"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Drawer Scrollable Content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-6 text-sm">
          {/* 1. Language Switcher */}
          <div>
            <label className="flex items-center gap-1.5 font-bold text-xs text-slate-700 uppercase tracking-wider mb-2">
              <Globe className="w-4 h-4 text-blue-700" />
              <span>Language / भाषा</span>
            </label>
            <div className="grid grid-cols-2 gap-2">
              {languages.map((lang) => (
                <button
                  key={lang.code}
                  onClick={() => onSelectLocale(lang.code)}
                  className={`p-2 rounded border text-left transition-all ${
                    currentLocale === lang.code
                      ? 'bg-blue-50 border-blue-600 text-blue-900 font-bold shadow-xs'
                      : 'border-slate-200 hover:bg-slate-50 text-slate-700'
                  }`}
                >
                  <span className="block text-xs">{lang.native}</span>
                  <span className="block text-[10px] text-slate-500">{lang.label}</span>
                </button>
              ))}
            </div>
          </div>

          <hr className="border-slate-100" />

          {/* 2. Citizen Safety Actions */}
          <div className="space-y-2">
            <label className="font-bold text-xs text-slate-700 uppercase tracking-wider block mb-2">
              Public Safety Actions
            </label>

            <button
              onClick={() => { onClose(); onOpenMarkSafe(); }}
              className="w-full flex items-center gap-3 p-3 bg-emerald-50 hover:bg-emerald-100 border border-emerald-300 rounded-lg text-emerald-900 font-bold text-left transition-colors shadow-xs"
            >
              <ShieldCheck className="w-5 h-5 text-emerald-700 flex-shrink-0" />
              <div>
                <span className="block text-xs sm:text-sm">Mark Yourself Safe</span>
                <span className="block text-[11px] text-emerald-700 font-normal">Notify linked family numbers</span>
              </div>
            </button>

            <button
              onClick={() => { onClose(); onOpenFamilyLookup(); }}
              className="w-full flex items-center gap-3 p-3 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg text-blue-900 font-bold text-left transition-colors"
            >
              <Users className="w-5 h-5 text-blue-700 flex-shrink-0" />
              <div>
                <span className="block text-xs sm:text-sm">Check Loved Ones&apos; Safety</span>
                <span className="block text-[11px] text-blue-700 font-normal">Lookup check-in status by phone</span>
              </div>
            </button>

            <button
              onClick={() => { onClose(); onOpenReportHazard(); }}
              className="w-full flex items-center gap-3 p-3 bg-amber-50 hover:bg-amber-100 border border-amber-300 rounded-lg text-amber-900 font-bold text-left transition-colors"
            >
              <AlertCircle className="w-5 h-5 text-amber-700 flex-shrink-0" />
              <div>
                <span className="block text-xs sm:text-sm">Report Mountain Hazard</span>
                <span className="block text-[11px] text-amber-800 font-normal">Geotag road blockages or slides</span>
              </div>
            </button>
          </div>

          <hr className="border-slate-100" />

          {/* 3. Connectivity & Low-Bandwidth Mode */}
          <div>
            <label className="font-bold text-xs text-slate-700 uppercase tracking-wider block mb-2">
              Connectivity Mode
            </label>
            <div className="flex items-center justify-between p-3 bg-slate-50 border border-slate-200 rounded-lg">
              <div className="flex items-center gap-2">
                {lowBandwidth ? (
                  <WifiOff className="w-4 h-4 text-amber-700" />
                ) : (
                  <Wifi className="w-4 h-4 text-emerald-700" />
                )}
                <div>
                  <span className="block text-xs font-bold text-slate-800">
                    2G/3G Low-Bandwidth
                  </span>
                  <span className="block text-[11px] text-slate-500">
                    {lowBandwidth ? 'Optimized text-only' : 'Standard live GIS map'}
                  </span>
                </div>
              </div>
              <button
                onClick={onToggleLowBandwidth}
                className={`px-3 py-1 text-xs font-bold rounded-full transition-colors ${
                  lowBandwidth 
                    ? 'bg-amber-600 text-white' 
                    : 'bg-slate-200 text-slate-700 hover:bg-slate-300'
                }`}
              >
                {lowBandwidth ? 'ON' : 'OFF'}
              </button>
            </div>
            {lastSyncTime && (
              <p className="text-[11px] text-slate-500 mt-2 font-mono">
                Cached telemetry: {lastSyncTime}
              </p>
            )}
          </div>

          <hr className="border-slate-100" />

          {/* 4. Emergency Directory */}
          <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 space-y-1.5 text-xs">
            <span className="font-bold text-slate-800 block mb-1">Emergency Numbers</span>
            <div className="flex justify-between font-mono">
              <span className="text-slate-600">Police &amp; All Emergencies:</span>
              <strong className="text-red-700">112</strong>
            </div>
            <div className="flex justify-between font-mono">
              <span className="text-slate-600">State Disaster Control:</span>
              <strong className="text-slate-900">1070</strong>
            </div>
            <div className="flex justify-between font-mono">
              <span className="text-slate-600">District Emergency Ops:</span>
              <strong className="text-slate-900">1077</strong>
            </div>
          </div>
        </div>

        {/* Drawer Footer: Discrete Link to Gated DMMC Admin */}
        <div className="p-4 border-t border-slate-200 bg-slate-50 flex items-center justify-between text-xs">
          <span className="text-slate-500">Staff Control Room</span>
          <Link
            href="/admin"
            onClick={onClose}
            className="flex items-center gap-1.5 text-blue-700 hover:text-blue-900 font-bold hover:underline"
          >
            <Lock className="w-3.5 h-3.5" />
            <span>DMMC Login</span>
          </Link>
        </div>
      </div>
    </div>
  );
}
