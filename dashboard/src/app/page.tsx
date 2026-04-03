export const dynamic = "force-dynamic";

import { getRuns } from "@/lib/api";
import { RunsTable } from "@/components/RunsTable";
import { StatCard } from "@/components/StatCard";

export default async function HomePage() {
  const { runs } = await getRuns({ limit: 50 }).catch(() => ({ runs: [] }));

  const total = runs.length;
  const completed = runs.filter((r) => r.status === "completed").length;
  const failed = runs.filter((r) => r.status === "failed").length;
  const running = runs.filter((r) => r.status === "running").length;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-veld-400">Overview</h1>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatCard label="Total Runs" value={total} />
        <StatCard label="Completed" value={completed} variant="success" />
        <StatCard label="Failed" value={failed} variant="danger" />
        <StatCard label="Running" value={running} variant="info" />
      </div>

      <section>
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-widest text-[var(--muted)]">
          Recent Runs
        </h2>
        <RunsTable runs={runs.slice(0, 20)} />
      </section>
    </div>
  );
}
