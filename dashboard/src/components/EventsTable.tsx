import type { Event } from "@/lib/types";

interface Props {
  events: Event[];
}

export function EventsTable({ events }: Props) {
  if (events.length === 0) {
    return (
      <p className="card text-sm text-[var(--muted)]">No events for this run.</p>
    );
  }

  return (
    <div className="card overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-[var(--border)] text-[var(--muted)] text-xs uppercase tracking-widest">
            <th className="pb-2 text-left">Timestamp</th>
            <th className="pb-2 text-left">Type</th>
            <th className="pb-2 text-left">Latency</th>
            <th className="pb-2 text-left">Payload</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-[var(--border)]">
          {events.map((e) => (
            <tr key={e.event_id} className="align-top hover:bg-[var(--border)] transition-colors">
              <td className="py-2 pr-4 text-xs text-[var(--muted)] whitespace-nowrap">
                {new Date(e.timestamp).toLocaleTimeString()}
              </td>
              <td className="py-2 pr-4 font-mono text-xs text-veld-300">{e.event_type}</td>
              <td className="py-2 pr-4 text-xs text-[var(--muted)]">
                {e.latency_ms != null ? `${e.latency_ms.toFixed(1)}ms` : "—"}
              </td>
              <td className="py-2 text-xs text-[var(--muted)] max-w-xs truncate font-mono">
                {e.payload ? JSON.stringify(e.payload) : "—"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
