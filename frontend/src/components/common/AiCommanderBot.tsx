'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Bot, Send, X, ShieldAlert, Sparkles, MapPin, Navigation, Compass, AlertTriangle, CheckCircle2 } from 'lucide-react';

interface ChatMessage {
  id: string;
  sender: 'user' | 'bot';
  text: string;
  timestamp: string;
  stationId?: string;
  activeTier?: string;
  verifiedShelter?: string;
  verifiedRoute?: string;
  confidence?: string;
  sopCitation?: string;
  auditBadge?: string;
}

const STATION_OPTIONS = [
  { id: 'UK-CHAMOLI-01', name: 'Chamoli (Joshimath / Tapovan)', district: 'Chamoli' },
  { id: 'UK-RUDRAPRAYAG-02', name: 'Rudraprayag (Kedarnath Axis)', district: 'Rudraprayag' },
  { id: 'UK-UTTARKASHI-03', name: 'Uttarkashi (Bhagirathi Gorge)', district: 'Uttarkashi' },
  { id: 'UK-PAURI-04', name: 'Pauri Garhwal (Alaknanda Basin)', district: 'Pauri' },
];

const SUGGESTED_QUERIES = [
  'What is the safest evacuation route and shelter for Joshimath if the gorge floods?',
  'Why did the system issue an alert? Explain current hazard scores.',
  'What is the active alert tier and situation report for this station?',
  'What are the mandatory USDMA SOP deployment directives for SDRF teams?',
];

