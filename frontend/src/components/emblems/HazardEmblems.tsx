import React from 'react';

interface HazardEmblemProps {
  type: string;
  className?: string;
  size?: number;
}

export const HazardEmblem: React.FC<HazardEmblemProps> = ({ type, className = 'w-6 h-6', size = 24 }) => {
  const normType = type.toUpperCase();

  // 1. GLOF & Flash Floods Vector Emblem
  if (normType.includes('FLOOD') || normType.includes('GLOF')) {
    return (
      <svg className={className} width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M2 13c1.5-2 3.5-2 5 0s3.5 2 5 0 3.5-2 5 0 3.5 2 5 0" />
        <path d="M2 18c1.5-2 3.5-2 5 0s3.5 2 5 0 3.5-2 5 0 3.5 2 5 0" />
        <path d="M12 2a5 5 0 0 0-5 5c0 3 5 7 5 7s5-4 5-7a5 5 0 0 0-5-5z" fill="currentColor" fillOpacity="0.3" />
      </svg>
    );
  }

  // 2. Landslides & Mudslides Vector Emblem
  if (normType.includes('LANDSLIDE') || normType.includes('SLOPE') || normType.includes('MUD')) {
    return (
      <svg className={className} width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M2 20h20" />
        <path d="m3 19 8-14 4 7 7 7" />
        <circle cx="16" cy="7" r="1.5" fill="currentColor" />
        <circle cx="19" cy="11" r="2" fill="currentColor" />
        <circle cx="17" cy="15" r="1.5" fill="currentColor" />
      </svg>
    );
  }

  // 3. Cloudbursts & Severe Thunderstorms Vector Emblem
  if (normType.includes('CLOUDBURST') || normType.includes('RAIN') || normType.includes('THUNDER')) {
    return (
      <svg className={className} width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M17.5 14A4.5 4.5 0 0 0 18 5a6 6 0 0 0-11.72 1.5A4.5 4.5 0 0 0 6.5 14h11z" fill="currentColor" fillOpacity="0.2" />
        <path d="m13 13-3 5h4l-2 5" strokeWidth="2.5" />
      </svg>
    );
  }

  // 4. Earthquakes & Seismic Fault Lines Vector Emblem
  if (normType.includes('EARTHQUAKE') || normType.includes('SEISMIC')) {
    return (
      <svg className={className} width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M2 12h3l2-5 3 10 3-8 2 6 2-3h7" />
        <path d="M4 18h16" strokeDasharray="3 3" />
        <path d="M4 6h16" strokeDasharray="3 3" />
      </svg>
    );
  }

  // 5. Forest Fires Vector Emblem
  if (normType.includes('FIRE') || normType.includes('FOREST')) {
    return (
      <svg className={className} width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z" fill="currentColor" fillOpacity="0.3" />
      </svg>
    );
  }

  // 6. Heavy Snowfall & Avalanches Vector Emblem
  if (normType.includes('SNOW') || normType.includes('AVALANCHE') || normType.includes('BLIZZARD')) {
    return (
      <svg className={className} width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M2 20 8 9l5 7 4-5 5 9H2z" />
        <line x1="12" y1="2" x2="12" y2="6" />
        <line x1="10" y1="3" x2="14" y2="5" />
        <line x1="10" y1="5" x2="14" y2="3" />
      </svg>
    );
  }

  // Generic Emergency Warning Emblem
  return (
    <svg className={className} width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
      <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3z" fill="currentColor" fillOpacity="0.2" />
      <line x1="12" y1="9" x2="12" y2="13" />
      <line x1="12" y1="17" x2="12.01" y2="17" strokeWidth="3" />
    </svg>
  );
};

export default HazardEmblem;
