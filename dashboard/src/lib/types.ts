export interface Run {
  run_id: string;
  agent_id: string | null;
  status: "running" | "completed" | "failed";
  started_at: string;
  ended_at: string | null;
  error: string | null;
  metadata: Record<string, unknown> | null;
}

export interface RunListResponse {
  runs: Run[];
  total: number;
}

export interface Event {
  event_id: string;
  run_id: string;
  event_type: string;
  timestamp: string;
  latency_ms: number | null;
  payload: Record<string, unknown> | null;
}

export interface EventListResponse {
  events: Event[];
}

export interface Alert {
  alert_id: string;
  run_id: string | null;
  rule_name: string;
  message: string;
  severity: "info" | "warning" | "critical";
  triggered_at: string;
  resolved: boolean;
}

export interface AlertListResponse {
  alerts: Alert[];
  total: number;
}

export interface TrendMetric {
  name: string;
  slope: number;
  direction: "improving" | "degrading" | "stable";
  start_value: number;
  end_value: number;
}

export interface TrendReport {
  window: number;
  run_count: number;
  success_rate_trend: TrendMetric;
  avg_duration_trend: TrendMetric;
  any_regression: boolean;
}
