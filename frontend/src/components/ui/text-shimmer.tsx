'use client';

import React from 'react';
import { motion } from 'motion/react';
import { cn } from '@/lib/utils';

interface TextShimmerProps {
  children: React.ReactNode;
  className?: string;
  duration?: number;
}

export function TextShimmer({
  children,
  className,
  duration = 2.5,
}: TextShimmerProps) {
  return (
    <motion.span
      className={cn(
        'inline-block bg-[linear-gradient(110deg,#94a3b8,45%,#00f0ff,55%,#94a3b8)] bg-[length:250%_100%] bg-clip-text text-transparent',
        className
      )}
      animate={{
        backgroundPosition: ['100% 0', '-100% 0'],
      }}
      transition={{
        repeat: Infinity,
        duration,
        ease: 'linear',
      }}
    >
      {children}
    </motion.span>
  );
}
