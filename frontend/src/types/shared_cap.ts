/**
 * Canonical CAP 1.2 & DMMC Disaster Early Warning Shared Types
 * Shared across Web Dashboard, Android Kotlin Native (mirrored), Backend API, and Admin/Ops Portal.
 * Strict weather.gov/alerts functional feature parity adapted for Uttarakhand, India.
 */

export type UttarakhandDistrict =
  | 'Dehradun'
  | 'Uttarkashi'
  | 'Chamoli'
  | 'Rudraprayag'
  | 'Tehri Garhwal'
  | 'Pauri Garhwal'
  | 'Pithoragarh'
  | 'Bageshwar'
  | 'Almora'
  | 'Champawat'
  | 'Nainital'
  | 'Haridwar'
  | 'Udham Singh Nagar';

export const UTTARAKHAND_DISTRICTS: UttarakhandDistrict[] = [
  'Dehradun',
  'Uttarkashi',
  'Chamoli',
  'Rudraprayag',
  'Tehri Garhwal',
  'Pauri Garhwal',
  'Pithoragarh',
  'Bageshwar',
  'Almora',
  'Champawat',
  'Nainital',
  'Haridwar',
  'Udham Singh Nagar',
];

export type HimalayanHazardType =
  | 'FLASH_FLOOD_GLOF'
  | 'LANDSLIDE_SLOPE_FAILURE'
  | 'CLOUDBURST_SEVERE_STORM'
  | 'EARTHQUAKE_SEISMIC'
  | 'FOREST_FIRE'
  | 'AVALANCHE_SNOWFALL';

export type AlertSeverity = 'CRITICAL' | 'SEVERE' | 'ADVISORY';

export type CapUrgency = 'Immediate' | 'Expected' | 'Future' | 'Past' | 'Unknown';
export type CapCertainty = 'Observed' | 'Likely' | 'Possible' | 'Unlikely' | 'Unknown';
export type CapStatus = 'Actual' | 'Exercise' | 'System' | 'Test' | 'Draft';
export type CapMsgType = 'Alert' | 'Update' | 'Cancel' | 'Ack' | 'Error';

export type SupportedLocale = 'en-IN' | 'hi-IN' | 'gbm-IN' | 'kfy-IN';

export type DeliveryChannelType =
  | 'CELL_BROADCAST'
  | 'SMS'
  | 'IVR_VOICE'
  | 'WHATSAPP'
  | 'FCM_PUSH';

export interface CapArea {
  areaDesc: string;
  polygon?: [number, number][]; // [[lat, lon], ...]
  circle?: string;
  altitude?: number;
  ceiling?: number;
}

export interface LocalizedCapInfo {
  language: SupportedLocale;
  headline: string;
  description: string;
  instruction: string;
  senderName: string;
  event: string;
}

export interface CapAlertItem {
  identifier: string;
  sender: string;
  senderName: string;
  sent: string; // ISO-8601 string
  status: CapStatus;
  msgType: CapMsgType;
  scope: 'Public' | 'Restricted' | 'Private';
  
  // Hazard Classification
  hazardType: HimalayanHazardType;
  severity: AlertSeverity;
  urgency: CapUrgency;
  certainty: CapCertainty;

  // Geographic Scope
  districts: UttarakhandDistrict[];
  area: CapArea;

  // Timestamps
  effective: string; // ISO-8601
  onset?: string;    // ISO-8601
  expires: string;  // ISO-8601
  ends?: string;     // ISO-8601

  // Localized Content
  localized: Record<SupportedLocale, LocalizedCapInfo>;

  // Source & Telemetry Metadata
  sourceFeed: 'NDMA_CAP' | 'NDMA_SACHET' | 'CWC_GAUGE' | 'IMD_NOWCAST' | 'IITR_EEW' | 'FOREST_FIRE_TRACK' | 'AVALANCHE_MONITOR' | 'DMMC_SEOC_OVERRIDE';
  sourceLastUpdated: string; // ISO-8601
  isFailClosedFallback?: boolean;
}

export interface HazardFeedStatus {
  hazardType: HimalayanHazardType;
  adapterName: string;
  isConfigured: boolean;
  status: 'ONLINE' | 'DATA_UNAVAILABLE' | 'ERROR' | 'CIRCUIT_OPEN' | 'STALE_WARNING';
  lastChecked: string;
  errorMessage?: string;
  endpointMasked?: string;
  latencyMs?: number;
  isStale?: boolean;
}

export interface AlertFilterOptions {
  district?: UttarakhandDistrict | 'ALL';
  severity?: AlertSeverity | 'ALL';
  urgency?: CapUrgency | 'ALL';
  certainty?: CapCertainty | 'ALL';
  hazardType?: HimalayanHazardType | 'ALL';
  searchQuery?: string;
}

// Crowdsourced Hazard Report Interface
export type HazardReportStatus = 'UNVERIFIED' | 'APPROVED' | 'REJECTED' | 'MERGED';
export type HazardReportCategory =
  | 'ROAD_BLOCKED'
  | 'LANDSLIDE_OBSERVED'
  | 'RIVER_SURGE'
  | 'STRUCTURE_DAMAGE'
  | 'SNOW_AVALANCHE_DRIFT'
  | 'OTHER';

export interface CrowdsourcedHazardReport {
  report_id: string;
  reporter_phone_hash: string;
  district: UttarakhandDistrict;
  hazardType: HimalayanHazardType;
  category: HazardReportCategory;
  description: string;
  photo_url?: string;
  lat: number;
  lon: number;
  submitted_at: string;
  status: HazardReportStatus;
  verification_notes?: string;
  verified_by?: string;
  is_unverified: boolean;
}

// Citizen "Mark Safe" Check-In Record
export type CitizenSafetyStatus = 'SAFE' | 'NEEDS_ASSISTANCE' | 'EVACUATED';

export interface CitizenCheckInRecord {
  checkin_id: string;
  phone_hash: string;
  status: CitizenSafetyStatus;
  district: UttarakhandDistrict;
  lat?: number;
  lon?: number;
  message?: string;
  timestamp: string;
  linked_contacts: string[];
}

// Shelter Occupancy Record
export interface ShelterOccupancyItem {
  shelter_id: string;
  name: string;
  district: UttarakhandDistrict;
  elevation_m: number;
  capacity: number;
  current_occupancy: number;
  is_live: boolean;
  last_updated: string;
  helpline: string;
  address?: string;
}

// Admin Audit Trail Log
export interface AdminAuditRecord {
  audit_id: string;
  action_type:
    | 'MANUAL_ALERT_ISSUED'
    | 'ALERT_OVERRIDE'
    | 'REPORT_APPROVED'
    | 'REPORT_REJECTED'
    | 'SHELTER_OCCUPANCY_UPDATED'
    | 'DISPATCH_TRIGGERED'
    | 'FEED_HEALTH_CHECK';
  admin_user: string;
  target_id: string;
  details: Record<string, any>;
  timestamp: string;
}
