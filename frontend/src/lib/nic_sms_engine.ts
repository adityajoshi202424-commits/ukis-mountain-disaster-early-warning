/**
 * DMMC Uttarakhand Early-Warning Platform — Multi-Channel Language-Synchronized SMS Engine
 * Cross-platform TypeScript implementation modeled after NDMA Sachet & C-DOT architecture.
 */

export interface CAPAlertInfo {
  language: string;
  category: string;
  event: string;
  urgency: string;
  severity: string;
  certainty: string;
  headline: string;
  description: string;
  instruction: string;
  area: {
    areaDesc: string;
    polygon: string;
  };
}

export interface CAPAlertPayload {
  identifier: string;
  sender: string;
  sent: string;
  status: string;
  msgType: string;
  scope: string;
  info: Array<CAPAlertInfo>;
}

export interface OutboundSMSRequest {
  recipientPhoneNumber: string;
  assignedLocale: 'hi' | 'en' | 'gb' | 'ku';
  hazardType: string;
  severity: string;
  rawPayload: CAPAlertPayload;
}

export async function dispatchSynchronizedSMS(request: OutboundSMSRequest): Promise<{ status: string; body: string }> {
  const targetGateway = process.env.NIC_SMS_GATEWAY_URL || 'https://smsapi.nic.in/api/v2/send';
  const authToken = process.env.NIC_SMS_AUTH_TOKEN || '';

  // Select matching localized string block dynamically matching user configuration profile
  const matchedInfoBlock =
    request.rawPayload.info.find(
      (info) => info.language.toLowerCase().substring(0, 2) === request.assignedLocale
    ) || request.rawPayload.info[0]; // Fallback cleanly to root default info element

  const smsBody =
    `[DMMC ALERT - ${matchedInfoBlock.event.toUpperCase()}]\n` +
    `Severity: ${matchedInfoBlock.severity}\n` +
    `Action Required: ${matchedInfoBlock.instruction}\n` +
    `Safe Hubs: Dial 1070 for local emergency aid channels.`;

  try {
    const response = await fetch(targetGateway, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${authToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        to: request.recipientPhoneNumber,
        body: smsBody,
        priority: 'HIGH_ALERT_EMERGENCY',
        encoding: 'UTF-8', // Explicitly support regional Unicode scripts
      }),
    });

    return {
      status: response.ok ? 'DELIVERED' : 'BUFFERED',
      body: smsBody,
    };
  } catch (err) {
    return {
      status: 'BUFFERED_FOR_LOCAL_SIM_RELAY',
      body: smsBody,
    };
  }
}
