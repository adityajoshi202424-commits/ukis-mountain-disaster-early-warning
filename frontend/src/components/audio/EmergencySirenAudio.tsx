'use client';

import React, { useEffect, useRef, useState, useCallback } from 'react';
import { Volume2, VolumeX, AlertTriangle, Play, Square, BellRing } from 'lucide-react';

interface EmergencySirenAudioProps {
  isTriggered: boolean;
  alertLevel?: string;
  locationName?: string;
}

export default function EmergencySirenAudio({
  isTriggered,
  alertLevel = 'RED',
  locationName = 'Joshimath / Tapovan Sector',
}: EmergencySirenAudioProps) {
  const [isAudioUnlocked, setIsAudioUnlocked] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [manualTesting, setManualTesting] = useState(false);

  const audioCtxRef = useRef<AudioContext | null>(null);
  const osc1Ref = useRef<OscillatorNode | null>(null);
  const osc2Ref = useRef<OscillatorNode | null>(null);
  const gainNodeRef = useRef<GainNode | null>(null);
  const sweepIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Initialize or resume AudioContext
  const getAudioContext = useCallback(() => {
    if (!audioCtxRef.current) {
      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      audioCtxRef.current = new AudioCtx();
    }
    if (audioCtxRef.current.state === 'suspended') {
      audioCtxRef.current.resume();
    }
    return audioCtxRef.current;
  }, []);

  // Unlock AudioContext on the very first user interaction anywhere on the page
  useEffect(() => {
    const handleFirstInteraction = () => {
      try {
        const ctx = getAudioContext();
        if (ctx && ctx.state === 'running') {
          setIsAudioUnlocked(true);
          window.removeEventListener('click', handleFirstInteraction);
          window.removeEventListener('keydown', handleFirstInteraction);
          window.removeEventListener('touchstart', handleFirstInteraction);
        }
      } catch (e) {
        console.warn('Audio unlock error:', e);
      }
    };

    window.addEventListener('click', handleFirstInteraction);
    window.addEventListener('keydown', handleFirstInteraction);
    window.addEventListener('touchstart', handleFirstInteraction);

    return () => {
      window.removeEventListener('click', handleFirstInteraction);
      window.removeEventListener('keydown', handleFirstInteraction);
      window.removeEventListener('touchstart', handleFirstInteraction);
    };
  }, [getAudioContext]);

  // Authentic Civil Defence Dual-Tone Siren Synthesizer
  const startSiren = useCallback(() => {
    if (isMuted) return;
    try {
      const ctx = getAudioContext();
      if (!ctx) return;

      // Stop previous oscillators if already running
      stopSiren();

      // Main siren oscillator
      const osc1 = ctx.createOscillator();
      const osc2 = ctx.createOscillator();
      const gain = ctx.createGain();

      osc1.type = 'sawtooth';
      osc2.type = 'sine';

      // Base frequencies
      osc1.frequency.setValueAtTime(800, ctx.currentTime);
      osc2.frequency.setValueAtTime(805, ctx.currentTime); // Slight detune for urgency thickness

      // Volume envelope
      gain.gain.setValueAtTime(0.12, ctx.currentTime);

      osc1.connect(gain);
      osc2.connect(gain);
      gain.connect(ctx.destination);

      osc1.start();
      osc2.start();

      osc1Ref.current = osc1;
      osc2Ref.current = osc2;
      gainNodeRef.current = gain;
      setIsPlaying(true);

      // Modulate frequency: Wailing siren sweep between 750Hz and 1150Hz
      let sweepHigh = true;
      sweepIntervalRef.current = setInterval(() => {
        if (!osc1Ref.current || !osc2Ref.current || !audioCtxRef.current) return;
        const now = audioCtxRef.current.currentTime;
        const target = sweepHigh ? 1150 : 750;
        osc1Ref.current.frequency.exponentialRampToValueAtTime(target, now + 0.4);
        osc2Ref.current.frequency.exponentialRampToValueAtTime(target + 5, now + 0.4);
        sweepHigh = !sweepHigh;
      }, 450);
    } catch (err) {
      console.warn('Audio playback error:', err);
    }
  }, [getAudioContext, isMuted]);

  const stopSiren = useCallback(() => {
    if (sweepIntervalRef.current) {
      clearInterval(sweepIntervalRef.current);
      sweepIntervalRef.current = null;
    }
    if (osc1Ref.current) {
      try {
        osc1Ref.current.stop();
        osc1Ref.current.disconnect();
      } catch (e) {}
      osc1Ref.current = null;
    }
    if (osc2Ref.current) {
      try {
        osc2Ref.current.stop();
        osc2Ref.current.disconnect();
      } catch (e) {}
      osc2Ref.current = null;
    }
    setIsPlaying(false);
    setManualTesting(false);
  }, []);

  // Trigger siren automatically when warning is active or in manual test mode
  useEffect(() => {
    if ((isTriggered || manualTesting) && !isMuted) {
      startSiren();
    } else {
      stopSiren();
    }
    return () => {
      stopSiren();
    };
  }, [isTriggered, manualTesting, isMuted, startSiren, stopSiren]);

  const toggleManualTest = () => {
    const ctx = getAudioContext();
    setIsAudioUnlocked(true);
    if (isPlaying || manualTesting) {
      stopSiren();
    } else {
      setIsMuted(false);
      setManualTesting(true);
    }
  };

  return (
    <div className="fixed bottom-12 right-6 z-50 flex items-center gap-3 bg-slate-900/95 border border-sky-500/30 px-3.5 py-2.5 rounded-xl shadow-2xl backdrop-blur-2xl">
      {/* Visual Siren Status Indicator */}
      <div className="flex items-center gap-2">
        <span className="relative flex h-3 w-3">
          {isPlaying && (
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
          )}
          <span
            className={`relative inline-flex rounded-full h-3 w-3 ${
              isPlaying ? 'bg-red-500 shadow-[0_0_10px_#ef4444]' : 'bg-emerald-500'
            }`}
          ></span>
        </span>
        <div className="flex flex-col">
          <span className="text-[10px] font-mono font-bold text-slate-200 uppercase tracking-wide">
            {isPlaying ? '🚨 SIREN TRANSMITTING' : '🔊 EMERGENCY AUDIO'}
          </span>
          <span className="text-[9px] font-mono text-slate-400">
            {isPlaying ? 'Civil Defence Audio Alarm' : 'Auto-triggers on flood breach'}
          </span>
        </div>
      </div>

      {/* Manual Test / Stop Siren Button */}
      <button
        onClick={toggleManualTest}
        className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-[10px] font-mono font-bold transition-all ${
          isPlaying
            ? 'bg-red-600 hover:bg-red-700 text-white shadow-[0_0_16px_rgba(239,68,68,0.5)] animate-pulse'
            : 'bg-sky-600 hover:bg-sky-500 text-white shadow-[0_0_12px_rgba(14,165,233,0.3)]'
        }`}
        title={isPlaying ? 'Stop Siren Test' : 'Test Emergency Siren Audio'}
      >
        {isPlaying ? (
          <>
            <Square className="w-3 h-3 fill-white" />
            <span>STOP SIREN</span>
          </>
        ) : (
          <>
            <Play className="w-3 h-3 fill-white" />
            <span>TEST SIREN</span>
          </>
        )}
      </button>

      {/* Mute Toggle Button */}
      <button
        onClick={() => {
          if (isMuted) {
            setIsMuted(false);
            if (isTriggered || manualTesting) startSiren();
          } else {
            setIsMuted(true);
            stopSiren();
          }
        }}
        className={`p-1.5 rounded-lg border transition-colors ${
          isMuted
            ? 'bg-slate-800 border-slate-700 text-slate-500'
            : 'bg-slate-800/80 border-sky-500/30 text-sky-400 hover:text-sky-200'
        }`}
        title={isMuted ? 'Unmute Emergency Siren' : 'Mute Emergency Siren'}
      >
        {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
      </button>
    </div>
  );
}
