export const dynamic = "force-dynamic";

import { getRuns } from "@/lib/api";
import { RunsTable } from "@/components/RunsTable";

export default async function RunsPage() {
  const { runs } = await getRuns({ limit: 100 }).catch(() => ({ runs: [] }));

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-veld-400">Runs</h1>
      <RunsTable runs={runs} />
    </div>
  );
}
