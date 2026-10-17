'use client';

import React from 'react';

interface DataSourceItem {
  stream_id?: string;
  name: string;
  type?: string;
  provider: string;
  resolution?: string;
  latency?: string;
  parameters?: string;
  url?: string;
  license?: string;
}

interface DataSourcesModalProps {
  isOpen?: boolean;
  onClose: () => void;
  sources: DataSourceItem[];
}

export default function DataSourcesModal({ isOpen = true, onClose, sources }: DataSourcesModalProps) {
  if (isOpen === false) return null;

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        backgroundColor: 'rgba(15, 23, 42, 0.5)',
        backdropFilter: 'blur(4px)',
        zIndex: 9999,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '20px',
      }}
      onClick={onClose}
    >
      <div
        style={{
          backgroundColor: '#FFFFFF',
          border: '1px solid #E2E8F0',
          width: '100%',
          maxWidth: '780px',
          maxHeight: '85vh',
          overflowY: 'auto',
          borderRadius: '12px',
          padding: '24px',
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #E2E8F0', paddingBottom: '12px', marginBottom: '16px' }}>
          <div>
            <h2 style={{ fontSize: '15px', fontWeight: 800, color: '#002E6D', margin: 0, letterSpacing: '0.02em', textTransform: 'uppercase' }}>
              Authoritative Data Sources &amp; Provenance Registry
            </h2>
            <p style={{ fontSize: '12px', color: '#64748B', margin: '4px 0 0 0' }}>
              Uttarakhand State Disaster Management Authority &bull; Open Multi-Hazard Telemetry
            </p>
          </div>
          <button
            onClick={onClose}
            style={{
              background: '#F1F5F9',
              border: '1px solid #CBD5E1',
              color: '#334155',
              fontSize: '14px',
              fontWeight: 700,
              cursor: 'pointer',
              borderRadius: '6px',
              width: '28px',
              height: '28px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            ✕
          </button>
        </div>

        <p style={{ fontSize: '12px', color: '#475569', lineHeight: 1.5, marginBottom: '16px', backgroundColor: '#F8FAFC', padding: '10px 14px', borderRadius: '8px', border: '1px solid #E2E8F0' }}>
          <strong style={{ color: '#0F172A' }}>Rule 1 &amp; Rule 2 Compliance:</strong> All observations in this platform originate from official operational infrastructure with full provenance metadata. No values are fabricated or synthetically substituted.
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {sources.map((src, i) => (
            <div key={src.stream_id || i} style={{ backgroundColor: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '8px', padding: '14px 16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                <h4 style={{ fontSize: '13px', fontWeight: 700, color: '#0F172A', margin: 0 }}>{src.name}</h4>
                {src.license && (
                  <span style={{ fontSize: '10px', fontWeight: 700, backgroundColor: '#E0F2FE', color: '#0369A1', padding: '2px 8px', borderRadius: '4px' }}>
                    {src.license}
                  </span>
                )}
              </div>
              <p style={{ fontSize: '11px', color: '#64748B', margin: '0 0 8px 0', fontWeight: 500 }}>
                {src.type ? `${src.type} • ` : ''}{src.provider}
              </p>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px', fontSize: '11px', color: '#475569' }}>
                {src.resolution && <div><strong style={{ color: '#0F172A' }}>Resolution:</strong> {src.resolution}</div>}
                {src.latency && <div><strong style={{ color: '#0F172A' }}>Latency:</strong> {src.latency}</div>}
                {src.parameters && <div style={{ gridColumn: 'span 2' }}><strong style={{ color: '#0F172A' }}>Parameters:</strong> {src.parameters}</div>}
                {src.url && (
                  <div style={{ gridColumn: 'span 2' }}>
                    <strong style={{ color: '#0F172A' }}>Endpoint:</strong>{' '}
                    <a href={src.url} target="_blank" rel="noreferrer" style={{ color: '#0284C7', textDecoration: 'underline' }}>
                      {src.url}
                    </a>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        <div style={{ marginTop: '20px', paddingTop: '16px', borderTop: '1px solid #E2E8F0', textAlign: 'right' }}>
          <button
            onClick={onClose}
            style={{
              backgroundColor: '#002E6D',
              border: 'none',
              color: '#FFFFFF',
              padding: '8px 18px',
              fontSize: '12px',
              fontWeight: 700,
              cursor: 'pointer',
              borderRadius: '6px',
              boxShadow: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
            }}
          >
            Close Registry
          </button>
        </div>
      </div>
    </div>
  );
}
