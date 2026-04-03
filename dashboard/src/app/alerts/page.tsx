export const dynamic = "force-dynamic";

import { getAlerts } from "@/lib/api";
import { AlertsTable } from "@/components/AlertsTable";

export default async function AlertsPage() {
  const { alerts } = await getAlerts({ limit: 100 }).catch(() => ({ alerts: [] }));

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-veld-400">Alerts</h1>
      <AlertsTable alerts={alerts} />
    </div>
  );
}
