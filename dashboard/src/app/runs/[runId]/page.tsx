export const dynamic = "force-dynamic";

import { getEvents } from "@/lib/api";
import { EventsTable } from "@/components/EventsTable";

interface Props {
  params: Promise<{ runId: string }>;
}

export default async function RunDetailPage({ params }: Props) {
  const { runId } = await params;
  const events = await getEvents(runId).catch(() => []);

  return (
    <div className="space-y-4">
      <div>
        <p className="text-xs text-[var(--muted)] mb-1">Run</p>
        <h1 className="text-lg font-mono text-veld-300 break-all">{runId}</h1>
      </div>
      <section>
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-widest text-[var(--muted)]">
          Events
        </h2>
        <EventsTable events={events} />
      </section>
    </div>
  );
}
