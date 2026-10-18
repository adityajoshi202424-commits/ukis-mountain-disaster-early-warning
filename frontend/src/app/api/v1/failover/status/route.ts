import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const simulateCut = searchParams.get('simulate_cut') === 'true';

  return NextResponse.json({
    architectureName: 'HIM-KAVACH Zero-Downtime Active-Active Failover Grid',
    targetRTO: '< 10 seconds (Recovery Time Objective)',
    targetRPO: '0 seconds (Recovery Point Objective - Synchronous Replication)',
    systemHealth: simulateCut ? 'FAILOVER_ACTIVE' : 'NOMINAL_OPTIMAL',
    timestamp: new Date().toISOString(),

    ingestionGateways: [
      {
        tier: 'PRIMARY',
        name: 'Cellular 4G/5G MQTT Broker & SWAN Optical Fiber',
        status: simulateCut ? 'OFFLINE_SEVERED' : 'ONLINE_HEALTHY',
        packetLossPct: simulateCut ? 100 : 0.02,
        latencyMs: simulateCut ? null : 24,
      },
      {
        tier: 'FAILOVER_1',
        name: 'LoRaWAN Mountain Mesh (Peer-to-Peer Valley Sensors)',
        status: 'ONLINE_ACTIVE',
        packetLossPct: 0.15,
        latencyMs: 140,
        coverage: 'Alpine sensor clusters to ridge-top solar gateway',
      },
      {
        tier: 'FAILOVER_2',
        name: 'ISRO INSAT-3DR / GSAT Satellite VSAT Direct Uplink',
        status: 'STANDBY_HOT',
        packetLossPct: 0.0,
        latencyMs: 380,
        coverage: 'Direct satellite burst telemetry (High-altitude GLOF lakes & dams)',
      },
    ],

    serverComputeNodes: {
      primaryDC: {
        location: 'UKSDC (Uttarakhand State Data Centre, ITDA Dehradun)',
        seismicZone: 'Zone IV',
        status: simulateCut ? 'CONNECTIVITY_DROP_FAILOVER_TRIGGERED' : 'PRIMARY_ACTIVE',
        cpuUtilizationPct: 42,
        activeConnections: simulateCut ? 0 : 3840,
      },
      drCloudNode: {
        location: 'GI Cloud (MeghRaj / NIC National Data Centre, Delhi/Hyderabad)',
        seismicZone: 'Zone II (Geographically Dispersed)',
        status: simulateCut ? 'PROMOTED_TO_ACTIVE_PRIMARY' : 'HOT_STANDBY_SYNC',
        syncLagSeconds: 0,
        replicationState: 'SYNCHRONOUS_STREAMING',
        bgpAnycastRerouteTimeSec: simulateCut ? 6.4 : 0,
      },
      edgeCDN: {
        provider: 'Cloudflare / NIC State Edge CDN',
        publicCacheHitRatioPct: 98.4,
        protection: 'Public visitor traffic isolated; SEOC officer network completely protected',
      },
    },

    databaseCluster: {
      engine: 'PostgreSQL 16 + PostGIS + TimescaleDB Partitioning',
      haManager: 'Patroni 3.2 + etcd distributed consensus',
      connectionPooler: 'PgBouncer (Transaction Pooling, 5,000 max clients)',
      primaryDb: simulateCut ? 'MeghRaj DR Node (Auto-Promoted by etcd in 2.8s)' : 'UKSDC Dehradun (Master)',
      replicaDb: simulateCut ? 'UKSDC Offline Node (Re-syncing)' : 'MeghRaj Cloud (Hot Standby Synchronous)',
      timescalePartitioning: 'Hourly hyper-tables for high-frequency IoT sensor telemetry',
      redisCluster: 'In-Memory Pub/Sub for sub-second WebSocket hazard polygon updates',
    },

    notificationCircuitBreaker: {
      cbsChannel4370: 'ACTIVE (Cell Broadcast bypasses cellular data congestion)',
      cdacSmppSms: 'OPERATIONAL (PRI/SMPP direct government shortcode 1070)',
      ivrVoiceBridge: 'ONLINE (Spoken Hindi / Garhwali / Kumaoni via BSNL/Airtel PRI trunk)',
      lorawanSirens: 'ARMED (Direct RF hardware trigger for riverbank hooters)',
    },
  });
}
