export const dynamic = "force-dynamic";

import { getTrend } from "@/lib/api";
import { TrendView } from "@/components/TrendView";

export default async function TrendPage() {
  const trend = await getTrend({ window: 50 }).catch(() => null);

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-veld-400">Trend Analysis</h1>
      <p className="text-sm text-[var(--muted)]">
        OLS regression across the last {trend?.window ?? 50} runs.
      </p>
      {trend ? (
        <TrendView trend={trend} />
      ) : (
        <p className="text-sm text-[var(--muted)]">
          Could not reach the API. Make sure the server is running.
        </p>
      )}
    </div>
  );
}
