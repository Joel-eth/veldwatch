import Link from "next/link";
import type { Run } from "@/lib/types";

function StatusBadge({ status }: { status: Run["status"] }) {
  const cls =
    status === "completed"
      ? "badge-completed"
      : status === "failed"
        ? "badge-failed"
        : "badge-running";
  return <span className={cls}>{status}</span>;
}

function fmt(iso: string | null) {
  if (!iso) return "—";
  return new Date(iso).toLocaleString();
}

function duration(start: string, end: string | null) {
  if (!end) return "—";
  const ms = new Date(end).getTime() - new Date(start).getTime();
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(1)}s`;
}

interface Props {
  runs: Run[];
}

export function RunsTable({ runs }: Props) {
  if (runs.length === 0) {
    return (
      <p className="card text-sm text-[var(--muted)]">No runs recorded yet.</p>
    );
  }

  return (
    <div className="card overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-[var(--border)] text-[var(--muted)] text-xs uppercase tracking-widest">
            <th className="pb-2 text-left">Run ID</th>
            <th className="pb-2 text-left">Agent</th>
            <th className="pb-2 text-left">Status</th>
            <th className="pb-2 text-left">Started</th>
            <th className="pb-2 text-left">Duration</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-[var(--border)]">
          {runs.map((r) => (
            <tr key={r.run_id} className="hover:bg-[var(--border)] transition-colors">
              <td className="py-2 pr-4 font-mono text-xs">
                <Link href={`/runs/${r.run_id}`} className="text-veld-400 hover:underline">
                  {r.run_id.slice(0, 12)}…
                </Link>
              </td>
              <td className="py-2 pr-4">{r.agent_id ?? "—"}</td>
              <td className="py-2 pr-4">
                <StatusBadge status={r.status} />
              </td>
              <td className="py-2 pr-4 text-xs text-[var(--muted)]">{fmt(r.started_at)}</td>
              <td className="py-2 text-xs text-[var(--muted)]">
                {duration(r.started_at, r.ended_at)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
