import { FilterParams, DashboardResponse, DealItem, WorkOrderItem, ChatResponse, ExecutiveSummaryResponse, DataQualityReportResponse } from './types';

const API_BASE = "http://127.0.0.1:8000";

function getHeaders() {
  const token = typeof window !== 'undefined' ? localStorage.getItem('mondayApiToken') || '' : '';
  const dealBoardId = typeof window !== 'undefined' ? localStorage.getItem('mondayDealBoardId') || '' : '';
  const workBoardId = typeof window !== 'undefined' ? localStorage.getItem('mondayWorkBoardId') || '' : '';
  return {
    token,
    dealBoardId,
    workBoardId
  };
}

export async function fetchDashboard(filters: FilterParams): Promise<DashboardResponse> {
  const { token, dealBoardId, workBoardId } = getHeaders();
  const query = new URLSearchParams({
    apiToken: token,
    dealBoardId,
    workBoardId,
    ...(filters.startDate && { startDate: filters.startDate }),
    ...(filters.endDate && { endDate: filters.endDate }),
    ...(filters.sector && { sector: filters.sector }),
    ...(filters.dealStage && { dealStage: filters.dealStage }),
    ...(filters.salesperson && { salesperson: filters.salesperson }),
    ...(filters.workOrderStatus && { workOrderStatus: filters.workOrderStatus }),
    ...(filters.customer && { customer: filters.customer }),
  });
  const res = await fetch(`${API_BASE}/dashboard?${query}`);
  if (!res.ok) throw new Error("Failed to fetch dashboard data");
  return res.json();
}

export async function fetchDeals(filters: FilterParams): Promise<{ deals: DealItem[]; count: number }> {
  const { token, dealBoardId } = getHeaders();
  const query = new URLSearchParams({
    apiToken: token,
    dealBoardId,
    ...(filters.startDate && { startDate: filters.startDate }),
    ...(filters.endDate && { endDate: filters.endDate }),
    ...(filters.sector && { sector: filters.sector }),
    ...(filters.dealStage && { dealStage: filters.dealStage }),
    ...(filters.salesperson && { salesperson: filters.salesperson }),
  });
  const res = await fetch(`${API_BASE}/deals?${query}`);
  if (!res.ok) throw new Error("Failed to fetch deals");
  return res.json();
}

export async function fetchWorkOrders(filters: FilterParams): Promise<{ workOrders: WorkOrderItem[]; count: number }> {
  const { token, workBoardId } = getHeaders();
  const query = new URLSearchParams({
    apiToken: token,
    workBoardId,
    ...(filters.startDate && { startDate: filters.startDate }),
    ...(filters.endDate && { endDate: filters.endDate }),
    ...(filters.sector && { sector: filters.sector }),
    ...(filters.workOrderStatus && { workOrderStatus: filters.workOrderStatus }),
    ...(filters.customer && { customer: filters.customer }),
  });
  const res = await fetch(`${API_BASE}/workorders?${query}`);
  if (!res.ok) throw new Error("Failed to fetch work orders");
  return res.json();
}

export async function sendChatMessage(message: string, filters: FilterParams): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, filters })
  });
  if (!res.ok) throw new Error("Chat assistant failed");
  return res.json();
}

export async function fetchExecutiveSummary(): Promise<ExecutiveSummaryResponse> {
  const { token, dealBoardId, workBoardId } = getHeaders();
  const res = await fetch(`${API_BASE}/summary`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ apiToken: token, dealBoardId, workBoardId })
  });
  if (!res.ok) throw new Error("Failed to generate summary");
  return res.json();
}

export async function fetchForecast(): Promise<{ forecast: any[]; expectedRevenue: number }> {
  const { token, dealBoardId, workBoardId } = getHeaders();
  const res = await fetch(`${API_BASE}/forecast`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ apiToken: token, dealBoardId, workBoardId })
  });
  if (!res.ok) throw new Error("Failed to fetch forecast");
  return res.json();
}

export async function fetchDataQualityReport(): Promise<DataQualityReportResponse> {
  const { token, dealBoardId, workBoardId } = getHeaders();
  const query = new URLSearchParams({ apiToken: token, dealBoardId, workBoardId });
  const res = await fetch(`${API_BASE}/data-quality?${query}`);
  if (!res.ok) throw new Error("Failed to fetch data quality report");
  return res.json();
}

export async function globalSearch(query: string): Promise<{ deals: DealItem[]; workOrders: WorkOrderItem[] }> {
  const { token, dealBoardId, workBoardId } = getHeaders();
  const searchParams = new URLSearchParams({ query, apiToken: token, dealBoardId, workBoardId });
  const res = await fetch(`${API_BASE}/search?${searchParams}`);
  if (!res.ok) throw new Error("Global search failed");
  return res.json();
}

export async function verifyConnection(token: string, dealBoardId: string, workBoardId: string): Promise<any> {
  const res = await fetch(`${API_BASE}/settings/verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mondayApiToken: token, dealBoardId, workBoardId })
  });
  if (!res.ok) throw new Error("Settings verification failed");
  return res.json();
}
