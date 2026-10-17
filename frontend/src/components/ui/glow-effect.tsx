'use client';

import React from 'react';
import { motion } from 'motion/react';
import { cn } from '@/lib/utils';

interface GlowEffectProps {
  children?: React.ReactNode;
  className?: string;
  glowColor?: string;
  blur?: number;
  duration?: number;
}

export function GlowEffect({
  children,
  className,
  glowColor = 'rgba(56, 189, 248, 0.35)',
  blur = 20,
  duration = 3,
}: GlowEffectProps) {
  return (
    <div className={cn('relative group', className)}>
      <motion.div
        className="absolute -inset-0.5 rounded-lg opacity-75 blur-md pointer-events-none"
        style={{
          background: glowColor,
          filter: `blur(${blur}px)`,
        }}
        animate={{
          opacity: [0.4, 0.85, 0.4],
          scale: [0.98, 1.01, 0.98],
        }}
        transition={{
          duration,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
      />
      <div className="relative z-10">{children}</div>
    </div>
  );
}
