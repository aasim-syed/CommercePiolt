const flowSteps = [
  "1. Ask for reserve balance",
  "2. Create payment link for 1200",
  "3. Share payment URL and ref",
  "4. Check payment status",
  "5. Reflect webhook-driven update",
];

export default function OverviewPage() {
  return (
    <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
      <section className="rounded-xl border bg-card p-8 shadow-sm">
        <p className="text-xs font-semibold tracking-[0.22em] text-muted-foreground uppercase">
          Demo scope
        </p>
        <h2 className="mt-2 text-3xl font-semibold">Three-flow payments MVP</h2>
        <p className="mt-3 max-w-2xl text-sm text-muted-foreground">
          Frontend, orchestration, and session-driven payment flow are ready for the hackathon
          demo. Provider internals can be swapped later without changing the operator UI.
        </p>

        <div className="mt-8 grid gap-4 md:grid-cols-3">
          <Metric label="Primary flow" value="Payment links" />
          <Metric label="Secondary flow" value="Status tracking" />
          <Metric label="Financial flow" value="Reserve balance" />
        </div>
      </section>

      <section className="rounded-xl border bg-card p-6 shadow-sm">
        <p className="text-xs font-semibold tracking-[0.22em] text-muted-foreground uppercase">
          Judge path
        </p>
        <div className="mt-4 space-y-3">
          {flowSteps.map((step) => (
            <div key={step} className="rounded-lg border bg-background px-4 py-3 text-sm">
              {step}
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border bg-background p-4">
      <div className="text-xs font-medium text-muted-foreground uppercase">{label}</div>
      <div className="mt-2 text-base font-semibold">{value}</div>
    </div>
  );
}
