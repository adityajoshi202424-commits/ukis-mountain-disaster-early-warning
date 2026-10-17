'use client';

import React, { useState } from 'react';
import { TopNav } from '@/components/nav/TopNav';
import { CitizenDrawer } from '@/components/nav/CitizenDrawer';
import { SosFab } from '@/components/alerts/SosFab';
import { GovFooter } from '@/components/layout/GovFooter';
import { MarkSafeModal } from '@/components/citizen/MarkSafeModal';
import { ReportHazardModal } from '@/components/citizen/ReportHazardModal';
import { FamilyCheckInModal } from '@/components/citizen/FamilyCheckInModal';
import { DmmcLocale } from '@/lib/dmmc_localization';
import { 
  Waves, 
  Mountain, 
  Snowflake, 
  ShieldAlert, 
  CheckSquare, 
  PhoneCall, 
  AlertTriangle 
} from 'lucide-react';

export default function EmergencyGuidebookPage() {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [locale, setLocale] = useState<DmmcLocale>('en-IN');
  const [isMarkSafeOpen, setIsMarkSafeOpen] = useState(false);
  const [isReportHazardOpen, setIsReportHazardOpen] = useState(false);
  const [isFamilyLookupOpen, setIsFamilyLookupOpen] = useState(false);
  const [lowBandwidth, setLowBandwidth] = useState(false);

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900 font-sans">
      <TopNav onOpenDrawer={() => setDrawerOpen(true)} />

      <main className="flex-1 max-w-5xl mx-auto w-full px-4 sm:px-6 py-6 sm:py-8 space-y-6">
        {/* Header Title Banner */}
        <div className="bg-white border border-slate-200 rounded-lg p-5 sm:p-6 shadow-xs space-y-2">
          <div className="flex items-center gap-2 text-xs font-bold text-red-700 uppercase tracking-wider">
            <AlertTriangle className="w-4 h-4" />
            <span>Official Himalayan Survival Protocols</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Emergency Evacuation &amp; Safety Guidebook
          </h1>
          <p className="text-sm sm:text-base text-slate-600 leading-relaxed max-w-3xl">
            Critical response guidelines for mountain communities and pilgrims traveling along Uttarakhand river valleys (Char Dham &amp; Border Highway Corridors).
          </p>
        </div>

        {/* Hazard Protocol Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* 1. Flash Flood & Cloudburst */}
          <div className="bg-white border border-slate-200 border-t-4 border-t-blue-700 rounded-lg p-5 shadow-xs space-y-3">
            <div className="w-9 h-9 rounded-lg bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-700">
              <Waves className="w-5 h-5" />
            </div>
            <h2 className="text-base font-bold text-slate-900">Flash Flood &amp; Cloudburst</h2>
            <ul className="text-xs sm:text-sm text-slate-700 space-y-2 list-disc list-inside leading-relaxed">
              <li><strong>Move to high ground immediately:</strong> Gain at least 50m of vertical elevation above stream channels.</li>
              <li><strong>Never cross culverts or bridges</strong> when water is murky or accelerating. 15cm of rushing mountain water can sweep an adult away.</li>
              <li>Disconnect electricity and gas if instructed before evacuating.</li>
            </ul>
          </div>

          {/* 2. Landslide & Rockfall */}
          <div className="bg-white border border-slate-200 border-t-4 border-t-amber-700 rounded-lg p-5 shadow-xs space-y-3">
            <div className="w-9 h-9 rounded-lg bg-amber-50 border border-amber-200 flex items-center justify-center text-amber-700">
              <Mountain className="w-5 h-5" />
            </div>
            <h2 className="text-base font-bold text-slate-900">Landslides &amp; Slope Creep</h2>
            <ul className="text-xs sm:text-sm text-slate-700 space-y-2 list-disc list-inside leading-relaxed">
              <li><strong>Escape sideways:</strong> Run perpendicular to the direction of falling debris, not downhill.</li>
              <li>Watch for early warning signs: sudden muddy water in clear springs, tilting telephone poles, or deep rumbling sounds.</li>
              <li>If trapped in a vehicle during rockfall, remain inside with doors unlocked.</li>
            </ul>
          </div>

          {/* 3. Glacial Lake Outburst (GLOF) */}
          <div className="bg-white border border-slate-200 border-t-4 border-t-red-700 rounded-lg p-5 shadow-xs space-y-3">
            <div className="w-9 h-9 rounded-lg bg-red-50 border border-red-200 flex items-center justify-center text-red-700">
              <Snowflake className="w-5 h-5" />
            </div>
            <h2 className="text-base font-bold text-slate-900">GLOF &amp; Dam Breaches</h2>
            <ul className="text-xs sm:text-sm text-slate-700 space-y-2 list-disc list-inside leading-relaxed">
              <li>GLOF waves travel extremely fast down narrow gorges (e.g. Rishi Ganga, Alaknanda).</li>
              <li>Move to designated hill flanks above the flood plain without returning for belongings.</li>
              <li>Do not seek shelter inside riverbed hotels, ashrams, or concrete basements.</li>
            </ul>
          </div>
        </div>

        {/* Emergency Go-Bag Checklist */}
        <div className="bg-white border border-slate-200 rounded-lg p-5 sm:p-6 shadow-xs space-y-4">
          <div className="flex items-center gap-2">
            <CheckSquare className="w-5 h-5 text-emerald-700" />
            <h2 className="text-lg font-bold text-slate-900">Mountain Emergency Go-Bag Checklist</h2>
          </div>
          <p className="text-xs sm:text-sm text-slate-600">
            Keep a waterproof backpack ready near the exit with these essentials:
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 text-xs sm:text-sm text-slate-700 font-medium">
            <div className="p-3 bg-slate-50 border border-slate-200 rounded">✓ 3 Liters bottled water per person</div>
            <div className="p-3 bg-slate-50 border border-slate-200 rounded">✓ High-calorie dry rations / glucose</div>
            <div className="p-3 bg-slate-50 border border-slate-200 rounded">✓ Battery torch with spare cells</div>
            <div className="p-3 bg-slate-50 border border-slate-200 rounded">✓ Loud whistle for acoustic rescue signal</div>
            <div className="p-3 bg-slate-50 border border-slate-200 rounded">✓ Waterproof pouch: Aadhaar, IDs, cash</div>
            <div className="p-3 bg-slate-50 border border-slate-200 rounded">✓ Warm thermal blanket &amp; poncho</div>
            <div className="p-3 bg-slate-50 border border-slate-200 rounded">✓ First-aid kit + 7 days personal meds</div>
            <div className="p-3 bg-slate-50 border border-slate-200 rounded">✓ Fully charged power bank &amp; cables</div>
            <div className="p-3 bg-slate-50 border border-slate-200 rounded">✓ Portable FM/AM battery radio</div>
          </div>
        </div>

        {/* Emergency Helplines Callout */}
        <div className="bg-red-50 border border-red-200 rounded-lg p-5 flex flex-wrap items-center justify-between gap-4">
          <div>
            <h3 className="font-bold text-sm text-red-950">Immediate Life Threat or Stranded?</h3>
            <p className="text-xs text-red-800">State emergency services and SDRF mountain response teams are active 24/7.</p>
          </div>
          <a
            href="tel:112"
            className="flex items-center gap-2 bg-red-700 hover:bg-red-800 text-white font-extrabold px-5 py-2.5 rounded-md shadow-xs text-sm transition-colors"
          >
            <PhoneCall className="w-4 h-4" />
            <span>Call 112 Now</span>
          </a>
        </div>
      </main>

      <CitizenDrawer
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        currentLocale={locale}
        onSelectLocale={setLocale}
        onOpenMarkSafe={() => setIsMarkSafeOpen(true)}
        onOpenReportHazard={() => setIsReportHazardOpen(true)}
        onOpenFamilyLookup={() => setIsFamilyLookupOpen(true)}
        lowBandwidth={lowBandwidth}
        onToggleLowBandwidth={() => setLowBandwidth(!lowBandwidth)}
      />

      <MarkSafeModal isOpen={isMarkSafeOpen} onClose={() => setIsMarkSafeOpen(false)} />
      <ReportHazardModal isOpen={isReportHazardOpen} onClose={() => setIsReportHazardOpen(false)} />
      <FamilyCheckInModal isOpen={isFamilyLookupOpen} onClose={() => setIsFamilyLookupOpen(false)} />

      <SosFab />
      <GovFooter />
    </div>
  );
}
