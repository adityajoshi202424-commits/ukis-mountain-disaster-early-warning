'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  Map, 
  BarChart3, 
  Waves, 
  Radio, 
  ShieldCheck, 
  ChevronLeft, 
  ChevronRight,
  Activity,
  Layers,
  Compass,
  FileCode,
  BellRing
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { motion } from 'motion/react';

export function AppSidebar() {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const pathname = usePathname();

  const navItems = [
    {
      href: '/',
      label: 'GIS Tactical Replay',
      badge: 'LIVE MAP',
      icon: Map,
      description: 'Zero-leakage historical & real-time GIS map',
      exact: true,
    },
    {
      href: '/dashboard',
      label: 'Authority Ops Center',
      badge: 'METRICS',
      icon: BarChart3,
      description: 'CWC & IMD hydro-calculus gauges',
    },
    {
      href: '/analyst',
      label: 'Cascade Hydro-Met',
      badge: 'MODELS',
      icon: Waves,
      description: 'Cross-district wave dispersion modeler',
    },
    {
      href: '/public',
      label: 'Emergency Broadcaster',
      badge: '7 DIALECTS',
      icon: Radio,
      description: 'CAP v1.2 XML & multilingual cellular SMS',
    },
    {
      href: '/admin',
      label: 'System Health & Ledger',
      badge: 'AUDIT',
      icon: ShieldCheck,
      description: 'SHA-256 cryptographic consensus ledger',
    },
  ];

  return (
    <aside
      className={cn(
        'hidden md:flex flex-col flex-shrink-0 bg-slate-950/90 border-r border-sky-500/20 backdrop-blur-2xl transition-all duration-300 relative z-30',
        isCollapsed ? 'w-16' : 'w-64'
      )}
    >
      {/* Sidebar Header */}
      <div className="p-4 border-b border-sky-500/20 flex items-center justify-between">
        {!isCollapsed && (
          <div className="flex flex-col">
            <span className="text-[10px] font-mono font-bold text-sky-400 tracking-wider uppercase">
              TACTICAL WORKSPACES
            </span>
            <span className="text-xs font-bold text-slate-200">
              NDMA Operational Matrix
            </span>
          </div>
        )}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="p-1.5 bg-slate-900 hover:bg-slate-800 border border-slate-700/80 rounded-md text-slate-400 hover:text-sky-300 transition-colors mx-auto"
          title={isCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
        >
          {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>

      {/* Navigation Items */}
      <nav className="flex-1 p-2.5 space-y-1.5 overflow-y-auto font-mono text-xs">
        {navItems.map((item) => {
          const isActive = item.exact ? pathname === item.href : pathname.startsWith(item.href);
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all relative group',
                isActive
                  ? 'bg-sky-500/15 border border-sky-400/50 text-sky-200 shadow-[0_0_16px_rgba(56,189,248,0.2)]'
                  : 'text-slate-400 hover:text-slate-100 hover:bg-slate-900/60 border border-transparent'
              )}
            >
              <Icon className={cn('w-4 h-4 flex-shrink-0', isActive ? 'text-sky-400' : 'text-slate-500 group-hover:text-slate-300')} />

              {!isCollapsed && (
                <div className="flex-1 flex items-center justify-between truncate">
                  <div className="flex flex-col truncate">
                    <span className={cn('truncate font-bold', isActive ? 'text-slate-100' : '')}>
                      {item.label}
                    </span>
                    <span className="text-[9px] text-slate-500 truncate">
                      {item.description}
                    </span>
                  </div>
                  {item.badge && (
                    <span
                      className={cn(
                        'text-[8px] px-1.5 py-0.5 rounded font-bold ml-1.5',
                        isActive
                          ? 'bg-sky-400/20 text-sky-300 border border-sky-400/40'
                          : 'bg-slate-900 text-slate-500'
                      )}
                    >
                      {item.badge}
                    </span>
                  )}
                </div>
              )}

              {/* Active Indicator Glow Pip */}
              {isActive && (
                <motion.div
                  layoutId="activeSidebarIndicator"
                  className="absolute left-0 top-1.5 bottom-1.5 w-1 bg-sky-400 rounded-r-full shadow-[0_0_8px_#38bdf8]"
                />
              )}
            </Link>
          );
        })}
      </nav>

      {/* Sidebar Footer Stats */}
      {!isCollapsed && (
        <div className="p-3.5 border-t border-sky-500/20 bg-slate-950/60 text-[10px] font-mono text-slate-400 space-y-1.5">
          <div className="flex justify-between items-center">
            <span>PILOT DISTRICT:</span>
            <span className="text-amber-400 font-bold">Chamoli, Uttarakhand</span>
          </div>
          <div className="flex justify-between items-center">
            <span>RIVER BASIN:</span>
            <span className="text-sky-300">Alaknanda &amp; Rishiganga</span>
          </div>
        </div>
      )}
    </aside>
  );
}
