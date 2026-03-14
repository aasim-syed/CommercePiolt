import { useEffect, useState } from "react";

import StatusPanel from "@/components/StatusPanel";
import { fetchHealth, type HealthResponse } from "@/lib/api";

export default function SystemPage() {
  const [health, setHealth] = useState<HealthResponse | null>(null);

  useEffect(() => {
    void (async () => {
      try {
        setHealth(await fetchHealth());
      } catch {
        setHealth(null);
      }
    })();
  }, []);

  return (
    <div className="grid gap-6 lg:grid-cols-[360px_1fr]">
      <StatusPanel
        health={health}
        sessionId="s1"
        merchantId="m123"
        sessionState={null}
        lastToolData={null}
      />

      <section className="rounded-xl border bg-card p-8 shadow-sm">
        <p className="text-xs font-semibold tracking-[0.22em] text-muted-foreground uppercase">
          Readiness
        </p>
        <h2 className="mt-2 text-2xl font-semibold">Integration state</h2>
        <p className="mt-3 text-sm text-muted-foreground">
          This view keeps the demo honest: orchestration is active, the provider mode is visible,
          and external integrations can be swapped in without changing the operator workflow.
        </p>
      </section>
    </div>
  );
}
