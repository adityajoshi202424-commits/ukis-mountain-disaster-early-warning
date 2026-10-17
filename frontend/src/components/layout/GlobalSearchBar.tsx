'use client';

import React, { useState } from 'react';
import { Search, MapPin, Building2, Radio, X } from 'lucide-react';
import { cn } from '@/lib/utils';

interface SearchResult {
  id: string;
  title: string;
  category: 'DISTRICT' | 'STATION' | 'SHELTER';
  coords: [number, number];
}

const SEARCH_ITEMS: SearchResult[] = [
  { id: 'CHAMOLI', title: 'Joshimath / Tapovan (Alaknanda & Rishiganga Gorge)', category: 'DISTRICT', coords: [30.5564, 79.5670] },
  { id: 'RUDRAPRAYAG', title: 'Kedarnath / Gaurikund (Mandakini Valley)', category: 'DISTRICT', coords: [30.7346, 79.0669] },
  { id: 'UTTARKASHI', title: 'Uttarkashi / Bhatwari (Bhagirathi Gorge)', category: 'DISTRICT', coords: [30.7268, 78.4354] },
  { id: 'PITHORAGARH', title: 'Dharchula / Milam (Kali & Goriganga Basin)', category: 'DISTRICT', coords: [29.8543, 80.5425] },
  { id: 'NAINITAL', title: 'Balia Nala / Nainital Hill Slopes', category: 'DISTRICT', coords: [29.3919, 79.4542] },
  { id: 'STN-001', title: 'Joshimath CWC Gauge Station', category: 'STATION', coords: [30.5564, 79.5670] },
  { id: 'STN-002', title: 'Srinagar Alaknanda Gauge Station', category: 'STATION', coords: [30.2220, 78.7840] },
  { id: 'STN-003', title: 'Kedarnath Mandakini AWS Gauge Station', category: 'STATION', coords: [30.7346, 79.0669] },
  { id: 'STN-004', title: 'Uttarkashi Bhagirathi AWS Gauge Station', category: 'STATION', coords: [30.7268, 78.4354] },
  { id: 'SHELTER-01', title: 'Joshimath Cantonment High-Ground Shelter (El: 2050m)', category: 'SHELTER', coords: [30.565, 79.578] },
  { id: 'SHELTER-02', title: 'Govt Inter College Joshimath Campus (El: 1980m)', category: 'SHELTER', coords: [30.563, 79.574] },
];

interface GlobalSearchBarProps {
  onSelectResult?: (result: SearchResult) => void;
  className?: string;
}

export function GlobalSearchBar({ onSelectResult, className }: GlobalSearchBarProps) {
  const [query, setQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);

  const filtered = query.trim()
    ? SEARCH_ITEMS.filter((item) => item.title.toLowerCase().includes(query.toLowerCase()) || item.id.toLowerCase().includes(query.toLowerCase()))
    : [];

  return (
    <div className={cn('relative w-full max-w-xs sm:max-w-sm font-mono text-xs', className)}>
      <div className="relative flex items-center">
        <Search className="w-4 h-4 text-sky-400 absolute left-3 pointer-events-none" />
        <input
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setIsOpen(true);
          }}
          onFocus={() => setIsOpen(true)}
          placeholder="Search districts, stations, shelters..."
          className="w-full pl-9 pr-8 py-2 bg-slate-900/90 border border-sky-500/30 rounded-lg text-slate-100 placeholder-slate-500 focus:outline-none focus:border-sky-400 focus:ring-1 focus:ring-sky-400 backdrop-blur-xl transition-all shadow-inner"
        />
        {query && (
          <button
            onClick={() => {
              setQuery('');
              setIsOpen(false);
            }}
            className="absolute right-2.5 text-slate-400 hover:text-slate-200"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        )}
      </div>

      {/* Autocomplete Dropdown */}
      {isOpen && filtered.length > 0 && (
        <div className="absolute top-full mt-1.5 left-0 right-0 z-50 bg-slate-900 border border-sky-500/40 rounded-lg shadow-2xl overflow-hidden backdrop-blur-2xl max-h-60 overflow-y-auto">
          {filtered.map((item) => (
            <button
              key={item.id}
              onClick={() => {
                if (onSelectResult) onSelectResult(item);
                setQuery(item.title);
                setIsOpen(false);
              }}
              className="w-full px-3.5 py-2.5 flex items-center justify-between gap-2 hover:bg-sky-500/10 border-b border-slate-800/80 last:border-b-0 text-left transition-colors"
            >
              <div className="flex items-center gap-2.5 truncate">
                {item.category === 'DISTRICT' && <MapPin className="w-3.5 h-3.5 text-amber-400 flex-shrink-0" />}
                {item.category === 'STATION' && <Radio className="w-3.5 h-3.5 text-sky-400 flex-shrink-0" />}
                {item.category === 'SHELTER' && <Building2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />}
                <span className="text-slate-200 truncate">{item.title}</span>
              </div>
              <span className="text-[9px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-bold">
                {item.category}
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
