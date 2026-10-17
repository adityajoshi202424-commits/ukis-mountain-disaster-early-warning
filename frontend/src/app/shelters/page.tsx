'use client';

import React, { useState } from 'react';
import dynamic from 'next/dynamic';
import { TopNav } from '@/components/nav/TopNav';
import { CitizenDrawer } from '@/components/nav/CitizenDrawer';
import { SosFab } from '@/components/alerts/SosFab';
import { GovFooter } from '@/components/layout/GovFooter';
import { ShelterCapacityBar } from '@/components/bars/ShelterCapacityBar';
import { MarkSafeModal } from '@/components/citizen/MarkSafeModal';
import { ReportHazardModal } from '@/components/citizen/ReportHazardModal';
import { FamilyCheckInModal } from '@/components/citizen/FamilyCheckInModal';
import { DmmcLocale } from '@/lib/dmmc_localization';
import { Building2, MapPin, PhoneCall, ShieldCheck, Filter } from 'lucide-react';
import { UttarakhandDistrict } from '@/types/shared_cap';

// Dynamic import for Leaflet GIS map with SSR disabled
const BhuvanGisMap = dynamic(() => import('@/components/gis/BhuvanGisMap'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-[360px] rounded-lg bg-slate-100 border border-slate-200 flex flex-col items-center justify-center text-slate-500">
      <div className="w-8 h-8 border-3 border-blue-700 border-t-transparent rounded-full animate-spin mb-2" />
      <span className="text-xs font-mono">Loading ISRO Bhuvan GIS Map...</span>
    </div>
  ),
});

