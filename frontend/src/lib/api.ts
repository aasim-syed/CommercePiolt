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

export type HealthResponse = {
  ok: boolean;
  app_name: string;
  environment: string;
  pine_labs_mode: string;
  pine_labs_base_url_configured: boolean;
  pine_labs_merchant_id_configured: boolean;
  bedrock_configured: boolean;
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
    let errorMessage = "Request failed";

    try {
      const errorData = await response.json();
      errorMessage =
        errorData?.detail ||
        errorData?.message ||
        `Request failed with status ${response.status}`;
    } catch {
      const text = await response.text();
      errorMessage = text || `Request failed with status ${response.status}`;
    }

    throw new Error(errorMessage);
  }

  return response.json() as Promise<ChatResponse>;
}

export async function fetchHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`);

  if (!response.ok) {
    throw new Error(`Health request failed with status ${response.status}`);
  }

  return response.json() as Promise<HealthResponse>;
}
