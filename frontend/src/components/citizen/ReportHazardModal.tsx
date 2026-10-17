'use client';

import React, { useState } from 'react';
import { X, AlertTriangle, MapPin, Send } from 'lucide-react';
import { UttarakhandDistrict, UTTARAKHAND_DISTRICTS } from '@/types/shared_cap';

interface ReportHazardModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function ReportHazardModal({ isOpen, onClose }: ReportHazardModalProps) {
  const [district, setDistrict] = useState<UttarakhandDistrict>('Chamoli');
  const [hazardType, setHazardType] = useState('LANDSLIDE');
  const [description, setDescription] = useState('');
  const [landmark, setLandmark] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [statusMsg, setStatusMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setStatusMsg(null);

    try {
      const res = await fetch('/api/v1/citizen/reports/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          district,
          hazard_type: hazardType,
          description,
          landmark,
          latitude: 30.5526, // Default Chamoli baseline
          longitude: 79.5632,
        }),
      });

      if (!res.ok) {
        const d = await res.json().catch(() => ({}));
        throw new Error(d.detail || 'Submission failed');
      }

      setStatusMsg({
        type: 'success',
        text: 'Report submitted! It is quarantined as UNVERIFIED pending SDRF field verification.',
      });
      setTimeout(() => onClose(), 2500);
    } catch (err: any) {
      setStatusMsg({ type: 'error', text: err.message || 'Error submitting report' });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs" onClick={onClose} aria-hidden="true" />
      <div className="relative w-full max-w-md bg-white rounded-xl shadow-2xl border border-slate-200 overflow-hidden z-10">
        <div className="px-5 py-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-amber-700" />
            <h3 className="font-bold text-sm text-slate-900">Report Mountain Hazard</h3>
          </div>
          <button onClick={onClose} className="p-1 rounded text-slate-400 hover:text-slate-700">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-5 space-y-4 text-sm">
          <div className="p-3 bg-amber-50 border border-amber-200 rounded text-xs text-amber-900 font-medium">
            Reports enter the DMMC Operations Queue as <strong>UNVERIFIED</strong> to prevent panic. Field teams inspect every reported incident.
          </div>

          {statusMsg && (
            <div
              className={`p-3 rounded text-xs font-bold ${
                statusMsg.type === 'success'
                  ? 'bg-emerald-50 text-emerald-900 border border-emerald-300'
                  : 'bg-red-50 text-red-900 border border-red-300'
              }`}
            >
              {statusMsg.text}
            </div>
          )}

          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">Hazard Category</label>
            <select
              value={hazardType}
              onChange={(e) => setHazardType(e.target.value)}
              className="w-full border border-slate-300 rounded p-2 text-slate-900 text-sm focus:ring-2 focus:ring-blue-600 focus:outline-none"
            >
              <option value="LANDSLIDE">Road Blockage / Landslide Debris</option>
              <option value="FLASH_FLOOD">Flash Flood Surge / River Rise</option>
              <option value="CLOUDBURST">Sudden Heavy Cloudburst Torrent</option>
              <option value="AVALANCHE">Snow Avalanche / Crevasse Breach</option>
              <option value="BRIDGE_OUT">Bridge / Culvert Structural Damage</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">District</label>
            <select
              value={district}
              onChange={(e) => setDistrict(e.target.value as UttarakhandDistrict)}
              className="w-full border border-slate-300 rounded p-2 text-slate-900 text-sm focus:ring-2 focus:ring-blue-600 focus:outline-none"
            >
              {UTTARAKHAND_DISTRICTS.map((d) => (
                <option key={d} value={d}>{d} District</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">Specific Location / Milestone / Highway</label>
            <input
              type="text"
              required
              placeholder="e.g. NH-58 near Sirobagarh, km 142"
              value={landmark}
              onChange={(e) => setLandmark(e.target.value)}
              className="w-full border border-slate-300 rounded p-2 text-slate-900 text-sm focus:ring-2 focus:ring-blue-600 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">Incident Observation Details</label>
            <textarea
              required
              rows={3}
              placeholder="Describe road conditions, water volume, or active debris fall..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full border border-slate-300 rounded p-2 text-slate-900 text-sm focus:ring-2 focus:ring-blue-600 focus:outline-none"
            />
          </div>

          <div className="pt-2 flex justify-end gap-2">
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
              className="px-4 py-1.5 bg-amber-700 hover:bg-amber-800 text-white rounded text-xs font-bold shadow-xs transition-colors"
            >
              {submitting ? 'Submitting...' : 'Submit Hazard Report'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