const SHELTERS_DATA = [
  {
    id: 'UK-SH-001',
    name: 'Joshimath GMVN Safe Elevation Transit Camp',
    capacity: 650,
    occupancy: 210,
    elevationM: 1950.0,
    district: 'Chamoli' as UttarakhandDistrict,
    contact: '+91-1372-222180',
    facilities: ['Medical Clinic', 'Emergency Oxygen', 'Satellite Link', 'Helipad'],
  },
  {
    id: 'UK-SH-002',
    name: 'Guptkashi High-Ground Relief Hub',
    capacity: 900,
    occupancy: 340,
    elevationM: 1319.0,
    district: 'Rudraprayag' as UttarakhandDistrict,
    contact: '+91-1364-267220',
    facilities: ['Disaster Supply Depot', 'Community Kitchen', 'Generator 75kVA'],
  },
  {
    id: 'UK-SH-003',
    name: 'Uttarkashi ITBP Disaster Evacuation Complex',
    capacity: 1200,
    occupancy: 450,
    elevationM: 1158.0,
    district: 'Uttarkashi' as UttarakhandDistrict,
    contact: '+91-1374-222120',
    facilities: ['First Aid Wing', 'Spring Water Filtration', 'Comms Command'],
  },
  {
    id: 'UK-SH-004',
    name: 'Dharchula Stadium Safe Ground Camp',
    capacity: 750,
    occupancy: 180,
    elevationM: 940.0,
    district: 'Pithoragarh' as UttarakhandDistrict,
    contact: '+91-5967-222110',
    facilities: ['Kali River High Bank', 'Emergency Food Stores', 'Medical Unit'],
  },
  {
    id: 'UK-SH-005',
    name: 'HNB Garhwal University Campus Assembly Hall',
    capacity: 800,
    occupancy: 140,
    elevationM: 560.0,
    district: 'Pauri Garhwal' as UttarakhandDistrict,
    contact: '+91-1368-252100',
    facilities: ['High Ridge Campus', 'Emergency Water Tanks', 'Medical Centre'],
  },
  {
    id: 'UK-SH-006',
    name: 'New Tehri District Sports Complex Relief Haven',
    capacity: 950,
    occupancy: 120,
    elevationM: 1750.0,
    district: 'Tehri Garhwal' as UttarakhandDistrict,
    contact: '+91-1376-232100',
    facilities: ['Indoor Stadium', 'Power Backup 100kVA', 'Wireless Comm Link'],
  },
  {
    id: 'UK-SH-007',
    name: 'Nainital Club High-Ground Disaster Assembly Hub',
    capacity: 500,
    occupancy: 95,
    elevationM: 2050.0,
    district: 'Nainital' as UttarakhandDistrict,
    contact: '+91-5942-235100',
    facilities: ['Solid Bedrock Elevation', 'Winter Quarters', 'First Aid Station'],
  },
  {
    id: 'UK-SH-008',
    name: 'Dehradun Parade Ground Multi-Purpose Evacuation Facility',
    capacity: 2000,
    occupancy: 310,
    elevationM: 660.0,
    district: 'Dehradun' as UttarakhandDistrict,
    contact: '+91-135-2710334',
    facilities: ['State SEOC Command Access', 'Mobile Hospital', 'Bulk Food Logistics'],
  },
  {
    id: 'UK-SH-009',
    name: 'Bageshwar Govt Degree College Evacuation Center',
    capacity: 600,
    occupancy: 80,
    elevationM: 1050.0,
    district: 'Bageshwar' as UttarakhandDistrict,
    contact: '+91-5963-220100',
    facilities: ['Elevated Plateau', 'Emergency Rations', 'Ambulance Bay'],
  },
  {
    id: 'UK-SH-010',
    name: 'SSJ University Campus Pavilion Relief Haven',
    capacity: 700,
    occupancy: 110,
    elevationM: 1680.0,
    district: 'Almora' as UttarakhandDistrict,
    contact: '+91-5962-230100',
    facilities: ['Tectonic Stable Ridge', 'Solar Microgrid', 'Sanitation Blocks'],
  },
  {
    id: 'UK-SH-011',
    name: 'Champawat Govt Polytechnic Disaster Shelter',
    capacity: 550,
    occupancy: 70,
    elevationM: 1640.0,
    district: 'Champawat' as UttarakhandDistrict,
    contact: '+91-5965-230150',
    facilities: ['NH-9 Bypass Access', 'Water Filtration', 'Satellite Phone'],
  },
  {
    id: 'UK-SH-012',
    name: 'Haridwar BHEL Community Center High-Water Relief Camp',
    capacity: 2500,
    occupancy: 420,
    elevationM: 295.0,
    district: 'Haridwar' as UttarakhandDistrict,
    contact: '+91-1334-222100',
    facilities: ['Elevated Flood Barrier', 'Industrial Kitchen', 'Emergency Wards'],
  },
  {
    id: 'UK-SH-013',
    name: 'Rudrapur District Sports Stadium Relief Hub',
    capacity: 2800,
    occupancy: 510,
    elevationM: 215.0,
    district: 'Udham Singh Nagar' as UttarakhandDistrict,
    contact: '+91-5944-242100',
    facilities: ['Flood-Resistant Elevated Arena', 'Heavy Logistics Access', 'Power Station'],
  },
];

