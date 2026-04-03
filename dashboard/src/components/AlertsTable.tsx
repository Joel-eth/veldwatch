import type { Alert } from "@/lib/types";

function SeverityBadge({ severity }: { severity: Alert["severity"] }) {
  const cls =
    severity === "critical"
      ? "badge-failed"
      : severity === "warning"
        ? "badge-warning"
        : "badge-running";
  return <span className={cls}>{severity}</span>;
}

interface Props {
  alerts: Alert[];
}

export function AlertsTable({ alerts }: Props) {
  if (alerts.length === 0) {
    return (
      <p className="card text-sm text-[var(--muted)]">No alerts triggered.</p>
    );
  }

  return (
    <div className="card overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-[var(--border)] text-[var(--muted)] text-xs uppercase tracking-widest">
            <th className="pb-2 text-left">Rule</th>
            <th className="pb-2 text-left">Severity</th>
            <th className="pb-2 text-left">Message</th>
            <th className="pb-2 text-left">Triggered</th>
            <th className="pb-2 text-left">Resolved</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-[var(--border)]">
          {alerts.map((a) => (
            <tr key={a.alert_id} className="hover:bg-[var(--border)] transition-colors">
              <td className="py-2 pr-4 font-mono text-xs">{a.rule_name}</td>
              <td className="py-2 pr-4">
                <SeverityBadge severity={a.severity} />
              </td>
              <td className="py-2 pr-4 text-xs text-[var(--muted)] max-w-xs truncate">{a.message}</td>
              <td className="py-2 pr-4 text-xs text-[var(--muted)] whitespace-nowrap">
                {new Date(a.triggered_at).toLocaleString()}
              </td>
              <td className="py-2 text-xs">
                {a.resolved ? (
                  <span className="badge-completed">yes</span>
                ) : (
                  <span className="badge-failed">no</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
