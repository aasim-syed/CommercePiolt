import { useMemo, useState } from "react";
import { Loader2, Sparkles } from "lucide-react";

import { sendChat, type ChatResponse } from "../lib/api";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Textarea } from "../components/ui/textarea";

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
  "Check status for pay_abc123",
];

export function ChatPage() {
  const [sessionId, setSessionId] = useState("s1");
  const [merchantId, setMerchantId] = useState("m123");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "I can help with payment links, payment status, and reserve balance. Try one of the prompts on the left.",
    },
  ]);

  const canSend = useMemo(() => message.trim().length > 0 && !loading, [message, loading]);

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

      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: response.reply,
        toolCalled: response.tool_called,
        data: response.data,
      };

      setMessages((prev) => [...prev, assistantMessage]);
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
    <div className="grid">
      <aside className="card sidebar">
        <h2>Starter prompts</h2>
        <p>
          Minimal chat UI using shadcn-style local components. Replace the mock backend
          tools later with real Pine Labs API integration.
        </p>

        <div className="pill-list">
          {starterPrompts.map((prompt) => (
            <button
              key={prompt}
              className="pill"
              onClick={() => void handleSubmit(prompt)}
              type="button"
            >
              {prompt}
            </button>
          ))}
        </div>

        <div style={{ marginTop: 20 }}>
          <h2 style={{ marginBottom: 10 }}>Supported actions</h2>
          <div className="pill-list">
            <span className="pill">Create payment link</span>
            <span className="pill">Check payment status</span>
            <span className="pill">Get reserve balance</span>
          </div>
        </div>
      </aside>

      <section className="card chat-panel">
        <div className="chat-header">
          <h2>Agent chat</h2>
          <p>Frontend sends chat messages to FastAPI and renders tool-call results.</p>
        </div>

        <div className="messages">
          {messages.length === 0 ? (
            <div className="empty">No messages yet.</div>
          ) : (
            messages.map((item) => (
              <div key={item.id} className={`message-row ${item.role}`}>
                <div className={`bubble ${item.role}`}>
                  {item.content}

                  {item.toolCalled ? (
                    <div className="tool-box">
                      <strong>Tool:</strong> {item.toolCalled.tool_name}
                      <br />
                      <strong>Args:</strong> {JSON.stringify(item.toolCalled.arguments)}
                    </div>
                  ) : null}

                  {item.data ? (
                    <div className="meta">Data: {JSON.stringify(item.data)}</div>
                  ) : null}
                </div>
              </div>
            ))
          )}

          {loading ? (
            <div className="message-row assistant">
              <div className="bubble assistant">
                <Loader2 size={16} style={{ verticalAlign: "middle", marginRight: 8 }} />
                Processing request...
              </div>
            </div>
          ) : null}
        </div>

        <div className="composer">
          <div className="row">
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
            placeholder="Type something like: create payment link for 1200"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
          />

          <Button disabled={!canSend} onClick={() => void handleSubmit()}>
            {loading ? (
              <>
                <Loader2 size={16} style={{ verticalAlign: "middle", marginRight: 8 }} />
                Sending...
              </>
            ) : (
              <>
                <Sparkles size={16} style={{ verticalAlign: "middle", marginRight: 8 }} />
                Send message
              </>
            )}
          </Button>
        </div>
      </section>
    </div>
  );
}
