import type { Metadata } from 'next';
import './globals.css';
import { GlobalStatusBar } from '@/components/layout/GlobalStatusBar';
import { GovNavbar } from '@/components/layout/GovNavbar';

export const metadata: Metadata = {
  title: 'UKIS 2026 (P-011) | AI Mountain Disaster Early-Warning Intelligence — USDMA Devbhoomi',
  description: 'Uttarakhand State Disaster Management Authority & ITDA Uttarakhand Early-Warning Platform for Mountain Hazards (GLOF, Landslides, Slopes, Cloudbursts, Seismicity). Hosted on NIC MeghRaj Cloud.',
  manifest: '/manifest.json',
  themeColor: '#B91C1C',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'black-translucent',
    title: 'UKIS Alert',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="manifest" href="/manifest.json" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
        <meta name="theme-color" content="#B91C1C" />
        <link
          rel="stylesheet"
          href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
          integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
          crossOrigin=""
        />
        <script
          dangerouslySetInnerHTML={{
            __html: `
              if (typeof window !== 'undefined' && 'serviceWorker' in navigator) {
                window.addEventListener('load', function() {
                  navigator.serviceWorker.register('/sw.js').then(
                    function(reg) { console.log('[UKIS] Offline Emergency Service Worker active:', reg.scope); },
                    function(err) { console.warn('[UKIS] Service Worker registration failed:', err); }
                  );
                });
              }
            `,
          }}
        />
      </head>
      <body className="bg-slate-50 text-slate-900 min-h-screen flex flex-col antialiased selection:bg-blue-900 selection:text-white">
        <div id="main-content" className="flex-1 flex flex-col min-w-0">
          {children}
        </div>
        <GlobalStatusBar />
      </body>
    </html>
  );
}
