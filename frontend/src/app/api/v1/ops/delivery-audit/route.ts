import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET() {
  return NextResponse.json({
    generated_at: new Date().toISOString(),
    system_latency_target_sec: 45,
    channels: [
      {
        channel: 'C-DOT Cell Broadcast (Channel 4370)',
        dispatched_count: 48200,
        delivered_count: 47910,
        delivery_rate_pct: 99.4,
        avg_propagation_sec: 3.8,
        status: 'OPERATIONAL',
      },
      {
        channel: 'Automated VoIP Voice Telephony (SDRF/DM)',
        dispatched_count: 84,
        delivered_count: 82,
        delivery_rate_pct: 97.6,
        avg_propagation_sec: 14.2,
        status: 'OPERATIONAL',
      },
      {
        channel: 'Multilingual SMS (English / Hindi / Garhwali)',
        dispatched_count: 12400,
        delivered_count: 12150,
        delivery_rate_pct: 98.0,
        avg_propagation_sec: 6.5,
        status: 'OPERATIONAL',
      },
      {
        channel: 'Physical 120dB Alpine Sirens (IoT Relay)',
        dispatched_count: 24,
        delivered_count: 24,
        delivery_rate_pct: 100.0,
        avg_propagation_sec: 1.8,
        status: 'OPERATIONAL',
      },
    ],
  });
}
