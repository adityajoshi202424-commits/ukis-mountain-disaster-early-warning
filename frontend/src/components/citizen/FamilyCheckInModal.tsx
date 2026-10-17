'use client';

import React, { useState } from 'react';
import { X, Users, Search, CheckCircle2, Clock, MapPin } from 'lucide-react';

interface FamilyCheckInModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function FamilyCheckInModal({ isOpen, onClose }: FamilyCheckInModalProps) {
  const [queryPhone, setQueryPhone] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!queryPhone.trim()) return;

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const res = await fetch(`/api/v1/citizen/check-in/status?phone=${encodeURIComponent(queryPhone.trim())}`);
      if (!res.ok) throw new Error('Search failed');
      const data = await res.json();
      setResults(data.records || []);
    } catch {
      setError('Could not complete safety check-in lookup. Please check network.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs" onClick={onClose} aria-hidden="true" />
      <div className="relative w-full max-w-md bg-white rounded-xl shadow-2xl border border-slate-200 overflow-hidden z-10">
        <div className="px-5 py-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Users className="w-5 h-5 text-blue-700" />
            <h3 className="font-bold text-sm text-slate-900">Verify Loved Ones&apos; Safety</h3>
          </div>
          <button onClick={onClose} className="p-1 rounded text-slate-400 hover:text-slate-700">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-5 space-y-4 text-sm">
          <p className="text-xs text-slate-600">
            Enter your mobile number to see if family members currently in Uttarakhand have checked in and linked you.
          </p>

          <form onSubmit={handleSearch} className="flex gap-2">
            <input
              type="tel"
              required
              placeholder="Your phone: +91 98765 43210"
              value={queryPhone}
              onChange={(e) => setQueryPhone(e.target.value)}
              className="flex-1 border border-slate-300 rounded p-2 text-slate-900 text-sm focus:ring-2 focus:ring-blue-600 focus:outline-none"
            />
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-blue-700 hover:bg-blue-800 text-white rounded text-xs font-bold transition-colors"
            >
              {loading ? 'Searching...' : 'Search'}
            </button>
          </form>

          {error && (
            <div className="p-3 bg-red-50 border border-red-200 text-red-800 rounded text-xs font-bold">
              {error}
            </div>
          )}

          {results !== null && (
            <div className="space-y-2 mt-3">
              <h4 className="text-xs font-bold uppercase text-slate-500 tracking-wider">
                Lookup Results ({results.length})
              </h4>
              {results.length === 0 ? (
                <div className="p-4 bg-slate-50 border border-slate-200 rounded text-center text-xs text-slate-500">
                  No active check-ins found linked to this number.
                </div>
              ) : (
                results.map((rec: any, idx: number) => (
                  <div
                    key={idx}
                    className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg flex items-center justify-between"
                  >
                    <div className="space-y-0.5">
                      <div className="flex items-center gap-1.5 font-bold text-xs text-emerald-950">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-700" />
                        <span>Status: {rec.status}</span>
                      </div>
                      <div className="text-[11px] text-slate-600 flex items-center gap-1">
                        <MapPin className="w-3 h-3 text-slate-400" />
                        <span>{rec.district} District</span>
                      </div>
                    </div>
                    <span className="text-[10px] font-mono text-slate-500">
                      {new Date(rec.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                ))
              )}
            </div>
          )}
        </div>

        <div className="px-5 py-3 border-t border-slate-200 bg-slate-50 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 border border-slate-300 rounded text-xs font-bold text-slate-700 hover:bg-slate-100"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
