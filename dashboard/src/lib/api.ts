import type {
  AlertListResponse,
  EventListResponse,
  RunListResponse,
  TrendReport,
} from "./types";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    cache: "no-store",
    ...init,
  });
  if (!res.ok) {
    throw new Error(`API ${path} → ${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export function getRuns(params: { limit?: number; offset?: number } = {}): Promise<RunListResponse> {
  const qs = new URLSearchParams();
  if (params.limit !== undefined) qs.set("limit", String(params.limit));
  if (params.offset !== undefined) qs.set("offset", String(params.offset));
  return apiFetch<RunListResponse>(`/runs?${qs}`);
}

export function getEvents(runId: string): Promise<EventListResponse["events"]> {
  return apiFetch<EventListResponse>(`/runs/${runId}/events`).then((r) => r.events);
}

export function getAlerts(params: { limit?: number; resolved?: boolean } = {}): Promise<AlertListResponse> {
  const qs = new URLSearchParams();
  if (params.limit !== undefined) qs.set("limit", String(params.limit));
  if (params.resolved !== undefined) qs.set("resolved", String(params.resolved));
  return apiFetch<AlertListResponse>(`/alerts?${qs}`);
}

export function getTrend(params: { window?: number } = {}): Promise<TrendReport> {
  const qs = new URLSearchParams();
  if (params.window !== undefined) qs.set("window", String(params.window));
  return apiFetch<TrendReport>(`/runs/trend?${qs}`);
}
