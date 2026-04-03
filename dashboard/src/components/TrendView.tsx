import type { TrendReport, TrendMetric } from "@/lib/types";

function directionIcon(d: TrendMetric["direction"]) {
  if (d === "improving") return "↑";
  if (d === "degrading")  return "↓";
  return "→";
}

function directionColor(d: TrendMetric["direction"]) {
  if (d === "improving") return "text-veld-400";
  if (d === "degrading")  return "text-red-400";
  return "text-[var(--muted)]";
}

function MetricCard({ metric, label }: { metric: TrendMetric; label: string }) {
  return (
    <div className="card space-y-3">
      <h3 className="text-xs uppercase tracking-widest text-[var(--muted)]">{label}</h3>
      <div className={`flex items-center gap-2 text-4xl font-bold font-mono ${directionColor(metric.direction)}`}>
        <span>{directionIcon(metric.direction)}</span>
        <span className="text-2xl capitalize">{metric.direction}</span>
      </div>
      <dl className="grid grid-cols-2 gap-x-6 gap-y-1 text-xs text-[var(--muted)]">
        <dt>Slope</dt>
        <dd className="text-[var(--text)] font-mono">{metric.slope.toFixed(5)}</dd>
        <dt>Start</dt>
        <dd className="font-mono">{metric.start_value.toFixed(3)}</dd>
        <dt>End</dt>
        <dd className="font-mono">{metric.end_value.toFixed(3)}</dd>
      </dl>
    </div>
  );
}

interface Props {
  trend: TrendReport;
}

export function TrendView({ trend }: Props) {
  return (
    <div className="space-y-6">
      {trend.any_regression && (
        <div className="rounded border border-red-800 bg-red-950 px-4 py-3 text-sm text-red-300">
          ⚠ Regression detected across the last {trend.run_count} runs.
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <MetricCard metric={trend.success_rate_trend} label="Success Rate Trend" />
        <MetricCard metric={trend.avg_duration_trend} label="Avg Duration Trend" />
      </div>

      <div className="card text-xs text-[var(--muted)] space-y-1">
        <p><span className="text-[var(--text)]">Window:</span> {trend.window} runs</p>
        <p><span className="text-[var(--text)]">Analysed:</span> {trend.run_count} runs</p>
        <p><span className="text-[var(--text)]">Any regression:</span>{" "}
          <span className={trend.any_regression ? "text-red-400" : "text-veld-400"}>
            {String(trend.any_regression)}
          </span>
        </p>
      </div>
    </div>
  );
}
