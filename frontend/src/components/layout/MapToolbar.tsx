'use client';

import React, { useState } from 'react';
import { 
  Navigation, 
  Layers, 
  MapPin, 
  Ruler, 
  Download, 
  ShieldAlert, 
  Eye, 
  EyeOff, 
  Compass,
  Maximize2
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface MapToolbarProps {
  showEvacRoutes: boolean;
  onToggleEvacRoutes: () => void;
  onFilterProfile?: (profile: string) => void;
  onExportGeoJSON?: () => void;
  className?: string;
}

export function MapToolbar({
  showEvacRoutes,
  onToggleEvacRoutes,
  onFilterProfile,
  onExportGeoJSON,
  className,
}: MapToolbarProps) {
  const [activeTool, setActiveTool] = useState<string | null>(null);

  return (
    <div
      className={cn(
        'absolute top-4 left-4 z-[400] flex flex-wrap items-center gap-1.5 p-1.5 bg-slate-900/90 border border-sky-500/30 rounded-lg shadow-2xl backdrop-blur-xl',
        className
      )}
    >
      <button
        onClick={onToggleEvacRoutes}
        className={cn(
          'flex items-center gap-1.5 px-3 py-1.5 text-[11px] font-mono font-bold rounded transition-all',
          showEvacRoutes
            ? 'bg-sky-500/20 border border-sky-400 text-sky-300 shadow-[0_0_12px_rgba(56,189,248,0.3)]'
            : 'bg-slate-800/80 border border-slate-700 text-slate-400 hover:text-slate-200'
        )}
        title="Toggle Dijkstra evacuation routes"
      >
        <Navigation className="w-3.5 h-3.5 text-sky-400" />
        <span>EVACUATION VECTORS</span>
      </button>

      <div className="h-4 w-[1px] bg-slate-700 mx-1" />

      <button
        onClick={() => {
          setActiveTool(activeTool === 'distance' ? null : 'distance');
        }}
        className={cn(
          'flex items-center gap-1.5 px-2.5 py-1.5 text-[11px] font-mono rounded transition-all',
          activeTool === 'distance'
            ? 'bg-amber-500/20 border border-amber-400 text-amber-300'
            : 'bg-slate-800/60 border border-slate-700 text-slate-400 hover:text-slate-200'
        )}
        title="Spatial Measure Tool"
      >
        <Ruler className="w-3.5 h-3.5" />
        <span>MEASURE</span>
      </button>

      <button
        onClick={() => {
          if (onExportGeoJSON) onExportGeoJSON();
          else alert('Exporting GeoJSON Boundary & Contour Layers to JSON...');
        }}
        className="flex items-center gap-1.5 px-2.5 py-1.5 text-[11px] font-mono bg-slate-800/60 hover:bg-slate-700 border border-slate-700 text-slate-300 rounded transition-all"
        title="Export spatial layers to GeoJSON"
      >
        <Download className="w-3.5 h-3.5 text-emerald-400" />
        <span>EXPORT GEOJSON</span>
      </button>
    </div>
  );
}
