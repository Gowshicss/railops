import axios from 'axios';
import {
  MaintenanceRequest,
  TrackAsset,
  MaintenancePlan,
  PlanDecision,
  DownstreamDispatch,
  ActivePossession,
  Station,
  StationMaintenanceHistory,
  WeeklyScheduleItem,
  DataSourceItem,
  DataImportLogItem,
  QualityReportItem,
  SolverMetrics,
  AuditLogItem
} from '../types/railops';

// Determine the base API URL dynamically:
// 1. If VITE_API_URL is configured (e.g. in production on Vercel), route requests to that host with /api
// 2. If unset (e.g. localhost dev), use '/api' to leverage Vite's local proxy to FastAPI
const rawApiUrl = import.meta.env.VITE_API_URL?.trim();

const getApiBaseUrl = (): string => {
  if (!rawApiUrl) {
    return '/api';
  }
  const cleanUrl = rawApiUrl.replace(/\/+$/, '');
  return cleanUrl.endsWith('/api') ? cleanUrl : `${cleanUrl}/api`;
};

const API_BASE = getApiBaseUrl();

const client = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Requests & Assets
  getRequests: async (department?: string, status?: string): Promise<MaintenanceRequest[]> => {
    const res = await client.get('/requests', { params: { department, status } });
    return res.data;
  },
  getRequestById: async (id: string): Promise<MaintenanceRequest> => {
    const res = await client.get(`/requests/${id}`);
    return res.data;
  },
  createRequest: async (data: Partial<MaintenanceRequest>): Promise<MaintenanceRequest> => {
    const res = await client.post('/requests', data);
    return res.data;
  },
  getAssets: async (dept_ref?: string, status?: string): Promise<TrackAsset[]> => {
    const res = await client.get('/requests/assets/inventory', { params: { dept_ref, status } });
    return res.data;
  },

  // Planning & Solver
  getPlans: async (request_id?: string, status?: string): Promise<MaintenancePlan[]> => {
    const res = await client.get('/plans', { params: { request_id, status } });
    return res.data;
  },
  generatePlans: async (request_id: string): Promise<MaintenancePlan[]> => {
    const res = await client.post('/plans/generate', { request_id });
    return res.data;
  },
  sendPlanToAuthority: async (plan_id: string): Promise<MaintenancePlan> => {
    const res = await client.put(`/plans/${plan_id}/send`);
    return res.data;
  },
  getSolverStatus: async (): Promise<SolverMetrics> => {
    const res = await client.get('/plans/optimization/status');
    return res.data;
  },

  // Authority Sign-Off & Dispatches
  getPendingAuthorityPlans: async (): Promise<MaintenancePlan[]> => {
    const res = await client.get('/authority/pending');
    return res.data;
  },
  approvePlan: async (plan_id: string, authority_user = 'Chief Controller', officer_id = 'CO MAS 4091', comments = ''): Promise<MaintenancePlan> => {
    const res = await client.post('/authority/approve', {
      plan_id,
      authority_user,
      officer_id,
      comments
    });
    return res.data;
  },
  modifyPlan: async (payload: {
    plan_id: string;
    modified_date: string;
    modified_start_time: string;
    modified_end_time: string;
    modified_duration: number;
    modified_track: string;
    modified_priority: string;
    operational_notes?: string;
  }): Promise<MaintenancePlan> => {
    const res = await client.post('/authority/modify', payload);
    return res.data;
  },
  rejectPlan: async (plan_id: string, rejection_reason: string, comments = ''): Promise<MaintenancePlan> => {
    const res = await client.post('/authority/reject', {
      plan_id,
      rejection_reason,
      comments
    });
    return res.data;
  },
  getDispatches: async (block_id: string): Promise<DownstreamDispatch[]> => {
    const res = await client.get(`/authority/dispatches/${block_id}`);
    return res.data;
  },
  getDecisionsHistory: async (decision?: string): Promise<PlanDecision[]> => {
    const res = await client.get('/authority/decisions', { params: { decision } });
    return res.data;
  },

  // Active Possessions & Execution Completion
  getActivePossessions: async (): Promise<ActivePossession[]> => {
    const res = await client.get('/possessions/active');
    return res.data;
  },
  completeMaintenance: async (payload: {
    block_id: string;
    station_code?: string;
    actual_start_time?: string;
    actual_end_time?: string;
    work_summary?: string;
    crew_gang?: string;
  }): Promise<StationMaintenanceHistory> => {
    const res = await client.post('/possessions/complete', payload);
    return res.data;
  },

  // Stations & History
  getStations: async (): Promise<Station[]> => {
    const res = await client.get('/stations');
    return res.data;
  },
  getStationHistory: async (code: string): Promise<StationMaintenanceHistory[]> => {
    const res = await client.get(`/stations/${code}/history`);
    return res.data;
  },
  searchHistory: async (params: {
    q?: string;
    station?: string;
    department?: string;
    year?: number;
    status?: string;
  }): Promise<StationMaintenanceHistory[]> => {
    const res = await client.get('/stations/records/search', { params });
    return res.data;
  },

  // Schedules
  getWeeklySchedule: async (): Promise<WeeklyScheduleItem[]> => {
    const res = await client.get('/schedules/weekly');
    return res.data;
  },
  getMonthlySchedule: async (month = '2026-09'): Promise<any> => {
    const res = await client.get('/schedules/monthly', { params: { month } });
    return res.data;
  },

  // Data Management & Quality Reports
  getDataSources: async (): Promise<DataSourceItem[]> => {
    const res = await client.get('/data/sources');
    return res.data;
  },
  getImportLogs: async (): Promise<DataImportLogItem[]> => {
    const res = await client.get('/data/import-logs');
    return res.data;
  },
  getDatasetInventory: async (): Promise<any[]> => {
    const res = await client.get('/data/inventory');
    return res.data;
  },
  getQualityReport: async (): Promise<QualityReportItem[]> => {
    const res = await client.get('/data/quality-report');
    return res.data;
  },
  simulateImport: async (dataset_name: string): Promise<DataImportLogItem> => {
    const res = await client.post('/data/simulate-import', null, { params: { dataset_name } });
    return res.data;
  },

  // Audit Logs
  getAuditLogs: async (): Promise<AuditLogItem[]> => {
    const res = await client.get('/audit/logs');
    return res.data;
  }
};
