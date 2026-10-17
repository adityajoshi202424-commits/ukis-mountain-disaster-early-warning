'use client';

import React from 'react';
import { motion } from 'motion/react';
import { cn } from '@/lib/utils';

interface BorderTrailProps {
  className?: string;
  size?: number;
  duration?: number;
  trailColor?: string;
}

export function BorderTrail({
  className,
  size = 60,
  duration = 4,
  trailColor = 'linear-gradient(90deg, transparent, #38bdf8, transparent)',
}: BorderTrailProps) {
  return (
    <div className={cn('absolute inset-0 overflow-hidden rounded-inherit pointer-events-none', className)}>
      <motion.div
        className="absolute w-full h-full"
        style={{
          background: trailColor,
        }}
        animate={{
          x: ['-100%', '100%'],
        }}
        transition={{
          repeat: Infinity,
          duration,
          ease: 'linear',
        }}
      />
    </div>
  );
}
