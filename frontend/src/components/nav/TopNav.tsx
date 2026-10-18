'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { AlertTriangle, MapPin, BookOpen, PhoneCall, Menu, Shield, Mountain, Activity } from 'lucide-react';
import { useLanguage } from '@/context/LanguageContext';

interface TopNavProps {
  onOpenDrawer: () => void;
  hasActiveAlerts?: boolean;
}

export function TopNav({ onOpenDrawer, hasActiveAlerts = false }: TopNavProps) {
  const pathname = usePathname();
  const { locale, t } = useLanguage();

  const getNavLabel = (key: string) => {
    switch (key) {
      case 'alerts':
        return t.tabs?.alerts || 'Active Alerts';
      case 'himKavach':
        if (locale === 'hi-IN') return 'हिम-कवच (XAI)';
        if (locale === 'gbm-IN') return 'हिम-कवच (XAI)';
        if (locale === 'kfy-IN') return 'हिम-कवच (XAI)';
        return 'HIM-KAVACH (XAI)';
      case 'geospatial':
        if (locale === 'hi-IN') return 'भू-स्थानिक एआई';
        if (locale === 'gbm-IN') return 'भू-स्थानिक एआई';
        if (locale === 'kfy-IN') return 'भू-स्थानिक एआई';
        return 'Gov Geospatial AI';
      case 'mountain':
        if (locale === 'hi-IN') return 'पर्वतीय बुद्धिमत्ता';
        if (locale === 'gbm-IN') return 'डांड्युं मा आफत चेताउनी';
        if (locale === 'kfy-IN') return 'डांड मा आफत चेताउनी';
        return 'Mountain Intelligence';
      case 'shelters':
        return t.tabs?.map || 'Live Map & Shelters';
      case 'guidebook':
        return t.tabs?.guidebook || 'Emergency Guidebook';
      default:
        return '';
    }
  };

  const navItems = [
    {
      href: '/',
      label: getNavLabel('alerts'),
      icon: AlertTriangle,
      exact: true,
      badge: hasActiveAlerts ? 'LIVE' : undefined,
    },
    {
      href: '/him-kavach',
      label: getNavLabel('himKavach'),
      icon: Activity,
      exact: false,
      badge: 'UKIS FLAGSHIP',
    },
    {
      href: '/geospatial-intelligence',
      label: getNavLabel('geospatial'),
      icon: Shield,
      exact: false,
      badge: 'RESTRICTED',
    },
    {
      href: '/mountain-intelligence',
      label: getNavLabel('mountain'),
      icon: Mountain,
      exact: false,
      badge: 'LIVE',
    },
    {
      href: '/shelters',
      label: getNavLabel('shelters'),
      icon: MapPin,
      exact: false,
    },
    {
      href: '/guidebook',
      label: getNavLabel('guidebook'),
      icon: BookOpen,
      exact: false,
    },
  ];

  return (
    <header className="sticky top-0 z-40 bg-white border-b border-slate-200 shadow-sm">
      {/* 4px Official Indian Tricolor Ribbon */}
      <div className="h-1 w-full bg-gradient-to-r from-[#FF9933] via-[#FFFFFF] to-[#138808]" />

      {/* Official Government Identity Bar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-2 flex items-center justify-between gap-3 text-xs border-b border-slate-100">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded bg-slate-100 border border-slate-200 flex items-center justify-center text-base shadow-xs" aria-hidden="true">
            🇮🇳
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-slate-900 uppercase tracking-tight text-[12px]">
                {locale === 'hi-IN'
                  ? 'उत्तराखंड शासन • Govt. of Uttarakhand'
                  : locale === 'gbm-IN'
                  ? 'उत्तराखंड सरकार • Govt. of Uttarakhand'
                  : locale === 'kfy-IN'
                  ? 'उत्तराखंड सरकार • Govt. of Uttarakhand'
                  : 'उत्तराखंड शासन • Govt. of Uttarakhand'}
              </span>
              <span className="hidden sm:inline-block text-[10px] text-blue-900 bg-blue-50 border border-blue-200 px-2 py-0.5 rounded font-semibold">
                DMMC Official
              </span>
            </div>
            <p className="text-[11px] text-slate-600 font-medium">
              {locale === 'hi-IN'
                ? 'आपदा न्यूनीकरण एवं प्रबंधन केंद्र • प्रारंभिक चेतावनी प्रणाली'
                : locale === 'gbm-IN'
                ? 'आपदा प्रबंधन केंद्र • डांड्युं मा आफत की पैली चेताउनी'
                : locale === 'kfy-IN'
                ? 'आपदा प्रबंधन केंद्र • डांड मा आफत की पैली चेताउनी'
                : 'Disaster Mitigation & Management Centre • Early Warning'}
            </p>
          </div>
        </div>

        {/* Universal SOS Emergency Helpline */}
        <div className="flex items-center gap-2">
          <a
            href="tel:112"
            className="flex items-center gap-1.5 bg-red-50 border border-red-200 text-red-800 hover:bg-red-100 px-2.5 py-1.5 rounded-md font-mono text-xs font-bold transition-colors"
            title="Emergency Police & Disaster Response: Dial 112"
          >
            <PhoneCall className="w-3.5 h-3.5 text-red-600 animate-pulse" />
            <span>SOS: <strong>112</strong></span>
          </a>
          <span className="hidden md:inline text-slate-400">|</span>
          <span className="hidden md:inline text-[11px] font-mono text-slate-600">
            USDMA: <strong>1070</strong>
          </span>
        </div>
      </div>

      {/* 3 Disciplined Top-Level Anchors + Slide-out Drawer Trigger */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 flex items-center justify-between">
        <nav className="flex items-center gap-1 sm:gap-2 overflow-x-auto py-1 scrollbar-none" aria-label="Primary Navigation">
          {navItems.map((item) => {
            const isActive = item.exact ? pathname === item.href : pathname.startsWith(item.href);
            const Icon = item.icon;

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-2 px-3 sm:px-4 py-2.5 rounded-md text-sm font-bold transition-colors whitespace-nowrap ${
                  isActive
                    ? 'bg-slate-900 text-white shadow-xs'
                    : 'text-slate-700 hover:bg-slate-100 hover:text-slate-900'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-500'}`} />
                <span>{item.label}</span>
                {item.badge && (
                  <span className="text-[10px] bg-red-600 text-white font-extrabold px-1.5 py-0.5 rounded animate-pulse">
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Citizen Slide-Out Drawer Toggle Button */}
        <button
          onClick={onOpenDrawer}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold text-slate-700 bg-slate-100 hover:bg-slate-200 border border-slate-300 rounded-md transition-colors"
          aria-label="Open citizen services and language settings menu"
        >
          <Menu className="w-4 h-4 text-slate-700" />
          <span className="hidden sm:inline">
            {locale === 'hi-IN'
              ? 'सेवाएँ एवं सेटिंग्स'
              : locale === 'gbm-IN'
              ? 'सेवा अर व्यवस्था'
              : locale === 'kfy-IN'
              ? 'सेवा अर खाता'
              : 'Services & Settings'}
          </span>
        </button>
      </div>
    </header>
  );
}
