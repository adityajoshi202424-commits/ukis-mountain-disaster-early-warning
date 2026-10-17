'use client';

import React, { useState } from 'react';
import { X, ShieldCheck, Phone, Users, Trash2 } from 'lucide-react';
import { UttarakhandDistrict, UTTARAKHAND_DISTRICTS } from '@/types/shared_cap';

interface MarkSafeModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function MarkSafeModal({ isOpen, onClose }: MarkSafeModalProps) {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [status, setStatus] = useState<'SAFE' | 'NEEDS_ASSISTANCE' | 'EVACUATED'>('SAFE');
  const [district, setDistrict] = useState<UttarakhandDistrict>('Chamoli');
  const [familyContacts, setFamilyContacts] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setMessage(null);

    const linkedList = familyContacts
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean);

    try {
      const res = await fetch('/api/v1/citizen/check-in-safe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          phone_number: phoneNumber,
          status: status,
          district: district,
          linked_family_phones: linkedList,
        }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || 'Failed to submit check-in');
      }

      setMessage({
        type: 'success',
        text: 'Safety status recorded! Linked family members can now verify your safety.',
      });
      setTimeout(() => {
        onClose();
      }, 2000);
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Check-in failed' });
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteHistory = async () => {
    if (!phoneNumber) {
      alert('Please enter your phone number to erase history.');
      return;
    }
    if (!confirm('Permanently erase your safety check-in history per DPDP Act 2023?')) return;

    try {
      const res = await fetch('/api/v1/citizen/check-in/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone_number: phoneNumber }),
      });
      if (res.ok) {
        alert('Your records have been permanently erased from DMMC servers.');
        onClose();
      }
    } catch {
      alert('Failed to erase records.');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs" onClick={onClose} aria-hidden="true" />
      <div className="relative w-full max-w-md bg-white rounded-xl shadow-2xl border border-slate-200 overflow-hidden z-10">
        <div className="px-5 py-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-emerald-700" />
            <h3 className="font-bold text-sm text-slate-900">Mark Yourself Safe</h3>
          </div>
          <button onClick={onClose} className="p-1 rounded text-slate-400 hover:text-slate-700">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-5 space-y-4 text-sm">
          {message && (
            <div
              className={`p-3 rounded text-xs font-bold ${
                message.type === 'success'
                  ? 'bg-emerald-50 text-emerald-900 border border-emerald-300'
                  : 'bg-red-50 text-red-900 border border-red-300'
              }`}
            >
              {message.text}
            </div>
          )}

          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">Your Mobile Number (Stored as SHA-256 Hash)</label>
            <input
              type="tel"
              required
              placeholder="+91 98765 43210"
              value={phoneNumber}
              onChange={(e) => setPhoneNumber(e.target.value)}
              className="w-full border border-slate-300 rounded p-2 text-slate-900 text-sm focus:ring-2 focus:ring-blue-600 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">Current Safety Status</label>
            <div className="grid grid-cols-3 gap-2">
              {(['SAFE', 'EVACUATED', 'NEEDS_ASSISTANCE'] as const).map((st) => (
                <button
                  type="button"
                  key={st}
                  onClick={() => setStatus(st)}
                  className={`p-2 rounded text-xs font-bold border transition-colors ${
                    status === st
                      ? st === 'SAFE'
                        ? 'bg-emerald-700 text-white border-emerald-700'
                        : st === 'EVACUATED'
                        ? 'bg-blue-700 text-white border-blue-700'
                        : 'bg-red-700 text-white border-red-700'
                      : 'border-slate-200 text-slate-700 hover:bg-slate-50'
                  }`}
                >
                  {st.replace('_', ' ')}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">Current District</label>
            <select
              value={district}
              onChange={(e) => setDistrict(e.target.value as UttarakhandDistrict)}
              className="w-full border border-slate-300 rounded p-2 text-slate-900 text-sm focus:ring-2 focus:ring-blue-600 focus:outline-none"
            >
              {UTTARAKHAND_DISTRICTS.map((d) => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">Linked Family Numbers (Comma-separated)</label>
            <input
              type="text"
              placeholder="+91 9876543211, +91 9876543212"
              value={familyContacts}
              onChange={(e) => setFamilyContacts(e.target.value)}
              className="w-full border border-slate-300 rounded p-2 text-slate-900 text-sm focus:ring-2 focus:ring-blue-600 focus:outline-none"
            />
            <p className="text-[11px] text-slate-500 mt-1">These numbers can look up your safety check-in.</p>
          </div>

          <div className="pt-2 flex items-center justify-between gap-3">
            <button
              type="button"
              onClick={handleDeleteHistory}
              className="text-xs text-red-700 hover:text-red-900 flex items-center gap-1 font-bold"
              title="Right to Erasure (DPDP Act 2023)"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Erase History</span>
            </button>

            <div className="flex gap-2">
              <button
                type="button"
                onClick={onClose}
                className="px-3 py-1.5 border border-slate-300 rounded text-xs font-bold text-slate-700 hover:bg-slate-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={submitting}
                className="px-4 py-1.5 bg-emerald-700 hover:bg-emerald-800 text-white rounded text-xs font-bold shadow-xs transition-colors"
              >
                {submitting ? 'Submitting...' : 'Confirm Safe'}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}
