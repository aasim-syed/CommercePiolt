import { useEffect, useMemo, useState } from "react";
import { Loader2, Sparkles } from "lucide-react";

import StatusPanel from "@/components/StatusPanel";
import { fetchHealth, sendChat, type ChatResponse, type HealthResponse } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  toolCalled?: ChatResponse["tool_called"];
  data?: ChatResponse["data"];
};

const starterPrompts = [
  "Create payment link for 1200",
  "What is my reserve balance?",
  "Check payment status",
];

function formatToolData(data: Record<string, unknown> | null | undefined): string | null {
  if (!data) return null;

  const paymentUrl =
    typeof data.payment_url === "string" && data.payment_url.trim()
      ? data.payment_url.trim()
      : null;
  const paymentRef =
    typeof data.payment_ref === "string" && data.payment_ref.trim()
      ? data.payment_ref.trim()
      : null;
  const status =
    typeof data.status === "string" && data.status.trim() ? data.status.trim() : null;
  const availableBalance =
    typeof data.available_balance === "number" || typeof data.available_balance === "string"
      ? String(data.available_balance)
      : null;
  const currency =
    typeof data.currency === "string" && data.currency.trim() ? data.currency.trim() : "INR";

  if (paymentUrl || paymentRef || status || availableBalance) {
    const parts: string[] = [];

    if (paymentRef) parts.push(`Payment Ref: ${paymentRef}`);
    if (status) parts.push(`Status: ${status}`);
    if (availableBalance) parts.push(`Reserve Balance: ${availableBalance} ${currency}`);
    if (paymentUrl) parts.push(`Payment URL: ${paymentUrl}`);

    return parts.join("\n");
  }

  return JSON.stringify(data, null, 2);
}

export default function ChatPage() {
  const [sessionId, setSessionId] = useState("s1");
  const [merchantId, setMerchantId] = useState("m123");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [sessionState, setSessionState] = useState<Record<string, unknown> | null>(null);
  const [lastToolData, setLastToolData] = useState<Record<string, unknown> | null>(null);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "I can help with payment links, payment status, and reserve balance. Try one of the prompts below.",
    },
  ]);

  const canSend = useMemo(() => message.trim().length > 0 && !loading, [message, loading]);

  useEffect(() => {
    void (async () => {
      try {
        const nextHealth = await fetchHealth();
        setHealth(nextHealth);
      } catch {
        setHealth(null);
      }
    })();
  }, []);

  async function handleSubmit(nextMessage?: string) {
    const finalMessage = (nextMessage ?? message).trim();
    if (!finalMessage || loading) return;

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: finalMessage,
    };

    setMessages((prev) => [...prev, userMessage]);
    setMessage("");
    setLoading(true);

    try {
      const response = await sendChat({
        message: finalMessage,
        session_id: sessionId.trim() || undefined,
        merchant_id: merchantId.trim() || undefined,
      });

      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: response.reply,
          toolCalled: response.tool_called,
          data: response.data,
        },
      ]);
      setSessionState(response.session_state ?? null);
      setLastToolData(response.data ?? null);
    } catch (error) {
      const err =
        error instanceof Error ? error.message : "Unknown error while calling backend.";

      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: `Backend error: ${err}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[300px_320px_1fr]">
      <aside className="rounded-xl border bg-card p-6 shadow-sm">
        <h2 className="text-lg font-semibold">Demo workflow</h2>
        <p className="mt-2 text-sm text-muted-foreground">
          Use the guided flow below to keep the demo consistent and fast.
        </p>

        <div className="mt-5 flex flex-col gap-2.5">
          {starterPrompts.map((prompt) => (
            <Button
              key={prompt}
              type="button"
              variant="outline"
              className="h-auto justify-start rounded-lg px-4 py-3 text-left whitespace-normal"
              onClick={() => void handleSubmit(prompt)}
              disabled={loading}
            >
              {prompt}
            </Button>
          ))}
        </div>

        <div className="mt-6">
          <h3 className="text-sm font-medium">Supported actions</h3>
          <div className="mt-3 flex flex-wrap gap-2">
            <span className="rounded-md border bg-secondary px-3 py-1 text-xs text-secondary-foreground">
              Create payment link
            </span>
            <span className="rounded-md border bg-secondary px-3 py-1 text-xs text-secondary-foreground">
              Check payment status
            </span>
            <span className="rounded-md border bg-secondary px-3 py-1 text-xs text-secondary-foreground">
              Get reserve balance
            </span>
          </div>
        </div>
      </aside>

      <StatusPanel
        health={health}
        loading={loading}
        sessionId={sessionId}
        merchantId={merchantId}
        sessionState={sessionState}
        lastToolData={lastToolData}
      />

      <section className="flex min-h-[75vh] flex-col rounded-xl border bg-card shadow-sm">
        <div className="border-b px-6 py-5">
          <h2 className="text-lg font-semibold">Operator console</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Chat interface for the three MVP payment workflows.
          </p>
        </div>

        <div className="flex flex-1 flex-col gap-4 overflow-y-auto p-6">
          {messages.map((item) => {
            const formattedData = formatToolData(item.data);

            return (
              <div
                key={item.id}
                className={`flex ${item.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl border px-4 py-3 text-sm shadow-sm ${
                    item.role === "user"
                    ? "border-primary bg-primary text-primary-foreground"
                      : "bg-background"
                  }`}
                >
                  <div>{item.content}</div>

                  {item.toolCalled ? (
                    <div className="mt-3 rounded-lg border bg-muted/60 p-3">
                      <div>
                        <strong>Tool:</strong> {item.toolCalled.tool_name}
                      </div>
                      <div className="mt-1 break-all text-xs text-muted-foreground">
                        <strong>Args:</strong> {JSON.stringify(item.toolCalled.arguments)}
                      </div>
                    </div>
                  ) : null}

                  {formattedData ? (
                    <pre className="mt-3 whitespace-pre-wrap rounded-lg border bg-muted/60 p-3 text-xs text-muted-foreground">
                      {formattedData}
                    </pre>
                  ) : null}

                  {typeof item.data?.payment_url === "string" && item.data.payment_url ? (
                    <div className="mt-3 text-xs">
                      <a href={item.data.payment_url} target="_blank" rel="noreferrer">
                        Open payment link
                      </a>
                    </div>
                  ) : null}
                </div>
              </div>
            );
          })}

          {loading ? (
            <div className="flex justify-start">
              <div className="rounded-lg border bg-background px-4 py-3 text-sm shadow-sm">
                <Loader2 className="mr-2 inline-block size-4 animate-spin align-text-bottom" />
                Processing request...
              </div>
            </div>
          ) : null}
        </div>

        <div className="border-t p-6">
          <div className="grid gap-3 md:grid-cols-2">
            <Input
              placeholder="Session ID"
              value={sessionId}
              onChange={(e) => setSessionId(e.target.value)}
            />
            <Input
              placeholder="Merchant ID"
              value={merchantId}
              onChange={(e) => setMerchantId(e.target.value)}
            />
          </div>

          <Textarea
            className="mt-3"
            placeholder="Type something like: create payment link for 1200"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={(e) => {
              if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
                e.preventDefault();
                void handleSubmit();
              }
            }}
          />

          <Button className="mt-3" disabled={!canSend} onClick={() => void handleSubmit()}>
            {loading ? (
              <>
                <Loader2 className="size-4 animate-spin" />
                Sending...
              </>
            ) : (
              <>
                <Sparkles className="size-4" />
                Send message
              </>
            )}
          </Button>
        </div>
      </section>
    </div>
  );
}
