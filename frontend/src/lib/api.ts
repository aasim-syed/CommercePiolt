export type ChatRequest = {
  message: string;
  session_id?: string;
  merchant_id?: string;
};

export type ToolCall = {
  tool_name: string;
  arguments: Record<string, unknown>;
};

export type ChatResponse = {
  reply: string;
  tool_called?: ToolCall | null;
  data?: Record<string, unknown> | null;
  session_state?: Record<string, unknown> | null;
};

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.trim() || "http://127.0.0.1:8000";

export async function sendChat(payload: ChatRequest): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/agent/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || "Request failed");
  }

  return response.json() as Promise<ChatResponse>;
}