export default function SheltersPage() {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [locale, setLocale] = useState<DmmcLocale>('en-IN');
  const [isMarkSafeOpen, setIsMarkSafeOpen] = useState(false);
  const [isReportHazardOpen, setIsReportHazardOpen] = useState(false);
  const [isFamilyLookupOpen, setIsFamilyLookupOpen] = useState(false);
  const [lowBandwidth, setLowBandwidth] = useState(false);
  const [selectedDistrict, setSelectedDistrict] = useState<string>('ALL');

  const filteredShelters = SHELTERS_DATA.filter((s) => {
    if (selectedDistrict === 'ALL') return true;
    return s.district === selectedDistrict;
  });

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900 font-sans">
      <TopNav onOpenDrawer={() => setDrawerOpen(true)} />

      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 py-6 space-y-6">
        {/* Page Title Banner */}
        <div className="bg-white border border-slate-200 rounded-lg p-5 shadow-xs flex flex-wrap items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <Building2 className="w-5 h-5 text-blue-900" />
              <h1 className="text-xl sm:text-2xl font-extrabold text-slate-900 tracking-tight">
                Live Evacuation Shelters &amp; High-Ground Havens
              </h1>
            </div>
            <p className="text-xs sm:text-sm text-slate-600">
              Verified safe ground elevation sites above active river surge and flash-flood hazard zones.
            </p>
          </div>

          <div className="flex items-center gap-3 text-xs font-mono font-bold">
            <span className="px-3 py-1.5 bg-emerald-50 border border-emerald-300 text-emerald-900 rounded-md">
              TOTAL CAPACITY: 3,500 BEDS
            </span>
            <span className="px-3 py-1.5 bg-blue-50 border border-blue-200 text-blue-900 rounded-md">
              OCCUPANCY: 1,180 (33.7%)
            </span>
          </div>
        </div>

        {/* Interactive GIS Map (Hidden in Low-Bandwidth Mode) */}
        {!lowBandwidth && (
          <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-xs space-y-2">
            <h2 className="text-xs font-bold uppercase text-slate-500 tracking-wider flex items-center gap-1.5">
              <MapPin className="w-4 h-4 text-blue-700" />
              <span>ISRO Bhuvan High-Ground Shelter Mapping</span>
            </h2>
            <div className="h-[360px] rounded overflow-hidden border border-slate-200">
              <BhuvanGisMap />
            </div>
          </div>
        )}

        {/* Shelters Directory & Filters */}
        <div className="space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3 bg-white border border-slate-200 rounded-lg p-3 sm:p-4 shadow-xs">
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-slate-500" />
              <span className="text-xs font-bold text-slate-700 uppercase">Filter District:</span>
              <select
                value={selectedDistrict}
                onChange={(e) => setSelectedDistrict(e.target.value)}
                className="bg-slate-50 border border-slate-300 text-slate-900 text-xs font-bold rounded px-2.5 py-1.5 focus:ring-2 focus:ring-blue-600 focus:outline-none"
              >
                <option value="ALL">All Districts</option>
                <option value="Chamoli">Chamoli</option>
                <option value="Rudraprayag">Rudraprayag</option>
                <option value="Uttarkashi">Uttarkashi</option>
                <option value="Pithoragarh">Pithoragarh</option>
              </select>
            </div>

            <span className="text-xs text-slate-500 font-mono">
              Showing <strong>{filteredShelters.length}</strong> operational shelters
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredShelters.map((shelter) => (
              <div
                key={shelter.id}
                className="bg-white border border-slate-200 rounded-lg p-4 sm:p-5 shadow-xs space-y-3"
              >
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <h3 className="font-bold text-base text-slate-900 leading-snug">{shelter.name}</h3>
                    <div className="flex items-center gap-2 text-xs text-slate-500 mt-1 font-mono">
                      <span>{shelter.district} District</span>
                      <span>&bull;</span>
                      <span className="text-blue-700 font-semibold">{shelter.elevationM}m Elevation</span>
                    </div>
                  </div>
                  <span className="text-[10px] bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded uppercase">
                    ACCEPTING
                  </span>
                </div>

                <ShelterCapacityBar
                  shelterName={shelter.name}
                  capacity={shelter.capacity}
                  occupancy={shelter.occupancy}
                  label="Bed Capacity Status"
                />

                <div className="flex flex-wrap gap-1.5 pt-1">
                  {shelter.facilities.map((fac, idx) => (
                    <span key={idx} className="text-[11px] bg-slate-100 text-slate-700 px-2 py-0.5 rounded">
                      {fac}
                    </span>
                  ))}
                </div>

                <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs">
                  <a
                    href={`tel:${shelter.contact}`}
                    className="inline-flex items-center gap-1.5 text-blue-700 hover:text-blue-900 font-bold"
                  >
                    <PhoneCall className="w-3.5 h-3.5" />
                    <span>{shelter.contact}</span>
                  </a>
                  <span className="text-[11px] text-slate-400 font-mono">ID: {shelter.id}</span>
                </div>
              </div>
            ))}
          </div>
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
