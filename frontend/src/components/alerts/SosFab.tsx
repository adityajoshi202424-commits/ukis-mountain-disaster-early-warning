'use client';

import React from 'react';
import { PhoneCall } from 'lucide-react';

export function SosFab() {
  return (
    <aside className="fixed bottom-5 right-5 z-40" aria-label="Emergency Speed Dial">
      <a
        href="tel:112"
        className="flex items-center gap-2 bg-red-700 hover:bg-red-800 text-white font-extrabold px-4 py-3 rounded-full shadow-lg hover:shadow-xl border-2 border-white transition-all transform hover:scale-105"
        title="Immediate Emergency Response: Call 112"
      >
        <PhoneCall className="w-5 h-5 animate-bounce" />
        <span className="text-sm font-mono tracking-wide">SOS 112</span>
      </a>
    </aside>
  );
}
