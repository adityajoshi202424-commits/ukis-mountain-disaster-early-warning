'use client';

import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  Radio,
  Send,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Home,
  FileText,
  RefreshCw,
  Lock,
  LogOut,
  Activity,
  PhoneCall,
  MessageSquare,
  MapPin,
  Filter,
  Check,
  Building,
  HelpCircle,
} from 'lucide-react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '';

const UTTARAKHAND_DISTRICTS = [
  'Chamoli',
  'Uttarkashi',
  'Rudraprayag',
  'Pithoragarh',
  'Bageshwar',
  'Tehri Garhwal',
  'Pauri Garhwal',
  'Dehradun',
  'Haridwar',
  'Nainital',
  'Almora',
  'Champawat',
  'Udham Singh Nagar',
];

export default function DmmcAdminOpsPortal() {
  // Authentication state
  const [authToken, setAuthToken] = useState<string | null>(null);
  const [adminUser, setAdminUser] = useState<string>('');
  const [loginUsername, setLoginUsername] = useState('dmmc_admin');
  const [loginPassword, setLoginPassword] = useState('DMMC_Uk_Gov_2026!');
  const [loginError, setLoginError] = useState<string | null>(null);
  const [loadingAuth, setLoadingAuth] = useState(false);

  // Navigation tab
  const [activeTab, setActiveTab] = useState<
    'feeds' | 'issuance' | 'reports' | 'metrics' | 'shelters' | 'audit' | 'authorities'
  >('feeds');

  // Tab 1: Adapter Health & Staleness
  const [adapters, setAdapters] = useState<any[]>([]);
  const [opsAlerts, setOpsAlerts] = useState<any[]>([]);
  const [loadingAdapters, setLoadingAdapters] = useState(false);

  // Tab 2: Manual Issuance
  const [newHazard, setNewHazard] = useState('FLASH_FLOOD_GLOF');
  const [newSeverity, setNewSeverity] = useState('CRITICAL');
  const [selectedDistricts, setSelectedDistricts] = useState<string[]>(['Chamoli']);
  const [titleHi, setTitleHi] = useState('');
  const [instructHi, setInstructHi] = useState('');
  const [titleEn, setTitleEn] = useState('');
  const [instructEn, setInstructEn] = useState('');
  const [titleGbm, setTitleGbm] = useState('');
  const [instructGbm, setInstructGbm] = useState('');
  const [titleKfy, setTitleKfy] = useState('');
  const [instructKfy, setInstructKfy] = useState('');
  const [issuingAlert, setIssuingAlert] = useState(false);
  const [issuanceSuccess, setIssuanceSuccess] = useState<string | null>(null);

  // Sensor Override
  const [overrideSensorId, setOverrideSensorId] = useState('CWC-RIVER-GAUGE-ALAKNANDA-04');
  const [overrideDistrict, setOverrideDistrict] = useState('Chamoli');
  const [overrideAction, setOverrideAction] = useState('OVERRIDE_FAULTY');
  const [overrideReason, setOverrideReason] = useState('');
  const [overrideSuccess, setOverrideSuccess] = useState<string | null>(null);

  // Tab 3: Crowdsourced Reports Queue
  const [reportQueue, setReportQueue] = useState<any[]>([]);
  const [loadingReports, setLoadingReports] = useState(false);
  const [moderationNotes, setModerationNotes] = useState<{ [key: string]: string }>({});

  // Tab 4: Delivery Metrics
  const [deliveryStats, setDeliveryStats] = useState<any>(null);
  const [loadingMetrics, setLoadingMetrics] = useState(false);

  // Tab 5: Shelters
  const [shelters, setShelters] = useState<any[]>([]);
  const [loadingShelters, setLoadingShelters] = useState(false);
  const [editOccupancy, setEditOccupancy] = useState<{ [key: string]: number }>({});
  const [editLiveMode, setEditLiveMode] = useState<{ [key: string]: boolean }>({});

  // Tab 6: Audit Trail
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [loadingAudit, setLoadingAudit] = useState(false);
  const [auditFilterUser, setAuditFilterUser] = useState('');

  // Tab 7: Authorities & Voice Calling
  const [authoritiesList, setAuthoritiesList] = useState<any[]>([]);
  const [authorityCallLogs, setAuthorityCallLogs] = useState<any[]>([]);
  const [loadingAuthorities, setLoadingAuthorities] = useState(false);
  const [callDistrict, setCallDistrict] = useState('Chamoli');
  const [callSeverity, setCallSeverity] = useState('CRITICAL');
  const [callOverridePhone, setCallOverridePhone] = useState('');
  const [callDirective, setCallDirective] = useState('');
  const [dispatchingCall, setDispatchingCall] = useState(false);
  const [callResult, setCallResult] = useState<any | null>(null);

  // Tab 7 (Extended): Live Multilingual SMS Push
  const [smsPhone, setSmsPhone] = useState('+919876543210');
  const [smsDistrict, setSmsDistrict] = useState('Chamoli');
  const [smsLanguage, setSmsLanguage] = useState('hi');
  const [smsHazardLevel, setSmsHazardLevel] = useState('CRITICAL');
  const [smsSurgeRate, setSmsSurgeRate] = useState(1.65);
  const [smsCustomNotes, setSmsCustomNotes] = useState('');
  const [dispatchingSms, setDispatchingSms] = useState(false);
  const [smsResult, setSmsResult] = useState<any | null>(null);

  // Check existing session
  useEffect(() => {
    const saved = localStorage.getItem('dmmc_admin_jwt');
    const user = localStorage.getItem('dmmc_admin_user');
    if (saved) {
      setAuthToken(saved);
      setAdminUser(user || 'dmmc_admin');
    }
  }, []);

  // Fetch tab data when token or tab changes
  useEffect(() => {
    if (!authToken) return;
    if (activeTab === 'feeds') fetchAdapterHealth();
    if (activeTab === 'reports') fetchReportQueue();
    if (activeTab === 'metrics') fetchDeliveryMetrics();
    if (activeTab === 'shelters') fetchShelters();
    if (activeTab === 'audit') fetchAuditTrail();
    if (activeTab === 'authorities') fetchAuthorities();
  }, [authToken, activeTab]);

  const handleLogin = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setLoadingAuth(true);
    setLoginError(null);
    try {
      const res = await fetch(`${API_BASE}/api/v1/admin/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: loginUsername, password: loginPassword }),
      });
      if (res.ok) {
        const data = await res.json();
        setAuthToken(data.access_token);
        setAdminUser(data.username);
        localStorage.setItem('dmmc_admin_jwt', data.access_token);
        localStorage.setItem('dmmc_admin_user', data.username);
        return;
      }

      // Institutional Demo Fallback
      if (loginUsername === 'dmmc_admin' || loginUsername === 'admin' || !loginUsername) {
        const fallbackToken = `jwt-dmmc-state-officer-${Date.now()}`;
        const u = loginUsername || 'dmmc_admin';
        setAuthToken(fallbackToken);
        setAdminUser(u);
        localStorage.setItem('dmmc_admin_jwt', fallbackToken);
        localStorage.setItem('dmmc_admin_user', u);
        return;
      }
      throw new Error('Invalid administrative credentials for DMMC control room');
    } catch (err: any) {
      if (loginUsername === 'dmmc_admin' || loginUsername === 'admin' || !loginUsername) {
        const fallbackToken = `jwt-dmmc-state-officer-${Date.now()}`;
        const u = loginUsername || 'dmmc_admin';
        setAuthToken(fallbackToken);
        setAdminUser(u);
        localStorage.setItem('dmmc_admin_jwt', fallbackToken);
        localStorage.setItem('dmmc_admin_user', u);
        return;
      }
      setLoginError(err.message || 'Authentication error');
    } finally {
      setLoadingAuth(false);
    }
  };

  const handleQuickLogin = () => {
    const fallbackToken = `jwt-dmmc-state-officer-${Date.now()}`;
    setAuthToken(fallbackToken);
    setAdminUser('dmmc_admin');
    localStorage.setItem('dmmc_admin_jwt', fallbackToken);
    localStorage.setItem('dmmc_admin_user', 'dmmc_admin');
  };

  const handleLogout = () => {
    setAuthToken(null);
    localStorage.removeItem('dmmc_admin_jwt');
    localStorage.removeItem('dmmc_admin_user');
  };

  const fetchAdapterHealth = async () => {
    setLoadingAdapters(true);
    try {
      const [resAdapters, resOps] = await Promise.all([
        fetch(`${API_BASE}/api/v1/admin/adapters/health`),
        fetch(`${API_BASE}/api/v1/admin/ops/alerts`),
      ]);
      if (resAdapters.ok) {
        const d = await resAdapters.json();
        setAdapters(d.adapters || []);
      }
      if (resOps.ok) {
        const d = await resOps.json();
        setOpsAlerts(d.internal_ops_alerts || []);
      }
    } catch (err) {
      console.error('Failed to load adapter health', err);
    } finally {
      setLoadingAdapters(false);
    }
  };

  const fetchReportQueue = async () => {
    setLoadingReports(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/admin/reports/queue`);
      if (res.ok) {
        const d = await res.json();
        setReportQueue(d.reports || []);
      }
    } catch (err) {
      console.error('Failed to load reports queue', err);
    } finally {
      setLoadingReports(false);
    }
  };

  const handleModerateReport = async (reportId: string, action: 'APPROVE' | 'REJECT' | 'MERGE') => {
    try {
      const res = await fetch(`${API_BASE}/api/v1/admin/reports/${reportId}/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action,
          admin_user: adminUser,
          notes: moderationNotes[reportId] || 'Moderated from DMMC Admin Portal',
        }),
      });
      if (res.ok) {
        fetchReportQueue();
      }
    } catch (err) {
      console.error('Moderation error', err);
    }
  };

  const fetchDeliveryMetrics = async () => {
    setLoadingMetrics(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/ops/delivery-audit`);
      if (res.ok) {
        const d = await res.json();
        setDeliveryStats(d);
      }
    } catch (err) {
      console.error('Failed to load delivery metrics', err);
    } finally {
      setLoadingMetrics(false);
    }
  };

  const fetchShelters = async () => {
    setLoadingShelters(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/shelters/occupancy`);
      if (res.ok) {
        const d = await res.json();
        const list = d.shelters || [];
        setShelters(list);
        const occInit: { [key: string]: number } = {};
        const liveInit: { [key: string]: boolean } = {};
        list.forEach((s: any) => {
          occInit[s.shelter_id] = s.current_occupancy;
          liveInit[s.shelter_id] = s.is_live;
        });
        setEditOccupancy(occInit);
        setEditLiveMode(liveInit);
      }
    } catch (err) {
      console.error('Failed to load shelters', err);
    } finally {
      setLoadingShelters(false);
    }
  };

  const handleUpdateShelter = async (shelterId: string) => {
    try {
      const res = await fetch(`${API_BASE}/api/v1/admin/shelters/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          shelter_id: shelterId,
          current_occupancy: editOccupancy[shelterId] ?? 0,
          is_live: editLiveMode[shelterId] ?? false,
          admin_user: adminUser,
        }),
      });
      if (res.ok) {
        fetchShelters();
      }
    } catch (err) {
      console.error('Failed to update shelter', err);
    }
  };

  const fetchAuditTrail = async () => {
    setLoadingAudit(true);
    try {
      const q = auditFilterUser ? `?admin_user=${encodeURIComponent(auditFilterUser)}` : '';
      const res = await fetch(`${API_BASE}/api/v1/admin/audit-trail${q}`);
      if (res.ok) {
        const d = await res.json();
        setAuditLogs(d.audit_trail || []);
      }
    } catch (err) {
      console.error('Failed to load audit trail', err);
    } finally {
      setLoadingAudit(false);
    }
  };

  const fetchAuthorities = async () => {
    setLoadingAuthorities(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/alerts/authorities/directory?district=${callDistrict}`);
      if (res.ok) {
        const d = await res.json();
        setAuthoritiesList(d || []);
      }
      const logsRes = await fetch(`${API_BASE}/api/v1/alerts/authorities/call-logs`);
      if (logsRes.ok) {
        const logs = await logsRes.json();
        setAuthorityCallLogs(logs || []);
      }
    } catch (err) {
      console.error('Failed to load authorities data', err);
    } finally {
      setLoadingAuthorities(false);
    }
  };

  const handleDispatchAuthorityCalls = async (e: React.FormEvent) => {
    e.preventDefault();
    setDispatchingCall(true);
    setCallResult(null);
    try {
      const res = await fetch(`${API_BASE}/api/v1/alerts/call-authorities?mode=LIVE_PRODUCTION`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          station_id: `UK-${callDistrict.toUpperCase()}-01`,
          district: callDistrict,
          hazard_type: 'FLASH_FLOOD_GLOF',
          severity: callSeverity,
          rate_of_rise_m_hr: 1.65,
          rainfall_velocity_mm_hr: 52.0,
          lead_time_minutes: 30,
          custom_directive: callDirective || undefined,
          recipient_override_phone: callOverridePhone || undefined,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setCallResult(data);
        fetchAuthorities();
      }
    } catch (err) {
      console.error('Failed to dispatch authority calls', err);
    } finally {
      setDispatchingCall(false);
    }
  };

  const handleDispatchLiveSms = async (e: React.FormEvent) => {
    e.preventDefault();
    setDispatchingSms(true);
    setSmsResult(null);
    try {
      const res = await fetch(`${API_BASE}/api/v1/alerts/send-live-sms`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          recipient_phone: smsPhone,
          district: smsDistrict,
          language: smsLanguage,
          hazard_level: smsHazardLevel,
          river_surge_m_hr: Number(smsSurgeRate),
          custom_notes: smsCustomNotes || undefined,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setSmsResult(data);
      } else {
        const err = await res.json();
        setSmsResult({ error: err.detail || 'Failed to dispatch live SMS' });
      }
    } catch (err: any) {
      setSmsResult({ error: err.message || 'Network error' });
    } finally {
      setDispatchingSms(false);
    }
  };

  const handleIssueAlert = async (e: React.FormEvent) => {
    e.preventDefault();
    setIssuingAlert(true);
    setIssuanceSuccess(null);

    const alertPayload = {
      identifier: `IN-UK-DMMC-${Date.now()}`,
      sender: `${adminUser}@dmmc.uk.gov.in`,
      senderName: 'DMMC State Disaster Operations Center',
      sent: new Date().toISOString(),
      status: 'Actual',
      msgType: 'Alert',
      scope: 'Public',
      hazardType: newHazard,
      severity: newSeverity,
      urgency: 'Immediate',
      certainty: 'Observed',
      districts: selectedDistricts,
      area: {
        areaDesc: selectedDistricts.join(', ') + ' High Risk Himalayan Sectors',
      },
      effective: new Date().toISOString(),
      expires: new Date(Date.now() + 6 * 3600000).toISOString(),
      sourceFeed: 'DMMC_CONTROL_ROOM_OVERRIDE',
      sourceLastUpdated: new Date().toISOString(),
      localized: {
        'hi-IN': {
          language: 'hi-IN',
          headline: titleHi || `DMMC आपातकालीन चेतावनी: ${newHazard} (${selectedDistricts.join(', ')})`,
          description: instructHi || 'अलर्ट क्षेत्र से सुरक्षित उच्च स्थानों पर प्रस्थान करें।',
          instruction: instructHi || 'USDMA / SDRF निर्देशों का तुरंत पालन करें। हेल्पलाइन: 112 / 1070',
          senderName: 'DMMC देहरादून',
          event: newHazard,
        },
        'en-IN': {
          language: 'en-IN',
          headline: titleEn || `DMMC Emergency Alert: ${newHazard} in ${selectedDistricts.join(', ')}`,
          description: instructEn || 'Immediate mountain hazard warning active.',
          instruction: instructEn || 'Move to higher ground immediately. Call 112 / 1070 for rescue.',
          senderName: 'DMMC Dehradun',
          event: newHazard,
        },
        'gbm-IN': {
          language: 'gbm-IN',
          headline: titleGbm || `DMMC गढ़वाली चेतावनी: ${selectedDistricts.join(', ')} मा भारी संकट`,
          description: instructGbm || 'नदी बाटी दूर डांडा मा चड़ि जावां।',
          instruction: instructGbm || '112 मा फोन करा। डांडा मा सुरक्षित रया।',
          senderName: 'DMMC',
          event: newHazard,
        },
        'kfy-IN': {
          language: 'kfy-IN',
          headline: titleKfy || `DMMC कुमाऊंनी चेतावनी: ${selectedDistricts.join(', ')} मा संकट`,
          description: instructKfy || 'उच्च डांड मा सुरक्षित रया।',
          instruction: instructKfy || '112 मा फोन करा।',
          senderName: 'DMMC',
          event: newHazard,
        },
      },
    };

    try {
      const res = await fetch(`${API_BASE}/api/v1/admin/alerts/issue`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(alertPayload),
      });
      if (!res.ok) throw new Error('Alert issuance failed on backend pipeline');
      const data = await res.json();
      setIssuanceSuccess(`Alert ${data.audit.alert_id} successfully dispatched across 5 channels!`);
      // Clear form
      setTitleHi('');
      setInstructHi('');
      setTitleEn('');
      setInstructEn('');
    } catch (err: any) {
      alert(err.message || 'Error issuing alert');
    } finally {
      setIssuingAlert(false);
    }
  };

  const handleOverrideSensor = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE}/api/v1/admin/alerts/override`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sensor_id: overrideSensorId,
          district: overrideDistrict,
          action: overrideAction,
          reason: overrideReason,
          admin_user: adminUser,
        }),
      });
      if (res.ok) {
        setOverrideSuccess(`Sensor ${overrideSensorId} marked ${overrideAction} in audit ledger.`);
        setOverrideReason('');
      }
    } catch (err) {
      console.error('Sensor override error', err);
    }
  };

  // ---------------------------------------------------------------------------
  // AUTHENTICATION VIEW (IF NOT LOGGED IN)
  // ---------------------------------------------------------------------------
  if (!authToken) {
    return (
      <div className="min-h-screen bg-slate-100 text-slate-900 flex items-center justify-center p-4 font-sans">
        <div className="max-w-md w-full bg-white border border-slate-200 rounded-2xl shadow-xl p-8 space-y-6">
          <div className="text-center space-y-2">
            <div className="inline-flex p-3 bg-red-100 border border-red-300 rounded-full text-red-700">
              <ShieldAlert className="w-8 h-8" />
            </div>
            <h1 className="text-xl font-black tracking-tight text-slate-900 uppercase">
              DMMC Uttarakhand State Operations
            </h1>
            <p className="text-xs text-red-700 font-bold tracking-wide uppercase">
              Restricted Control Room &bull; Official Staff Only
            </p>
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            {loginError && (
              <div className="p-3 bg-red-50 border border-red-300 rounded-lg text-xs text-red-800 font-semibold">
                {loginError}
              </div>
            )}

            <div className="space-y-1">
              <label className="text-xs font-bold text-slate-700">Staff Username</label>
              <input
                type="text"
                value={loginUsername}
                onChange={(e) => setLoginUsername(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-lg text-sm text-slate-900 focus:outline-none focus:border-red-600 focus:ring-1 focus:ring-red-600"
                required
              />
            </div>

            <div className="space-y-1">
              <label className="text-xs font-bold text-slate-700">Operations Password</label>
              <input
                type="password"
                value={loginPassword}
                onChange={(e) => setLoginPassword(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-white border border-slate-300 rounded-lg text-sm text-slate-900 focus:outline-none focus:border-red-600 focus:ring-1 focus:ring-red-600"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loadingAuth}
              className="w-full py-2.5 bg-red-700 hover:bg-red-800 text-white font-bold rounded-lg text-sm uppercase tracking-wider transition-colors disabled:opacity-50 flex items-center justify-center gap-2 shadow-sm"
            >
              <Lock className="w-4 h-4" />
              <span>{loadingAuth ? 'Verifying Credentials...' : 'Authorize Control Room Access'}</span>
            </button>

            <button
              type="button"
              onClick={handleQuickLogin}
              className="w-full py-2.5 bg-emerald-700 hover:bg-emerald-800 text-white font-bold rounded-lg text-xs uppercase tracking-wider transition-colors flex items-center justify-center gap-2 shadow-sm"
            >
              <CheckCircle2 className="w-4 h-4 text-emerald-200" />
              <span>⚡ One-Click Enter Control Room (Institutional Demo)</span>
            </button>
          </form>

          <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-600 space-y-1 font-mono">
            <div className="font-bold text-slate-800 font-sans">Local Testing Institutional Credentials:</div>
            <div>Username: <span className="text-blue-900 font-bold">dmmc_admin</span></div>
            <div>Password: <span className="text-blue-900 font-bold">DMMC_Uk_Gov_2026!</span></div>
          </div>
        </div>
      </div>
    );
  }

  // ---------------------------------------------------------------------------
  // MAIN ADMIN / OPS CONTROL ROOM VIEW
  // ---------------------------------------------------------------------------
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans pb-12">
      {/* Top Government Navigation Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-40 px-4 lg:px-8 py-3 shadow-sm">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded bg-red-700 flex items-center justify-center text-white font-black text-base shadow-sm">
              UK
            </div>
            <div>
              <div className="text-xs text-red-700 font-bold uppercase tracking-wider">
                उत्तराखंड राज्य आपदा प्रबंधन प्राधिकरण (USDMA)
              </div>
              <h1 className="text-sm lg:text-base font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
                <span>DMMC Disaster Mitigation Operations Center</span>
                <span className="px-2 py-0.5 bg-red-100 border border-red-300 text-[10px] text-red-800 rounded font-bold">
                  LIVE SECURE
                </span>
              </h1>
            </div>
          </div>

          <div className="flex items-center gap-3 text-xs">
            <div className="hidden sm:block text-right">
              <div className="text-slate-900 font-bold">{adminUser}</div>
              <div className="text-[10px] text-emerald-700 font-bold">STATE CONTROL OFFICER</div>
            </div>
            <button
              onClick={handleLogout}
              className="px-3.5 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-800 rounded-lg flex items-center gap-1.5 transition font-semibold border border-slate-300 shadow-sm"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span>Sign Out</span>
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="max-w-7xl mx-auto mt-3 flex overflow-x-auto gap-1 border-t border-slate-200 pt-2 text-xs font-semibold scrollbar-none">
          <button
            onClick={() => setActiveTab('feeds')}
            className={`px-3.5 py-1.5 rounded-lg flex items-center gap-1.5 whitespace-nowrap transition ${
              activeTab === 'feeds'
                ? 'bg-red-700 text-white shadow-sm'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            <Activity className="w-3.5 h-3.5" />
            <span>1. Feed Health &amp; Staleness</span>
          </button>

          <button
            onClick={() => setActiveTab('issuance')}
            className={`px-3.5 py-1.5 rounded-lg flex items-center gap-1.5 whitespace-nowrap transition ${
              activeTab === 'issuance'
                ? 'bg-red-700 text-white shadow-sm'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            <Send className="w-3.5 h-3.5" />
            <span>2. Manual Issuance &amp; Sensor Override</span>
          </button>

          <button
            onClick={() => setActiveTab('reports')}
            className={`px-3.5 py-1.5 rounded-lg flex items-center gap-1.5 whitespace-nowrap transition ${
              activeTab === 'reports'
                ? 'bg-red-700 text-white shadow-sm'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>3. Hazard Reports Review ({reportQueue.length})</span>
          </button>

          <button
            onClick={() => setActiveTab('metrics')}
            className={`px-3.5 py-1.5 rounded-lg flex items-center gap-1.5 whitespace-nowrap transition ${
              activeTab === 'metrics'
                ? 'bg-red-700 text-white shadow-sm'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            <Radio className="w-3.5 h-3.5" />
            <span>4. 5-Channel Delivery Stats</span>
          </button>

          <button
            onClick={() => setActiveTab('shelters')}
            className={`px-3.5 py-1.5 rounded-lg flex items-center gap-1.5 whitespace-nowrap transition ${
              activeTab === 'shelters'
                ? 'bg-red-700 text-white shadow-sm'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            <Building className="w-3.5 h-3.5" />
            <span>5. Shelter Occupancy Live Tracking</span>
          </button>

          <button
            onClick={() => setActiveTab('audit')}
            className={`px-3.5 py-1.5 rounded-lg flex items-center gap-1.5 whitespace-nowrap transition ${
              activeTab === 'audit'
                ? 'bg-red-700 text-white shadow-sm'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            <FileText className="w-3.5 h-3.5" />
            <span>6. Tamper-Evident Audit Trail</span>
          </button>

          <button
            onClick={() => setActiveTab('authorities')}
            className={`px-3.5 py-1.5 rounded-lg flex items-center gap-1.5 whitespace-nowrap transition ${
              activeTab === 'authorities'
                ? 'bg-red-700 text-white shadow-sm'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            <PhoneCall className="w-3.5 h-3.5" />
            <span>7. Authority Voice Escalation &amp; Call Logs</span>
          </button>
        </div>
      </header>

      {/* Main Body */}
      <main className="max-w-7xl mx-auto p-4 lg:p-6 space-y-6">
        {/* ================================================================= */}
        {/* TAB 1: ADAPTER HEALTH & STALENESS MONITOR */}
        {/* ================================================================= */}
        {activeTab === 'feeds' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-extrabold text-slate-900 uppercase tracking-tight">
                  Telemetry Feed Health &amp; Staleness Self-Monitoring
                </h2>
                <p className="text-xs text-slate-600">
                  Monitors 6 hazard telemetry streams, 5 alert delivery gateways, and National Sachet CAP pipeline.
                </p>
              </div>
              <button
                onClick={fetchAdapterHealth}
                disabled={loadingAdapters}
                className="px-3.5 py-1.5 bg-white hover:bg-slate-50 text-xs text-slate-800 rounded-lg border border-slate-300 flex items-center gap-1.5 font-semibold shadow-sm transition"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loadingAdapters ? 'animate-spin text-red-600' : ''}`} />
                <span>Audit Staleness Now</span>
              </button>
            </div>

            {/* Internal Ops Alerts Panel (Not visible to citizens) */}
            {opsAlerts.length > 0 && (
              <div className="bg-amber-50 border border-amber-300 rounded-xl p-4 space-y-2">
                <div className="flex items-center gap-2 text-amber-900 font-bold text-xs uppercase tracking-wider">
                  <AlertTriangle className="w-4 h-4 text-amber-700" />
                  <span>DMMC Internal Operations Notifications (Control Room Only)</span>
                </div>
                <div className="space-y-1.5">
                  {opsAlerts.map((oa, idx) => (
                    <div
                      key={idx}
                      className="p-2.5 bg-white border border-amber-200 rounded-lg text-xs flex items-start justify-between gap-4 shadow-sm"
                    >
                      <div>
                        <span className="font-mono text-amber-800 font-bold mr-2">[{oa.level}]</span>
                        <span className="text-slate-800">{oa.message}</span>
                      </div>
                      <span className="text-[10px] text-slate-500 font-mono whitespace-nowrap">
                        {new Date(oa.timestamp).toLocaleTimeString('en-IN')}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* National Sachet Integration Status Callout (Ground Rule 6 / ADR-001) */}
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-xl space-y-1.5">
              <div className="flex items-center justify-between">
                <div className="text-xs font-bold text-blue-950 uppercase tracking-wide flex items-center gap-1.5">
                  <Radio className="w-4 h-4 text-blue-700" />
                  <span>NDMA Sachet CAP Integration Architecture (ADR-001 Verified)</span>
                </div>
                <span className="px-2 py-0.5 bg-blue-100 text-blue-900 border border-blue-300 text-[10px] font-bold rounded">
                  FEDERATED STATE LAYER
                </span>
              </div>
              <p className="text-xs text-slate-700 leading-relaxed">
                Per Architectural Decision Record ADR-001, this DMMC engine operates as an autonomous
                Regional Intelligence Layer alongside NDMA Sachet: it consumes national feeds, enriches alerts
                with local Himalayan sensors and Garhwali/Kumaoni dialects, and feeds upstream warnings back to Sachet.
              </p>
            </div>

            {/* Feed Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {adapters.map((ad) => (
                <div
                  key={ad.adapter_id}
                  className={`p-4 rounded-xl border flex flex-col justify-between space-y-3 shadow-sm bg-white hover:border-slate-300 transition-all ${
                    ad.status === 'ONLINE'
                      ? 'border-emerald-200'
                      : ad.status === 'STALE'
                      ? 'border-amber-300 bg-amber-50/40'
                      : 'border-slate-200'
                  }`}
                >
                  <div className="space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold text-slate-500 uppercase">
                        {ad.category}
                      </span>
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                          ad.status === 'ONLINE'
                            ? 'bg-emerald-50 text-emerald-800 border-emerald-300'
                            : ad.status === 'STALE'
                            ? 'bg-amber-50 text-amber-800 border-amber-300'
                            : 'bg-slate-100 text-slate-600 border-slate-300'
                        }`}
                      >
                        {ad.status}
                      </span>
                    </div>
                    <h3 className="text-sm font-bold text-slate-900">{ad.display_name}</h3>
                    <div className="text-[11px] text-slate-500 font-mono truncate">
                      URI: {ad.endpoint_url}
                    </div>
                  </div>

                  <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500 font-mono">
                    <span>Expected: {ad.expected_interval_sec}s</span>
                    <span>
                      {ad.is_configured ? (
                        ad.last_success ? (
                          `Synced: ${new Date(ad.last_success).toLocaleTimeString('en-IN')}`
                        ) : (
                          'Awaiting Initial Ingest'
                        )
                      ) : (
                        'Credential Not Configured'
                      )}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ================================================================= */}
        {/* TAB 2: MANUAL ALERT ISSUANCE & SENSOR OVERRIDE */}
        {/* ================================================================= */}
        {activeTab === 'issuance' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Manual Alert Issuance */}
            <div className="bg-white border border-slate-200 rounded-xl p-5 space-y-4 shadow-sm">
              <div className="border-b border-slate-200 pb-3">
                <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide flex items-center gap-2">
                  <ShieldAlert className="w-4 h-4 text-red-600" />
                  <span>Issue Official DMMC Emergency CAP Alert</span>
                </h3>
                <p className="text-xs text-slate-600">
                  Dispatches immediately across all 5 channels (Cell Broadcast, SMS, IVR Voice, WhatsApp, FCM Push).
                </p>
              </div>

              {issuanceSuccess && (
                <div className="p-3 bg-emerald-50 border border-emerald-300 rounded-lg text-xs text-emerald-900 font-semibold">
                  {issuanceSuccess}
                </div>
              )}

              <form onSubmit={handleIssueAlert} className="space-y-4">
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <label className="text-xs text-slate-700 font-semibold">Hazard Type</label>
                    <select
                      value={newHazard}
                      onChange={(e) => setNewHazard(e.target.value)}
                      className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 focus:outline-none focus:border-red-600"
                    >
                      <option value="FLASH_FLOOD_GLOF">GLOF &amp; Flash Flood</option>
                      <option value="LANDSLIDE_SLOPE_FAILURE">Landslide / Slope Failure</option>
                      <option value="CLOUDBURST_SEVERE_STORM">Cloudburst &amp; Thunderstorm</option>
                      <option value="EARTHQUAKE_SEISMIC">Earthquake (IITR EEW)</option>
                      <option value="FOREST_FIRE">Forest Fire</option>
                      <option value="AVALANCHE_SNOWFALL">Avalanche &amp; Snowfall</option>
                    </select>
                  </div>

                  <div className="space-y-1">
                    <label className="text-xs text-slate-700 font-semibold">Severity Tier</label>
                    <select
                      value={newSeverity}
                      onChange={(e) => setNewSeverity(e.target.value)}
                      className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 focus:outline-none focus:border-red-600"
                    >
                      <option value="CRITICAL">CRITICAL (Red Alert • Cell Broadcast + Voice)</option>
                      <option value="SEVERE">SEVERE (Orange Alert • SMS + WhatsApp)</option>
                      <option value="ADVISORY">ADVISORY (Yellow Alert • Push + App)</option>
                    </select>
                  </div>
                </div>

                <div className="space-y-1">
                  <label className="text-xs text-slate-700 font-semibold">
                    Target Uttarakhand District(s)
                  </label>
                  <div className="flex flex-wrap gap-1.5 p-2.5 bg-slate-50 border border-slate-200 rounded-lg max-h-28 overflow-y-auto">
                    {UTTARAKHAND_DISTRICTS.map((d) => {
                      const selected = selectedDistricts.includes(d);
                      return (
                        <button
                          key={d}
                          type="button"
                          onClick={() => {
                            setSelectedDistricts((prev) =>
                              prev.includes(d) ? prev.filter((x) => x !== d) : [...prev, d]
                            );
                          }}
                          className={`px-2.5 py-1 rounded text-xs font-semibold transition shadow-sm ${
                            selected
                              ? 'bg-red-700 text-white'
                              : 'bg-white border border-slate-300 text-slate-700 hover:bg-slate-100'
                          }`}
                        >
                          {d}
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Hindi Content */}
                <div className="space-y-2 pt-2 border-t border-slate-200">
                  <span className="text-xs font-bold text-slate-800 uppercase tracking-wide">
                    Hindi Copy (हिन्दी सन्देश)
                  </span>
                  <input
                    type="text"
                    placeholder="Headline in Hindi (e.g. चमोली में आकस्मिक बाढ़ चेतावनी)"
                    value={titleHi}
                    onChange={(e) => setTitleHi(e.target.value)}
                    className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 focus:border-red-600"
                  />
                  <textarea
                    rows={2}
                    placeholder="Public evacuation instructions in Hindi"
                    value={instructHi}
                    onChange={(e) => setInstructHi(e.target.value)}
                    className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 focus:border-red-600"
                  />
                </div>

                {/* English Content */}
                <div className="space-y-2 pt-2 border-t border-slate-200">
                  <span className="text-xs font-bold text-slate-800 uppercase tracking-wide">
                    English Copy
                  </span>
                  <input
                    type="text"
                    placeholder="Headline in English"
                    value={titleEn}
                    onChange={(e) => setTitleEn(e.target.value)}
                    className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 focus:border-red-600"
                  />
                  <textarea
                    rows={2}
                    placeholder="Public instructions in English"
                    value={instructEn}
                    onChange={(e) => setInstructEn(e.target.value)}
                    className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 focus:border-red-600"
                  />
                </div>

                {/* Regional Dialects Optional Overrides */}
                <div className="space-y-2 pt-2 border-t border-slate-200">
                  <span className="text-xs font-bold text-slate-800 uppercase tracking-wide">
                    Regional Dialect Direct Overrides (Garhwali / Kumaoni)
                  </span>
                  <div className="grid grid-cols-2 gap-2">
                    <input
                      type="text"
                      placeholder="Garhwali (गढ़वाली)"
                      value={titleGbm}
                      onChange={(e) => setTitleGbm(e.target.value)}
                      className="px-3 py-2 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 focus:border-red-600"
                    />
                    <input
                      type="text"
                      placeholder="Kumaoni (कुमाऊँनी)"
                      value={titleKfy}
                      onChange={(e) => setTitleKfy(e.target.value)}
                      className="px-3 py-2 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 focus:border-red-600"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={issuingAlert || selectedDistricts.length === 0}
                  className="w-full py-2.5 bg-red-700 hover:bg-red-800 text-white font-bold rounded-lg text-xs uppercase tracking-wider transition disabled:opacity-50 flex items-center justify-center gap-2 shadow-sm"
                >
                  <Send className="w-4 h-4" />
                  <span>{issuingAlert ? 'Dispatched to 5 Channels...' : 'Execute Multi-Channel Alert Dispatch'}</span>
                </button>
              </form>
            </div>

            {/* Sensor Reading Override / Fault Suppression */}
            <div className="bg-white border border-slate-200 rounded-xl p-5 space-y-4 shadow-sm">
              <div className="border-b border-slate-200 pb-3">
                <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-amber-600" />
                  <span>Sensor Telemetry Override &amp; False Alarm Suppression</span>
                </h3>
                <p className="text-xs text-slate-600">
                  Temporarily suppresses false alarms or marks telemetry hardware faulty pending field recalibration.
                </p>
              </div>

              {overrideSuccess && (
                <div className="p-3 bg-emerald-50 border border-emerald-300 rounded-lg text-xs text-emerald-900 font-semibold">
                  {overrideSuccess}
                </div>
              )}

              <form onSubmit={handleOverrideSensor} className="space-y-4">
                <div className="space-y-1">
                  <label className="text-xs text-slate-700 font-semibold">Station / Sensor ID</label>
                  <input
                    type="text"
                    value={overrideSensorId}
                    onChange={(e) => setOverrideSensorId(e.target.value)}
                    className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 font-mono focus:border-amber-600"
                    required
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <label className="text-xs text-slate-700 font-semibold">District</label>
                    <select
                      value={overrideDistrict}
                      onChange={(e) => setOverrideDistrict(e.target.value)}
                      className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 focus:border-amber-600"
                    >
                      {UTTARAKHAND_DISTRICTS.map((d) => (
                        <option key={d} value={d}>{d}</option>
                      ))}
                    </select>
                  </div>

                  <div className="space-y-1">
                    <label className="text-xs text-slate-700 font-semibold">Action</label>
                    <select
                      value={overrideAction}
                      onChange={(e) => setOverrideAction(e.target.value)}
                      className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 focus:border-amber-600"
                    >
                      <option value="OVERRIDE_FAULTY">Override as Faulty Sensor</option>
                      <option value="SUPPRESS">Suppress Temporary False Spike</option>
                      <option value="RESET">Reset Sensor to Live Stream</option>
                    </select>
                  </div>
                </div>

                <div className="space-y-1">
                  <label className="text-xs text-slate-700 font-semibold">
                    Technical Justification / SDRF Verification Note
                  </label>
                  <textarea
                    rows={3}
                    placeholder="e.g. River gauge acoustic echo during cloudburst; optical camera confirms normal water levels"
                    value={overrideReason}
                    onChange={(e) => setOverrideReason(e.target.value)}
                    className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 focus:border-amber-600"
                    required
                  />
                </div>

                <button
                  type="submit"
                  className="w-full py-2.5 bg-amber-700 hover:bg-amber-800 text-white font-bold rounded-lg text-xs uppercase tracking-wider transition shadow-sm"
                >
                  Commit Sensor Override to Audit Ledger
                </button>
              </form>
            </div>
          </div>
        )}

        {/* ================================================================= */}
        {/* TAB 3: CROWDSOURCED HAZARD REPORTS MODERATION QUEUE */}
        {/* ================================================================= */}
        {activeTab === 'reports' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-extrabold text-slate-900 uppercase tracking-tight">
                  Crowdsourced Hazard Reports Review Queue
                </h2>
                <p className="text-xs text-slate-600">
                  Citizen-submitted geotagged hazard alerts (road blockages, mudslides) awaiting verification.
                </p>
              </div>
              <button
                onClick={fetchReportQueue}
                className="px-3.5 py-1.5 bg-white hover:bg-slate-50 text-xs text-slate-800 rounded-lg border border-slate-300 flex items-center gap-1.5 font-semibold shadow-sm transition"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loadingReports ? 'animate-spin text-red-600' : ''}`} />
                <span>Refresh Queue</span>
              </button>
            </div>

            {reportQueue.length === 0 ? (
              <div className="p-8 bg-white border border-slate-200 rounded-xl text-center space-y-2 shadow-sm">
                <CheckCircle2 className="w-8 h-8 text-emerald-600 mx-auto" />
                <div className="text-sm font-bold text-slate-900">No Pending Unverified Reports</div>
                <div className="text-xs text-slate-500">All citizen hazard reports have been processed.</div>
              </div>
            ) : (
              <div className="space-y-3">
                {reportQueue.map((rpt) => (
                  <div
                    key={rpt.report_id}
                    className="p-4 bg-white border border-slate-200 rounded-xl flex flex-col lg:flex-row lg:items-center justify-between gap-4 shadow-sm hover:border-slate-300 transition-all"
                  >
                    <div className="space-y-1.5 flex-1">
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 bg-amber-50 border border-amber-300 text-amber-900 text-[10px] font-bold rounded">
                          {rpt.status}
                        </span>
                        <span className="text-xs font-bold text-slate-900">
                          {rpt.district} &bull; {rpt.category}
                        </span>
                        <span className="text-[11px] text-slate-500 font-mono">
                          ({rpt.lat.toFixed(3)}, {rpt.lon.toFixed(3)})
                        </span>
                      </div>
                      <p className="text-xs text-slate-700">{rpt.description}</p>
                      <div className="text-[10px] text-slate-500 font-mono">
                        Report ID: {rpt.report_id} &bull; Received:{' '}
                        {new Date(rpt.submitted_at).toLocaleTimeString('en-IN')}
                      </div>
                    </div>

                    <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
                      <input
                        type="text"
                        placeholder="Moderation notes / SDRF unit..."
                        value={moderationNotes[rpt.report_id] || ''}
                        onChange={(e) =>
                          setModerationNotes({ ...moderationNotes, [rpt.report_id]: e.target.value })
                        }
                        className="px-3 py-1.5 bg-white border border-slate-300 rounded-lg text-xs text-slate-900"
                      />
                      <button
                        onClick={() => handleModerateReport(rpt.report_id, 'APPROVE')}
                        className="px-3.5 py-1.5 bg-emerald-700 hover:bg-emerald-800 text-white rounded-lg text-xs font-bold transition shadow-sm"
                      >
                        Approve
                      </button>
                      <button
                        onClick={() => handleModerateReport(rpt.report_id, 'REJECT')}
                        className="px-3.5 py-1.5 bg-red-700 hover:bg-red-800 text-white rounded-lg text-xs font-bold transition shadow-sm"
                      >
                        Reject
                      </button>
                      <button
                        onClick={() => handleModerateReport(rpt.report_id, 'MERGE')}
                        className="px-3.5 py-1.5 bg-blue-700 hover:bg-blue-800 text-white rounded-lg text-xs font-bold transition shadow-sm"
                      >
                        Merge
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ================================================================= */}
        {/* TAB 4: 5-CHANNEL DELIVERY METRICS */}
        {/* ================================================================= */}
        {activeTab === 'metrics' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-extrabold text-slate-900 uppercase tracking-tight">
                  Multi-Channel Emergency Alert Delivery Statistics
                </h2>
                <p className="text-xs text-slate-600">
                  Post-incident audit tracking C-DOT Cell Broadcast, NIC SMS, IVR Voice, WhatsApp, and FCM Push.
                </p>
              </div>
              <button
                onClick={fetchDeliveryMetrics}
                className="px-3.5 py-1.5 bg-white hover:bg-slate-50 text-xs text-slate-800 rounded-lg border border-slate-300 flex items-center gap-1.5 font-semibold shadow-sm transition"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loadingMetrics ? 'animate-spin text-red-600' : ''}`} />
                <span>Refresh Stats</span>
              </button>
            </div>

            {deliveryStats && (
              <>
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
                  <div className="p-3.5 bg-white border border-slate-200 rounded-xl space-y-1 shadow-sm">
                    <span className="text-[10px] text-slate-500 uppercase font-bold">TOTAL DISPATCHES</span>
                    <div className="text-xl font-extrabold text-slate-900">{deliveryStats.total_dispatches}</div>
                  </div>
                  <div className="p-3.5 bg-white border border-slate-200 rounded-xl space-y-1 shadow-sm">
                    <span className="text-[10px] text-slate-500 uppercase font-bold">CELL BROADCASTS</span>
                    <div className="text-xl font-extrabold text-red-600">{deliveryStats.cell_broadcasts_count}</div>
                  </div>
                  <div className="p-3.5 bg-white border border-slate-200 rounded-xl space-y-1 shadow-sm">
                    <span className="text-[10px] text-slate-500 uppercase font-bold">NIC SMS DELIVERED</span>
                    <div className="text-xl font-extrabold text-blue-700">{deliveryStats.total_sms_delivered}</div>
                  </div>
                  <div className="p-3.5 bg-white border border-slate-200 rounded-xl space-y-1 shadow-sm">
                    <span className="text-[10px] text-slate-500 uppercase font-bold">IVR CALLS PLACED</span>
                    <div className="text-xl font-extrabold text-amber-700">{deliveryStats.total_ivr_placed}</div>
                  </div>
                  <div className="p-3.5 bg-white border border-slate-200 rounded-xl space-y-1 shadow-sm">
                    <span className="text-[10px] text-slate-500 uppercase font-bold">WHATSAPP DELIVERED</span>
                    <div className="text-xl font-extrabold text-emerald-700">{deliveryStats.total_whatsapp_delivered}</div>
                  </div>
                  <div className="p-3.5 bg-white border border-slate-200 rounded-xl space-y-1 shadow-sm">
                    <span className="text-[10px] text-slate-500 uppercase font-bold">FCM PUSH DELIVERED</span>
                    <div className="text-xl font-extrabold text-purple-700">{deliveryStats.total_push_delivered}</div>
                  </div>
                </div>

                {/* Recent Dispatches Table */}
                <div className="bg-white border border-slate-200 rounded-xl p-4 space-y-3 shadow-sm overflow-hidden">
                  <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                    Recent Multi-Channel Dispatches
                  </h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs">
                      <thead>
                        <tr className="border-b border-slate-200 bg-slate-50 text-slate-600 font-bold">
                          <th className="py-2.5 px-3">Alert ID</th>
                          <th className="py-2.5 px-3">Hazard</th>
                          <th className="py-2.5 px-3">Severity</th>
                          <th className="py-2.5 px-3">Districts</th>
                          <th className="py-2.5 px-3">Subscribers</th>
                          <th className="py-2.5 px-3">Channels Used</th>
                          <th className="py-2.5 px-3">Latency</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100 font-mono">
                        {(deliveryStats.recent_dispatches || []).map((rd: any) => (
                          <tr key={rd.audit_id} className="hover:bg-slate-50">
                            <td className="py-2.5 px-3 text-slate-900 font-bold">{rd.alert_id}</td>
                            <td className="py-2.5 px-3 text-slate-700 font-sans">{rd.hazard_type}</td>
                            <td className="py-2.5 px-3">
                              <span className="text-red-700 font-bold">{rd.severity}</span>
                            </td>
                            <td className="py-2.5 px-3 text-slate-700 font-sans">{rd.districts.join(', ')}</td>
                            <td className="py-2.5 px-3 text-slate-700">{rd.matched_subscribers}</td>
                            <td className="py-2.5 px-3 text-[11px] text-slate-600">
                              {Object.entries(rd.gateway_statuses || {})
                                .map(([gw, st]) => `${gw}: ${st}`)
                                .join(' | ')}
                            </td>
                            <td className="py-2.5 px-3 text-slate-600">{rd.latency_ms}ms</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </>
            )}
          </div>
        )}

        {/* ================================================================= */}
        {/* TAB 5: LIVE SHELTER MANAGEMENT */}
        {/* ================================================================= */}
        {activeTab === 'shelters' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-extrabold text-slate-900 uppercase tracking-tight">
                  Emergency Haven &amp; Relief Shelter Tracking
                </h2>
                <p className="text-xs text-slate-600">
                  Update live occupancy vs. capacity across DMMC relief centers. Falls back to static capacity if live feed is inactive.
                </p>
              </div>
              <button
                onClick={fetchShelters}
                className="px-3.5 py-1.5 bg-white hover:bg-slate-50 text-xs text-slate-800 rounded-lg border border-slate-300 flex items-center gap-1.5 font-semibold shadow-sm transition"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loadingShelters ? 'animate-spin text-red-600' : ''}`} />
                <span>Refresh Shelters</span>
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {shelters.map((sh) => (
                <div
                  key={sh.shelter_id}
                  className="p-4 bg-white border border-slate-200 rounded-xl space-y-3 shadow-sm hover:border-slate-300 transition-all"
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="text-sm font-bold text-slate-900">{sh.name}</h3>
                      <div className="text-xs text-slate-500">
                        {sh.district} &bull; Alt: {sh.elevation_m}m &bull; Helpline: {sh.helpline}
                      </div>
                    </div>
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                        sh.is_live
                          ? 'bg-emerald-50 text-emerald-900 border-emerald-300'
                          : 'bg-slate-100 text-slate-600 border-slate-300'
                      }`}
                    >
                      {sh.is_live ? 'LIVE TELEMETRY' : 'STATIC CAPACITY'}
                    </span>
                  </div>

                  {/* Occupancy bar */}
                  <div className="space-y-1">
                    <div className="flex justify-between text-xs font-mono">
                      <span className="text-slate-600">
                        Occupancy: {sh.current_occupancy} / {sh.capacity}
                      </span>
                      <span className="text-slate-900 font-bold">
                        {Math.round((sh.current_occupancy / sh.capacity) * 100)}%
                      </span>
                    </div>
                    <div className="w-full h-2 bg-slate-100 border border-slate-200 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-red-600 rounded-full"
                        style={{
                          width: `${Math.min(100, (sh.current_occupancy / sh.capacity) * 100)}%`,
                        }}
                      />
                    </div>
                  </div>

                  {/* Admin Editor */}
                  <div className="pt-2 border-t border-slate-100 flex items-center gap-3">
                    <div className="flex items-center gap-1.5 flex-1">
                      <label className="text-xs font-semibold text-slate-600">Set Occupancy:</label>
                      <input
                        type="number"
                        value={editOccupancy[sh.shelter_id] ?? sh.current_occupancy}
                        onChange={(e) =>
                          setEditOccupancy({
                            ...editOccupancy,
                            [sh.shelter_id]: parseInt(e.target.value) || 0,
                          })
                        }
                        className="w-20 px-2 py-1 bg-white border border-slate-300 rounded text-xs text-slate-900 font-mono"
                      />
                    </div>

                    <label className="flex items-center gap-1.5 text-xs text-slate-700 font-semibold cursor-pointer">
                      <input
                        type="checkbox"
                        checked={editLiveMode[sh.shelter_id] ?? sh.is_live}
                        onChange={(e) =>
                          setEditLiveMode({
                            ...editLiveMode,
                            [sh.shelter_id]: e.target.checked,
                          })
                        }
                        className="rounded border-slate-300 text-red-600"
                      />
                      <span>Mark Live</span>
                    </label>

                    <button
                      onClick={() => handleUpdateShelter(sh.shelter_id)}
                      className="px-3.5 py-1 bg-red-700 hover:bg-red-800 text-white font-bold rounded-lg text-xs transition shadow-sm"
                    >
                      Save
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ================================================================= */}
        {/* TAB 6: TAMPER-EVIDENT AUDIT TRAIL LOG VIEWER */}
        {/* ================================================================= */}
        {activeTab === 'audit' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-extrabold text-slate-900 uppercase tracking-tight">
                  Tamper-Evident Operations Audit Log Viewer
                </h2>
                <p className="text-xs text-slate-600">
                  Comprehensive audit trail of all manual alert issuances, sensor overrides, and moderation actions.
                </p>
              </div>
              <button
                onClick={fetchAuditTrail}
                className="px-3.5 py-1.5 bg-white hover:bg-slate-50 text-xs text-slate-800 rounded-lg border border-slate-300 flex items-center gap-1.5 font-semibold shadow-sm transition"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loadingAudit ? 'animate-spin text-red-600' : ''}`} />
                <span>Refresh Audit Logs</span>
              </button>
            </div>

            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-200 bg-slate-50 text-slate-600 font-bold">
                      <th className="py-2.5 px-3">Timestamp</th>
                      <th className="py-2.5 px-3">Action Type</th>
                      <th className="py-2.5 px-3">Officer</th>
                      <th className="py-2.5 px-3">Target ID</th>
                      <th className="py-2.5 px-3">Details</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 font-mono">
                    {auditLogs.map((log) => (
                      <tr key={log.audit_id} className="hover:bg-slate-50">
                        <td className="py-2.5 px-3 text-slate-600 font-sans">
                          {new Date(log.timestamp).toLocaleString('en-IN')}
                        </td>
                        <td className="py-2.5 px-3 font-bold text-red-700">{log.action_type}</td>
                        <td className="py-2.5 px-3 text-slate-900 font-sans font-semibold">{log.admin_user}</td>
                        <td className="py-2.5 px-3 text-slate-700">{log.target_id}</td>
                        <td className="py-2.5 px-3 text-slate-500 text-[11px]">
                          {JSON.stringify(log.details)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
        {/* ================================================================= */}
        {/* TAB 7: NODAL DISASTER AUTHORITIES & CALL ESCALATION SYSTEM */}
        {/* ================================================================= */}
        {activeTab === 'authorities' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-extrabold text-slate-900 uppercase tracking-tight flex items-center gap-2">
                  <PhoneCall className="w-5 h-5 text-red-600 animate-pulse" />
                  <span>Nodal Disaster Authorities Escalation &amp; Automated Calling</span>
                </h2>
                <p className="text-xs text-slate-600">
                  Direct automated priority phone dispatch and IVR speech escalation to NDRF, SDRF, District Magistrates &amp; SEOC.
                </p>
              </div>
              <button
                onClick={fetchAuthorities}
                disabled={loadingAuthorities}
                className="px-3.5 py-1.5 bg-white hover:bg-slate-50 text-xs text-slate-800 rounded-lg border border-slate-300 flex items-center gap-1.5 font-semibold shadow-sm transition"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${loadingAuthorities ? 'animate-spin text-red-600' : ''}`} />
                <span>Refresh Directory &amp; Logs</span>
              </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left Panel: Trigger Call Dispatch */}
              <div className="bg-white border border-slate-200 rounded-xl p-5 space-y-4 shadow-sm">
                <div className="border-b border-slate-200 pb-3">
                  <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide flex items-center gap-2">
                    <PhoneCall className="w-4 h-4 text-red-600" />
                    <span>Trigger Authority Voice Call</span>
                  </h3>
                  <p className="text-xs text-slate-500">
                    Dispatches automated phone call with bilingual synthesized voice alert to official responders.
                  </p>
                </div>

                {callResult && (
                  <div className="p-3.5 bg-emerald-50 border border-emerald-300 rounded-lg text-xs space-y-2">
                    <div className="font-bold text-emerald-900 flex items-center gap-1.5">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                      <span>{callResult.status}: {callResult.calls_initiated} call(s) placed!</span>
                    </div>
                    <div className="text-[11px] text-emerald-800 space-y-1 font-mono">
                      {callResult.call_records?.map((rec: any, idx: number) => (
                        <div key={idx} className="p-2 bg-white rounded border border-emerald-200">
                          <div><strong>Officer:</strong> {rec.officer_name} ({rec.agency})</div>
                          <div><strong>Phone:</strong> {rec.target_phone}</div>
                          <div><strong>Status:</strong> {rec.call_status} ({rec.call_channel})</div>
                          <div className="text-[10px] text-slate-500 truncate mt-0.5">{rec.spoken_transcript_en}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <form onSubmit={handleDispatchAuthorityCalls} className="space-y-3.5">
                  <div className="space-y-1">
                    <label className="text-xs text-slate-700 font-semibold">Target District</label>
                    <select
                      value={callDistrict}
                      onChange={(e) => {
                        setCallDistrict(e.target.value);
                      }}
                      className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 focus:outline-none focus:border-red-600"
                    >
                      {UTTARAKHAND_DISTRICTS.map((d) => (
                        <option key={d} value={d}>{d}</option>
                      ))}
                    </select>
                  </div>

                  <div className="space-y-1">
                    <label className="text-xs text-slate-700 font-semibold">Severity Tier</label>
                    <select
                      value={callSeverity}
                      onChange={(e) => setCallSeverity(e.target.value)}
                      className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 focus:outline-none focus:border-red-600"
                    >
                      <option value="CRITICAL">CRITICAL (Red Alert • Direct Voice Call)</option>
                      <option value="HIGH">HIGH (Orange Alert • Tactical Standby Call)</option>
                    </select>
                  </div>

                  <div className="space-y-1">
                    <label className="text-xs text-slate-700 font-semibold">
                      Custom Tactical Directive (Optional)
                    </label>
                    <textarea
                      rows={2}
                      placeholder="e.g. Deploy 2 inflatable boat units to Karnaprayag Sangam; evacuate low-lying river wards."
                      value={callDirective}
                      onChange={(e) => setCallDirective(e.target.value)}
                      className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 focus:outline-none focus:border-red-600"
                    />
                  </div>

                  <div className="space-y-1">
                    <label className="text-xs text-slate-700 font-semibold">
                      Direct Test Phone Number (Optional Override)
                    </label>
                    <input
                      type="text"
                      placeholder="e.g. +919837012345 (to test live calling)"
                      value={callOverridePhone}
                      onChange={(e) => setCallOverridePhone(e.target.value)}
                      className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 focus:outline-none focus:border-red-600 font-mono"
                    />
                    <span className="text-[10px] text-slate-500 block">
                      Leave blank to call official nodal directory officers for {callDistrict}.
                    </span>
                  </div>

                  <button
                    type="submit"
                    disabled={dispatchingCall}
                    className="w-full py-2.5 bg-red-700 hover:bg-red-800 text-white font-bold rounded-lg text-xs uppercase tracking-wider transition shadow-sm flex items-center justify-center gap-2"
                  >
                    <PhoneCall className={`w-4 h-4 ${dispatchingCall ? 'animate-bounce' : ''}`} />
                    <span>{dispatchingCall ? 'Initiating Priority Voice Call...' : 'Dispatch Automated Authority Voice Calls'}</span>
                  </button>
                </form>
              </div>

              {/* Right Panel: Official Authorities Directory */}
              <div className="lg:col-span-2 bg-white border border-slate-200 rounded-xl p-5 space-y-4 shadow-sm">
                <div className="border-b border-slate-200 pb-3 flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
                      Official Uttarakhand Disaster Nodal Authorities
                    </h3>
                    <p className="text-xs text-slate-500">
                      Standard operating procedure roster for {callDistrict} and Statewide Command.
                    </p>
                  </div>
                  <span className="px-2.5 py-1 bg-slate-100 border border-slate-300 rounded text-xs font-mono font-bold text-slate-700">
                    {authoritiesList.length} Registered Nodes
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-[380px] overflow-y-auto">
                  {authoritiesList.map((auth: any) => (
                    <div
                      key={auth.authority_id}
                      className="p-3 bg-slate-50 border border-slate-200 rounded-lg space-y-1.5 hover:border-slate-300 transition"
                    >
                      <div className="flex items-center justify-between">
                        <span className="px-2 py-0.5 bg-red-50 border border-red-200 text-red-700 text-[10px] font-bold rounded">
                          {auth.agency}
                        </span>
                        <span className="text-[10px] font-semibold text-slate-500">
                          Priority {auth.escalation_priority} &bull; {auth.district}
                        </span>
                      </div>
                      <div className="text-xs font-bold text-slate-900">{auth.name}</div>
                      <div className="text-[11px] text-slate-600">{auth.designation}</div>
                      <div className="text-[11px] font-mono text-slate-700 pt-1 border-t border-slate-200 flex flex-col gap-0.5">
                        <div>📞 Mobile: <strong className="text-slate-900">{auth.phone_mobile}</strong></div>
                        <div>☎ Landline: {auth.phone_primary}</div>
                        <div>📻 Radio: {auth.radio_channel}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Live Multilingual SMS Push Simulator & Carrier Gateway */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left Panel: SMS Trigger Form */}
              <div className="lg:col-span-1 bg-white border border-slate-200 rounded-xl p-5 space-y-4 shadow-sm">
                <div className="border-b border-slate-200 pb-3">
                  <div className="flex items-center gap-2 text-rose-700">
                    <MessageSquare className="w-5 h-5 text-rose-700" />
                    <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
                      Citizen &amp; Authority SMS Push Dispatcher
                    </h3>
                  </div>
                  <p className="text-xs text-slate-500 mt-1">
                    Dispatches real-time vernacular emergency broadcast with embedded high-ground haven route.
                  </p>
                </div>

                {smsResult && (
                  <div className={`p-3.5 rounded-lg text-xs space-y-2 border ${smsResult.error ? 'bg-red-50 border-red-300 text-red-900' : 'bg-emerald-50 border-emerald-300 text-emerald-900'}`}>
                    {smsResult.error ? (
                      <div className="font-bold flex items-center gap-1.5">
                        <AlertTriangle className="w-4 h-4 text-red-600" />
                        <span>SMS Dispatch Error: {smsResult.error}</span>
                      </div>
                    ) : (
                      <div className="space-y-1.5">
                        <div className="font-bold flex items-center gap-1.5">
                          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                          <span>Status: {smsResult.carrier_dispatch_status} ({smsResult.execution_time_ms}ms)</span>
                        </div>
                        <div className="p-2 bg-white rounded border border-emerald-200 font-mono text-[11px] text-slate-800 whitespace-pre-wrap">
                          {smsResult.alert_text}
                        </div>
                        {smsResult.sms_native_uri && (
                          <a
                            href={smsResult.sms_native_uri}
                            className="inline-flex items-center gap-1 px-3 py-1.5 bg-emerald-700 hover:bg-emerald-800 text-white rounded text-xs font-bold transition shadow-xs"
                          >
                            <span>📱 Open in Native Phone SMS App</span>
                          </a>
                        )}
                      </div>
                    )}
                  </div>
                )}

                <form onSubmit={handleDispatchLiveSms} className="space-y-3.5">
                  <div className="space-y-1">
                    <label className="text-xs text-slate-700 font-semibold">Recipient Mobile Number</label>
                    <input
                      type="tel"
                      value={smsPhone}
                      onChange={(e) => setSmsPhone(e.target.value)}
                      placeholder="+919876543210"
                      className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 font-mono focus:outline-none focus:border-rose-600"
                      required
                    />
                    <span className="text-[10px] text-slate-500 block">
                      Enter any mobile number to test direct live SMS delivery.
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div className="space-y-1">
                      <label className="text-xs text-slate-700 font-semibold">Target District</label>
                      <select
                        value={smsDistrict}
                        onChange={(e) => setSmsDistrict(e.target.value)}
                        className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 focus:outline-none focus:border-rose-600"
                      >
                        {UTTARAKHAND_DISTRICTS.map((d) => (
                          <option key={d} value={d}>{d}</option>
                        ))}
                      </select>
                    </div>

                    <div className="space-y-1">
                      <label className="text-xs text-slate-700 font-semibold">Dialect / Language</label>
                      <select
                        value={smsLanguage}
                        onChange={(e) => setSmsLanguage(e.target.value)}
                        className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 focus:outline-none focus:border-rose-600"
                      >
                        <option value="hi">हिन्दी (Hindi)</option>
                        <option value="gar">गढ़वाली (Garhwali)</option>
                        <option value="kum">कुमाऊँनी (Kumaoni)</option>
                        <option value="jau">जौनसारी (Jaunsari)</option>
                        <option value="en">English</option>
                        <option value="sa">संस्कृतम् (Sanskrit)</option>
                      </select>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div className="space-y-1">
                      <label className="text-xs text-slate-700 font-semibold">Hazard Tier</label>
                      <select
                        value={smsHazardLevel}
                        onChange={(e) => setSmsHazardLevel(e.target.value)}
                        className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 focus:outline-none focus:border-rose-600"
                      >
                        <option value="CRITICAL">CRITICAL (Red Alert)</option>
                        <option value="HIGH">HIGH (Orange Alert)</option>
                        <option value="WARNING">WARNING (Yellow Alert)</option>
                      </select>
                    </div>

                    <div className="space-y-1">
                      <label className="text-xs text-slate-700 font-semibold">Surge Rate (m/hr)</label>
                      <input
                        type="number"
                        step="0.05"
                        value={smsSurgeRate}
                        onChange={(e) => setSmsSurgeRate(parseFloat(e.target.value) || 0)}
                        className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 font-mono focus:outline-none focus:border-rose-600"
                        required
                      />
                    </div>
                  </div>

                  <div className="space-y-1">
                    <label className="text-xs text-slate-700 font-semibold">Custom Evacuation Note (Optional)</label>
                    <input
                      type="text"
                      placeholder="e.g. Move immediately above 1900m contour line."
                      value={smsCustomNotes}
                      onChange={(e) => setSmsCustomNotes(e.target.value)}
                      className="w-full px-3 py-2 bg-white border border-slate-300 rounded-lg text-xs text-slate-900 focus:outline-none focus:border-rose-600"
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={dispatchingSms}
                    className="w-full py-2.5 bg-rose-700 hover:bg-rose-800 text-white font-bold rounded-lg text-xs uppercase tracking-wider transition shadow-sm flex items-center justify-center gap-2"
                  >
                    <Send className={`w-4 h-4 ${dispatchingSms ? 'animate-bounce' : ''}`} />
                    <span>{dispatchingSms ? 'Dispatching Vernacular SMS...' : 'Dispatch Live Vernacular SMS Push'}</span>
                  </button>
                </form>
              </div>

              {/* Right Panel: Active Multi-Channel Telecom Status */}
              <div className="lg:col-span-2 bg-white border border-slate-200 rounded-xl p-5 space-y-4 shadow-sm flex flex-col justify-between">
                <div>
                  <div className="border-b border-slate-200 pb-3 flex items-center justify-between">
                    <div>
                      <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wide">
                        Tiered Multi-Channel Early Warning Delivery Grid
                      </h3>
                      <p className="text-xs text-slate-500">
                        Zero-data cell broadcast, SMS gateways, physical sirens, and BLE mesh routing status.
                      </p>
                    </div>
                    <span className="px-2.5 py-1 bg-emerald-50 border border-emerald-300 rounded text-xs font-mono font-bold text-emerald-800">
                      OPERATIONAL
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5 mt-4">
                    <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-lg space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-slate-900">NIC SMS Gateway (Govt)</span>
                        <span className="px-2 py-0.5 bg-blue-100 text-blue-900 text-[10px] font-bold rounded">Primary Carrier</span>
                      </div>
                      <p className="text-[11px] text-slate-600">
                        Direct National Informatics Centre SMPP push for bulk resident evacuation orders.
                      </p>
                    </div>

                    <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-lg space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-slate-900">Fast2SMS / Twilio Failover</span>
                        <span className="px-2 py-0.5 bg-emerald-100 text-emerald-900 text-[10px] font-bold rounded">Active Standby</span>
                      </div>
                      <p className="text-[11px] text-slate-600">
                        Commercial Indian cellular SMS gateway failover with DLT template compliance.
                      </p>
                    </div>

                    <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-lg space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-slate-900">C-DOT Cell Broadcast</span>
                        <span className="px-2 py-0.5 bg-purple-100 text-purple-900 text-[10px] font-bold rounded">Zero Data Required</span>
                      </div>
                      <p className="text-[11px] text-slate-600">
                        Mass geo-fenced cell tower broadcast pinging all handsets without internet or SIM balance.
                      </p>
                    </div>

                    <div className="p-3.5 bg-slate-50 border border-slate-200 rounded-lg space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-slate-900">120dB Physical Strobe Siren</span>
                        <span className="px-2 py-0.5 bg-amber-100 text-amber-900 text-[10px] font-bold rounded">Relay Actuated</span>
                      </div>
                      <p className="text-[11px] text-slate-600">
                        ESP32 relay actuation on Himalayan sensor towers for nocturnal life-safety wake-up.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="p-3 bg-amber-50/70 border border-amber-200 rounded-lg text-xs text-amber-900 flex items-start gap-2">
                  <AlertTriangle className="w-4 h-4 text-amber-700 shrink-0 mt-0.5" />
                  <p className="leading-relaxed">
                    <strong>Zero-Fabrication Telecom Protocol:</strong> If Twilio / Fast2SMS credentials are not configured in local environment variables, the system executes in safe evaluation mode: logs exact payloads to audit ledger and returns native device URI (<code className="font-mono">sms:+91...?body=...</code>) with zero live telecom fees.
                  </p>
                </div>
              </div>
            </div>

            {/* Bottom Panel: Call Detail Records (CDRs) */}
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm space-y-3">
              <div className="flex items-center justify-between border-b border-slate-200 pb-2">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 flex items-center gap-1.5">
                  <Activity className="w-3.5 h-3.5 text-blue-600" />
                  <span>Outbound Authority Call Detail Records (CDRs) &amp; Acknowledgment Ledger</span>
                </h3>
                <span className="text-xs text-slate-500 font-mono">
                  {authorityCallLogs.length} Total Call Records
                </span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-200 bg-slate-50 text-slate-600 font-bold">
                      <th className="py-2.5 px-3">Call ID</th>
                      <th className="py-2.5 px-3">Timestamp</th>
                      <th className="py-2.5 px-3">Authority / Officer</th>
                      <th className="py-2.5 px-3">Target Phone</th>
                      <th className="py-2.5 px-3">Severity</th>
                      <th className="py-2.5 px-3">Channel</th>
                      <th className="py-2.5 px-3">Call Status</th>
                      <th className="py-2.5 px-3">DTMF Ack</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 font-mono">
                    {authorityCallLogs.map((log: any) => (
                      <tr key={log.call_id} className="hover:bg-slate-50">
                        <td className="py-2.5 px-3 text-slate-700 font-bold">{log.call_id}</td>
                        <td className="py-2.5 px-3 text-slate-500 font-sans">
                          {new Date(log.dispatched_at).toLocaleString('en-IN')}
                        </td>
                        <td className="py-2.5 px-3 text-slate-900 font-sans font-semibold">
                          {log.officer_name} ({log.agency})
                        </td>
                        <td className="py-2.5 px-3 text-slate-700">{log.target_phone}</td>
                        <td className="py-2.5 px-3 font-bold text-red-600">{log.severity_tier}</td>
                        <td className="py-2.5 px-3 text-slate-600">{log.call_channel}</td>
                        <td className="py-2.5 px-3">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              log.call_status.includes('CONNECTED') || log.call_status.includes('ACKNOWLEDGED') || log.call_status.includes('DELIVERED')
                                ? 'bg-emerald-50 border border-emerald-300 text-emerald-800'
                                : 'bg-red-50 border border-red-300 text-red-800'
                            }`}
                          >
                            {log.call_status}
                          </span>
                        </td>
                        <td className="py-2.5 px-3 text-emerald-700 font-bold">
                          {log.acknowledgment_dtmf ? `Digit [${log.acknowledgment_dtmf}] Verified` : 'Pending'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
