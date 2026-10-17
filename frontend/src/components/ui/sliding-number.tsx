'use client';

import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { cn } from '@/lib/utils';

interface SlidingNumberProps {
  value: number | string;
  className?: string;
  prefix?: string;
  suffix?: string;
}

export function SlidingNumber({
  value,
  className,
  prefix = '',
  suffix = '',
}: SlidingNumberProps) {
  return (
    <div className={cn('inline-flex items-center font-mono overflow-hidden', className)}>
      {prefix && <span>{prefix}</span>}
      <AnimatePresence mode="popLayout" initial={false}>
        <motion.span
          key={String(value)}
          initial={{ y: 14, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: -14, opacity: 0 }}
          transition={{ duration: 0.25, ease: 'easeOut' }}
          className="inline-block"
        >
          {value}
        </motion.span>
      </AnimatePresence>
      {suffix && <span>{suffix}</span>}
    </div>
  );
}
