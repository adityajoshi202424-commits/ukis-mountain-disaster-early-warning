'use client';

import React from 'react';
import { X, MapPin, Clock, ShieldAlert, PhoneCall, FileText } from 'lucide-react';
import { CapAlertItem } from '@/types/shared_cap';

interface CapDetailModalProps {
  alert: CapAlertItem | null;
  onClose: () => void;
}

export function CapDetailModal({ alert, onClose }: CapDetailModalProps) {
  if (!alert) return null;

  const anyAlert = alert as any;
  const identifier = alert.identifier || anyAlert.id || 'CAP-000';
  const headline = anyAlert.headline || alert.localized?.['en-IN']?.headline || 'Emergency Warning';
  const instruction = anyAlert.instruction || alert.localized?.['en-IN']?.instruction || '';
  const description = anyAlert.description || alert.localized?.['en-IN']?.description || 'No further details provided.';
  const district = alert.districts?.[0] || anyAlert.district || 'Chamoli';
  const riverBasin = anyAlert.river_basin || '';
  const areaDesc = alert.area?.areaDesc || anyAlert.area_desc || `${district} District`;
  const effectiveTime = alert.effective || anyAlert.effective_time || new Date().toISOString();
  const expiresTime = alert.expires || anyAlert.expires_time || new Date(Date.now() + 86400000).toISOString();
  const senderAgency = alert.senderName || alert.sender || anyAlert.sender_agency || 'DMMC Uttarakhand';
  const urgency = alert.urgency || anyAlert.urgency || 'Immediate';
  const certainty = alert.certainty || anyAlert.certainty || 'Observed';
  const scope = alert.scope || anyAlert.scope || 'Public';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Dialog Box */}
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="cap-dialog-title"
        className="relative w-full max-w-2xl bg-white rounded-xl shadow-2xl border border-slate-200 overflow-hidden z-10 flex flex-col max-h-[90vh]"
      >
        {/* Modal Header */}
        <div className="px-5 py-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span
              className={`px-2.5 py-0.5 rounded text-xs font-bold ${
                alert.severity === 'CRITICAL'
                  ? 'bg-red-700 text-white'
                  : alert.severity === 'SEVERE'
                  ? 'bg-amber-700 text-white'
                  : 'bg-amber-800 text-white'
              }`}
            >
              {alert.severity}
            </span>
            <span className="text-xs font-mono text-slate-500">
              CAP 1.2 &bull; {identifier}
            </span>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded text-slate-400 hover:text-slate-700 hover:bg-slate-200 transition-colors"
            aria-label="Close dialog"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-5 sm:p-6 overflow-y-auto space-y-4 text-sm">
          <div>
            <h2 id="cap-dialog-title" className="text-xl font-bold text-slate-900">
              {headline}
            </h2>
            <div className="flex flex-wrap items-center gap-3 mt-2 text-xs text-slate-500">
              <span className="flex items-center gap-1 font-semibold text-slate-700">
                <MapPin className="w-3.5 h-3.5 text-slate-400" />
                {district} District {riverBasin ? `(${riverBasin})` : ''}
              </span>
              <span>&bull;</span>
              <span className="flex items-center gap-1">
                <Clock className="w-3.5 h-3.5 text-slate-400" />
                Effective: {new Date(effectiveTime).toLocaleString()}
              </span>
              <span>&bull;</span>
              <span>Expires: {new Date(expiresTime).toLocaleString()}</span>
            </div>
          </div>

          {/* Actionable Instruction Box */}
          {instruction && (
            <div className="p-4 bg-red-50 border-l-4 border-red-700 rounded text-red-950">
              <h4 className="font-bold text-xs uppercase tracking-wider text-red-800 mb-1">
                Mandatory Emergency Instructions
              </h4>
              <p className="font-medium text-sm leading-relaxed">{instruction}</p>
            </div>
          )}

          {/* Description */}
          <div className="space-y-1.5">
            <h4 className="text-xs font-bold uppercase text-slate-500 tracking-wider">
              Situation Description
            </h4>
            <p className="text-slate-700 leading-relaxed bg-slate-50 border border-slate-200 p-3 rounded text-sm">
              {description}
            </p>
          </div>

          {/* Geographic Affected Area */}
          <div className="space-y-1.5">
            <h4 className="text-xs font-bold uppercase text-slate-500 tracking-wider">
              Affected Corridors &amp; Elevation
            </h4>
            <div className="bg-slate-50 border border-slate-200 p-3 rounded space-y-1 text-xs text-slate-700">
              <p><strong>Geographic Descriptor:</strong> {areaDesc}</p>
              {anyAlert.elevation_range_m && (
                <p>
                  <strong>Elevation Range:</strong> {anyAlert.elevation_range_m[0]}m – {anyAlert.elevation_range_m[1]}m
                </p>
              )}
            </div>
          </div>

          {/* Technical Protocol Metadata */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 border-t border-slate-100 text-xs">
            <div className="p-2 bg-slate-50 rounded border border-slate-200">
              <span className="text-slate-500 block text-[10px] uppercase">Urgency</span>
              <strong className="text-slate-900">{urgency}</strong>
            </div>
            <div className="p-2 bg-slate-50 rounded border border-slate-200">
              <span className="text-slate-500 block text-[10px] uppercase">Certainty</span>
              <strong className="text-slate-900">{certainty}</strong>
            </div>
            <div className="p-2 bg-slate-50 rounded border border-slate-200">
              <span className="text-slate-500 block text-[10px] uppercase">Scope</span>
              <strong className="text-slate-900">{scope}</strong>
            </div>
            <div className="p-2 bg-slate-50 rounded border border-slate-200">
              <span className="text-slate-500 block text-[10px] uppercase">Issuer</span>
              <strong className="text-slate-900">{senderAgency}</strong>
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="px-5 py-3 border-t border-slate-200 bg-slate-50 flex items-center justify-between">
          <a
            href="tel:112"
            className="inline-flex items-center gap-2 bg-red-700 hover:bg-red-800 text-white font-bold text-xs px-4 py-2 rounded-md shadow-xs transition-colors"
          >
            <PhoneCall className="w-4 h-4" />
            <span>Call 112 for Assistance</span>
          </a>
          <button
            onClick={onClose}
            className="text-xs font-bold text-slate-700 bg-white border border-slate-300 hover:bg-slate-100 px-4 py-2 rounded-md transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
