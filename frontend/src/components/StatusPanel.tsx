import { AlertCircle, CheckCircle2, CircleDashed, Wallet } from "lucide-react";

import type { HealthResponse } from "@/lib/api";

type StatusPanelProps = {
  health: HealthResponse | null;
  loading?: boolean;
  sessionId: string;
  merchantId: string;
  sessionState?: Record<string, unknown> | null;
  lastToolData?: Record<string, unknown> | null;
};

function readString(value: unknown): string | null {
  return typeof value === "string" && value.trim() ? value.trim() : null;
}

function StatusBadge({
  label,
  ok,
}: {
  label: string;
  ok: boolean;
}) {
  return (
    <div
      className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-medium ${
        ok
          ? "border-emerald-200 bg-emerald-50 text-emerald-700"
          : "border-amber-200 bg-amber-50 text-amber-700"
      }`}
    >
      {ok ? <CheckCircle2 className="size-3.5" /> : <AlertCircle className="size-3.5" />}
      {label}
    </div>
  );
}

export default function StatusPanel({
  health,
  loading = false,
  sessionId,
  merchantId,
  sessionState,
  lastToolData,
}: StatusPanelProps) {
  const resolvedMerchantId =
    readString(sessionState?.merchant_id) ?? readString(merchantId) ?? "Not set";
  const lastPaymentRef =
    readString(sessionState?.last_payment_ref) ?? readString(lastToolData?.payment_ref) ?? "None";
  const lastPaymentStatus =
    readString(sessionState?.last_payment_status) ?? readString(lastToolData?.status) ?? "Unknown";
  const providerMode =
    readString(lastToolData?.provider_mode) ??
    (health?.pine_labs_mode === "mock" ? "sandbox_stub" : health?.pine_labs_mode) ??
    "Unknown";

  return (
    <aside className="rounded-xl border bg-card p-5 shadow-sm">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-xs font-semibold tracking-[0.22em] text-muted-foreground uppercase">
            System status
          </p>
          <h2 className="mt-1 text-lg font-semibold"> control panel</h2>
        </div>
        <div className="grid size-10 place-items-center rounded-md bg-primary/8 text-primary">
          <Wallet className="size-5" />
        </div>
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        <StatusBadge label={`Bedrock ${health?.bedrock_configured ? "ready" : "not ready"}`} ok={Boolean(health?.bedrock_configured)} />
        <StatusBadge
          label={`Pine Labs ${
            health?.pine_labs_auth_configured
              ? health?.pine_labs_mode === "http"
                ? "auth ready"
                : "stub mode"
              : "pending"
          }`}
          ok={Boolean(health?.pine_labs_auth_configured || health?.pine_labs_mode === "mock")}
        />
      </div>

      <div className="mt-5 grid gap-3">
        <div className="rounded-lg border bg-background p-4">
          <div className="flex items-center gap-2 text-xs font-medium text-muted-foreground uppercase">
            <CircleDashed className="size-3.5" />
            Provider mode
          </div>
          <div className="mt-2 text-base font-semibold">{providerMode}</div>
        </div>

        <div className="grid gap-3 sm:grid-cols-2">
          <MetricCard label="Session ID" value={sessionId.trim() || "session-auto"} />
          <MetricCard label="Merchant ID" value={resolvedMerchantId} />
          <MetricCard label="Last Payment Ref" value={lastPaymentRef} />
          <MetricCard label="Last Status" value={lastPaymentStatus} />
        </div>
      </div>

      <p className="mt-4 text-xs text-muted-foreground">
        {loading
          ? "Refreshing status from the latest chat response."
          : "Status reflects current config plus the latest session state."}
      </p>
    </aside>
  );
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border bg-background p-4">
      <div className="text-xs font-medium text-muted-foreground uppercase">{label}</div>
      <div className="mt-2 break-all text-sm font-semibold">{value}</div>
    </div>
  );
}
