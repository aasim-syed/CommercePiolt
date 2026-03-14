import { useEffect, useMemo, useState } from "react";

import StatusPanel from "@/components/StatusPanel";
import {
  fetchHealth,
  triggerDemoPaymentStatus,
  type HealthResponse,
} from "@/lib/api";
import { Button } from "@/components/ui/button";

type SystemPageProps = {
  sessionId: string;
  merchantId: string;
  sessionState: Record<string, unknown> | null;
  lastToolData: Record<string, unknown> | null;
  onSessionStateChange: (value: Record<string, unknown> | null) => void;
};

const demoStatuses = ["SUCCESS", "FAILED", "EXPIRED"] as const;

export default function SystemPage({
  sessionId,
  merchantId,
  sessionState,
  lastToolData,
  onSessionStateChange,
}: SystemPageProps) {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [pendingStatus, setPendingStatus] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);

  useEffect(() => {
    void (async () => {
      try {
        setHealth(await fetchHealth());
      } catch {
        setHealth(null);
      }
    })();
  }, []);

  const paymentRef = useMemo(() => {
    const stateRef = sessionState?.last_payment_ref;
    if (typeof stateRef === "string" && stateRef.trim()) return stateRef.trim();

    const dataRef = lastToolData?.payment_ref;
    if (typeof dataRef === "string" && dataRef.trim()) return dataRef.trim();

    return "";
  }, [lastToolData, sessionState]);

  async function handleTrigger(status: (typeof demoStatuses)[number]) {
    if (!paymentRef) {
      setFeedback("Create a payment link first so the demo trigger has a payment reference.");
      return;
    }

    setPendingStatus(status);
    setFeedback(null);

    try {
      const response = await triggerDemoPaymentStatus({
        payment_ref: paymentRef,
        status,
      });

      onSessionStateChange({
        ...(sessionState ?? {}),
        merchant_id: sessionState?.merchant_id ?? merchantId,
        last_payment_ref: paymentRef,
        last_payment_status: response.updated_status,
      });
      setFeedback(response.message);
    } catch (error) {
      setFeedback(error instanceof Error ? error.message : "Unable to trigger demo payment status.");
    } finally {
      setPendingStatus(null);
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[360px_1fr]">
      <StatusPanel
        health={health}
        sessionId={sessionId}
        merchantId={merchantId}
        sessionState={sessionState}
        lastToolData={lastToolData}
      />

      <section className="rounded-xl border bg-card p-8 shadow-sm">
        <p className="text-xs font-semibold tracking-[0.22em] text-muted-foreground uppercase">
          Demo controls
        </p>
        <h2 className="mt-2 text-2xl font-semibold">Webhook status trigger</h2>
        <p className="mt-3 text-sm text-muted-foreground">
          Use this panel to simulate Pine Labs status changes and show event-driven updates without
          waiting on live webhook delivery.
        </p>

        <div className="mt-6 rounded-lg border bg-background p-4">
          <div className="text-xs font-medium text-muted-foreground uppercase">Active payment ref</div>
          <div className="mt-2 break-all text-sm font-semibold">
            {paymentRef || "No payment reference yet"}
          </div>
        </div>

        <div className="mt-6 grid gap-3 sm:grid-cols-3">
          {demoStatuses.map((status) => (
            <Button
              key={status}
              type="button"
              variant="outline"
              className="h-11 rounded-lg"
              disabled={Boolean(pendingStatus)}
              onClick={() => void handleTrigger(status)}
            >
              {pendingStatus === status ? `Triggering ${status}...` : status}
            </Button>
          ))}
        </div>

        <div className="mt-6 rounded-lg border bg-muted/40 p-4 text-sm text-muted-foreground">
          {feedback ?? "Trigger a status after creating a payment link to update the active session."}
        </div>
      </section>
    </div>
  );
}
