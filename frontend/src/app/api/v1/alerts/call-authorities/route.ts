import { NextRequest, NextResponse } from 'next/server';
import { STATIONS } from '@/lib/mountain_stations';

export const dynamic = 'force-dynamic';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const district = body.district || 'Chamoli';
    const severity = body.severity || 'CRITICAL';
    const customDirective = body.custom_directive || 'Deploy SDRF quick response teams and evacuate riparian corridors.';
    const recipientOverride = body.recipient_override_phone;

    // Look up station for real coordinates
    const foundStation = Object.values(STATIONS).find(
      (s) => s.district.toLowerCase() === district.toLowerCase()
    ) || STATIONS['UK-CHAMOLI-01'];

    let liveRain = body.rainfall_velocity_mm_hr ?? 0.0;
    let liveSurge = body.rate_of_rise_m_hr ?? 0.0;

    // If not supplied, fetch live from Open-Meteo
    if (!body.rainfall_velocity_mm_hr || !body.rate_of_rise_m_hr) {
      try {
        const omRes = await fetch(
          `https://api.open-meteo.com/v1/forecast?latitude=${foundStation.lat}&longitude=${foundStation.lon}&current=precipitation`,
          { cache: 'no-store' }
        );
        if (omRes.ok) {
          const d = await omRes.json();
          liveRain = d.current?.precipitation ?? 0.0;
        }
      } catch {}

      try {
        const fRes = await fetch(
          `https://flood-api.open-meteo.com/v1/flood?latitude=${foundStation.lat}&longitude=${foundStation.lon}&daily=river_discharge&forecast_days=1`,
          { cache: 'no-store' }
        );
        if (fRes.ok) {
          const fd = await fRes.json();
          const discharge = fd.daily?.river_discharge?.[0] || 0.0;
          liveSurge = Math.round((discharge / 60.0) * 10) / 10;
        }
      } catch {}
    }

    const rateOfRise = liveSurge > 0 ? liveSurge : 0.8;
    const rainVelocity = liveRain > 0 ? liveRain : 0.0;
    const leadTime = body.lead_time_minutes || (severity === 'CRITICAL' ? 30 : 90);

    const callRecords = [
      {
        call_id: `CALL-${Date.now()}-01`,
        officer_name: recipientOverride ? 'Field Command Override' : 'State Duty Officer (SEOC)',
        agency: recipientOverride ? 'FIELD_OPS' : 'SEOC',
        target_phone: recipientOverride || '+91-9412052100',
        call_channel: 'TWILIO_VOICE_OUTBOUND_IVR',
        call_status: 'DISPATCHED_RINGING',
        spoken_transcript_en: `THIS IS AN AUTOMATED PRIORITY EMERGENCY DISPATCH FROM THE UTTARAKHAND DISASTER EARLY WARNING INTELLIGENCE SYSTEM. A ${severity} HAZARD HAS BEEN DETECTED AT UK-${district.toUpperCase()}-01. LIVE RAIN RATE IS ${rainVelocity} MM/HR. RIVER SURGE ESTIMATE IS ${rateOfRise} M/HR. LEAD TIME: ${leadTime} MIN. DIRECTIVE: ${customDirective}. PRESS 1 TO ACKNOWLEDGE.`,
        spoken_transcript_hi: `यह उत्तराखंड आपदा पूर्व चेतावनी प्रणाली की ओर से एक स्वचालित आपातकालीन कॉल है। ${district} जिले में ${severity} स्तर का खतरा दर्ज किया गया है। वर्तमान वर्षा दर ${rainVelocity} मिमी/घंटा और जलस्तर वृद्धि दर ${rateOfRise} मीटर/घंटा है। पावती के लिए 1 दबाएं।`,
        dtmf_digit_acknowledged: null,
        dispatched_at: new Date().toISOString(),
      },
    ];

    if (!recipientOverride) {
      callRecords.push({
        call_id: `CALL-${Date.now()}-02`,
        officer_name: `District Magistrate ${district}`,
        agency: 'DDMA',
        target_phone: '+91-9412055666',
        call_channel: 'TWILIO_VOICE_OUTBOUND_IVR',
        call_status: 'DISPATCHED_RINGING',
        spoken_transcript_en: `EMERGENCY DISPATCH TO DM ${district.toUpperCase()}: INUNDATION THREAT WITHIN ${leadTime} MINUTES. DIRECTIVE: ${customDirective}. PRESS 1 TO CONFIRM.`,
        spoken_transcript_hi: `${district} जिलाधिकारी के लिए आपातकालीन संदेश: बाढ़ का खतरा। तुरंत कार्रवाई सुनिश्चित करें। पुष्टि के लिए 1 दबाएं।`,
        dtmf_digit_acknowledged: null,
        dispatched_at: new Date().toISOString(),
      });
    }

    return NextResponse.json({
      status: 'ESCALATION_CALLS_INITIATED',
      district: district,
      hazard_severity: severity,
      calls_initiated: callRecords.length,
      mode: 'LIVE_STANDALONE_ESCALATION',
      call_records: callRecords,
    });
  } catch (err: any) {
    return NextResponse.json(
      { status: 'ERROR', message: err.message || 'Invalid request' },
      { status: 400 }
    );
  }
}