export function AiCommanderBot() {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedStation, setSelectedStation] = useState('UK-CHAMOLI-01');
  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      sender: 'bot',
      text: 'Namaste. I am the UKIS AI Mountain Disaster Commander Assistant. I provide real-time, SOP-grounded emergency directives and dynamic evacuation corridors strictly based on live telemetry (Open-Meteo, GloFAS, USGS) and USDMA Standard Operating Procedures. Zero hallucination guaranteed. How can I assist your command team?',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      activeTier: 'YELLOW',
      sopCitation: 'USDMA SOP-01 (Mountain Emergency Operational Protocol)',
      auditBadge: '0% Fabrication • Grounded in Real Telemetry',
    },
  ]);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isOpen]);

  const handleSendQuery = async (queryText?: string) => {
    const textToSend = queryText || inputQuery;
    if (!textToSend.trim() || loading) return;

    const userMsgId = `user-${Date.now()}`;
    const userMsg: ChatMessage = {
      id: userMsgId,
      sender: 'user',
      text: textToSend,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      stationId: selectedStation,
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!queryText) setInputQuery('');
    setLoading(true);

    try {
      const res = await fetch('/api/v1/mountain/commander/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          station_id: selectedStation,
          query: textToSend,
        }),
      });

      if (!res.ok) {
        throw new Error(`Server responded with ${res.status}`);
      }

      const data = await res.json();
      const botMsg: ChatMessage = {
        id: `bot-${Date.now()}`,
        sender: 'bot',
        text: data.grounded_response || 'No directive returned from decision engine.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        stationId: data.station_id,
        activeTier: data.active_tier,
        verifiedShelter: data.verified_shelter,
        verifiedRoute: data.verified_route,
        confidence: data.confidence_interval,
        sopCitation: data.grounded_sop_citation,
        auditBadge: data.data_fabrication_audit,
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: `bot-err-${Date.now()}`,
        sender: 'bot',
        text: `Unable to query mountain hazard engine: ${err.message || 'Network timeout'}. The system fails closed when telemetry is unreachable.`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        activeTier: 'FAIL_CLOSED',
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Floating Action Button */}
      <div className="fixed bottom-6 right-6 z-50">
        {!isOpen ? (
          <button
            onClick={() => setIsOpen(true)}
            className="flex items-center gap-2 px-4 py-3 bg-gradient-to-r from-red-700 via-rose-700 to-amber-700 hover:from-red-800 hover:to-amber-800 text-white rounded-full shadow-xl hover:shadow-2xl transition-all duration-300 font-bold text-xs uppercase tracking-wider border-2 border-amber-300/40 transform hover:-translate-y-0.5"
            aria-label="Open AI Mountain Commander Assistant"
          >
            <div className="relative">
              <Bot className="w-5 h-5 text-amber-200" />
              <span className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping" />
              <span className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-emerald-500" />
            </div>
            <span>AI Disaster Commander</span>
            <span className="bg-white/20 text-white text-[10px] px-2 py-0.5 rounded-full ml-1 font-mono">
              Live Bot
            </span>
          </button>
        ) : null}
      </div>

      {/* Slide-out Interactive Chat Panel */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 z-50 w-full max-w-lg bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl overflow-hidden flex flex-col h-[620px] transition-all duration-300 animate-in fade-in slide-in-from-bottom-5">
          {/* Header */}
          <div className="px-5 py-3.5 bg-gradient-to-r from-slate-950 via-slate-900 to-slate-950 border-b border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-red-600/20 border border-red-500/40 flex items-center justify-center">
                <Bot className="w-4 h-4 text-red-400" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-xs font-bold text-white tracking-wide uppercase">
                    AI Mountain Commander Assistant
                  </h3>
                  <span className="px-1.5 py-0.2 bg-emerald-950 border border-emerald-500/50 text-emerald-400 text-[9px] font-mono rounded">
                    SOP Grounded
                  </span>
                </div>
                <p className="text-[10px] text-slate-400">
                  USDMA Incident Command Decision Support &bull; Zero Hallucination
                </p>
              </div>
            </div>

            <button
              onClick={() => setIsOpen(false)}
              className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition"
              title="Close Assistant"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Station Selector Bar */}
          <div className="px-4 py-2 bg-slate-950/70 border-b border-slate-800 flex items-center justify-between gap-2 text-xs">
            <div className="flex items-center gap-1.5 text-slate-400 text-[11px]">
              <MapPin className="w-3.5 h-3.5 text-red-400" />
              <span>Observational Station:</span>
            </div>
            <select
              value={selectedStation}
              onChange={(e) => setSelectedStation(e.target.value)}
              className="bg-slate-900 text-slate-200 border border-slate-700 rounded px-2.5 py-1 text-xs focus:outline-none focus:border-red-500"
            >
              {STATION_OPTIONS.map((stn) => (
                <option key={stn.id} value={stn.id}>
                  {stn.name}
                </option>
              ))}
            </select>
          </div>

          {/* Messages Stream */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-900/90 text-xs">
            {messages.map((m) => (
              <div
                key={m.id}
                className={`flex flex-col ${m.sender === 'user' ? 'items-end' : 'items-start'}`}
              >
                <div
                  className={`max-w-[90%] rounded-xl p-3.5 space-y-2 ${
                    m.sender === 'user'
                      ? 'bg-red-700 text-white rounded-br-none shadow-md'
                      : 'bg-slate-800/90 border border-slate-700 text-slate-200 rounded-bl-none shadow-sm'
                  }`}
                >
                  {/* Sender Tag */}
                  <div className="flex items-center justify-between gap-4 text-[10px] opacity-75 font-mono">
                    <span>{m.sender === 'user' ? 'Emergency Commander' : 'UKIS Early-Warning Engine'}</span>
                    <span>{m.timestamp}</span>
                  </div>

                  {/* Main Text */}
                  <p className="leading-relaxed whitespace-pre-wrap">{m.text}</p>

                  {/* Grounded Decision Cards (Only for Bot responses) */}
                  {m.sender === 'bot' && (m.verifiedShelter || m.verifiedRoute || m.activeTier) && (
                    <div className="mt-2 pt-2 border-t border-slate-700/80 space-y-1.5 text-[11px]">
                      {m.activeTier && (
                        <div className="flex items-center justify-between">
                          <span className="text-slate-400">Hazard Tier:</span>
                          <span
                            className={`px-2 py-0.5 rounded font-mono font-bold text-[10px] ${
                              m.activeTier === 'RED'
                                ? 'bg-red-950 text-red-400 border border-red-800'
                                : m.activeTier === 'ORANGE'
                                ? 'bg-amber-950 text-amber-400 border border-amber-800'
                                : 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                            }`}
                          >
                            {m.activeTier} {m.confidence ? `• ${m.confidence}` : ''}
                          </span>
                        </div>
                      )}

                      {m.verifiedShelter && (
                        <div className="flex items-start gap-1.5 bg-slate-900/60 p-2 rounded border border-slate-700">
                          <Navigation className="w-3.5 h-3.5 text-emerald-400 mt-0.5 shrink-0" />
                          <div>
                            <span className="text-slate-400 font-mono text-[10px] block">
                              Safe Haven Shelter:
                            </span>
                            <span className="text-emerald-300 font-bold">
                              {m.verifiedShelter}
                            </span>
                          </div>
                        </div>
                      )}

                      {m.verifiedRoute && (
                        <div className="flex items-start gap-1.5 bg-slate-900/60 p-2 rounded border border-slate-700">
                          <Compass className="w-3.5 h-3.5 text-blue-400 mt-0.5 shrink-0" />
                          <div>
                            <span className="text-slate-400 font-mono text-[10px] block">
                              Computed Evacuation Corridor:
                            </span>
                            <span className="text-blue-200 font-mono">
                              {m.verifiedRoute}
                            </span>
                          </div>
                        </div>
                      )}

                      {m.sopCitation && (
                        <div className="text-[10px] text-slate-400 font-mono flex items-center gap-1 pt-1">
                          <CheckCircle2 className="w-3 h-3 text-emerald-400 shrink-0" />
                          <span>Citation: {m.sopCitation}</span>
                        </div>
                      )}

                      {m.auditBadge && (
                        <div className="text-[9px] text-amber-300 font-mono bg-amber-950/40 px-2 py-0.5 rounded border border-amber-800/40">
                          🛡 {m.auditBadge}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex items-center gap-2 text-slate-400 text-xs italic bg-slate-800/50 p-2.5 rounded-lg border border-slate-700 w-fit">
                <Sparkles className="w-3.5 h-3.5 animate-spin text-amber-400" />
                <span>Consulting live hydrological telemetry &amp; USDMA SOPs...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick Query Suggestions */}
          <div className="p-2.5 bg-slate-950/80 border-t border-slate-800 flex gap-1.5 overflow-x-auto text-[11px] no-scrollbar">
            {SUGGESTED_QUERIES.map((q, idx) => (
              <button
                key={idx}
                onClick={() => handleSendQuery(q)}
                disabled={loading}
                className="whitespace-nowrap px-2.5 py-1 bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-white rounded-full border border-slate-700 transition shrink-0"
              >
                {q.length > 36 ? q.slice(0, 36) + '...' : q}
              </button>
            ))}
          </div>

          {/* Input Box */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendQuery();
            }}
            className="p-3 bg-slate-950 border-t border-slate-800 flex items-center gap-2"
          >
            <input
              type="text"
              placeholder="Ask evacuation route, alert cause, or SOP directive..."
              value={inputQuery}
              onChange={(e) => setInputQuery(e.target.value)}
              disabled={loading}
              className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-red-500"
            />
            <button
              type="submit"
              disabled={loading || !inputQuery.trim()}
              className="p-2 bg-red-700 hover:bg-red-800 disabled:opacity-50 text-white rounded-lg transition"
              title="Send to Commander Engine"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      )}
    </>
  );
}
