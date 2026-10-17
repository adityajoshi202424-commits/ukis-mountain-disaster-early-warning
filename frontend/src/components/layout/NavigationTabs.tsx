'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function NavigationTabs() {
  const pathname = usePathname();

  const tabs = [
    { href: '/', label: '◷ SIH Replay & Live Console', exact: true },
    { href: '/dashboard', label: '📊 Authority Ops Center' },
    { href: '/analyst', label: '🔬 Hydro-Met Visualizer' },
    { href: '/admin', label: '⚙ System Health & Audit Ledger' },
    { href: '/public', label: '🛡 Public Citizen Advisory' },
  ];

  return (
    <nav
      style={{
        background: 'rgba(15, 23, 42, 0.8)',
        borderBottom: '1px solid rgba(56, 189, 248, 0.15)',
        display: 'flex',
        gap: '6px',
        padding: '0 24px',
        overflowX: 'auto',
        backdropFilter: 'blur(12px)',
      }}
    >
      {tabs.map((t) => {
        const isActive = t.exact ? pathname === t.href : pathname.startsWith(t.href);
        return (
          <Link
            key={t.href}
            href={t.href}
            style={{
              textDecoration: 'none',
              padding: '10px 18px',
              fontSize: '12px',
              fontFamily: 'var(--font-mono)',
              fontWeight: isActive ? 700 : 500,
              color: isActive ? '#38bdf8' : '#94a3b8',
              backgroundColor: isActive ? 'rgba(56, 189, 248, 0.1)' : 'transparent',
              borderBottom: isActive ? '2px solid #38bdf8' : '2px solid transparent',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              transition: 'all 0.2s ease',
              borderRadius: '4px 4px 0 0',
            }}
          >
            <span>{t.label}</span>
          </Link>
        );
      })}
    </nav>
  );
}
