import type { EvaluationRequest, EvaluationResponse } from "../types/evaluation";

const API_BASE = import.meta.env.VITE_API_BASE ?? "";

function parseApiError(status: number, body: unknown): string {
  if (body && typeof body === "object") {
    const b = body as Record<string, unknown>;
    if (typeof b.detail === "string") return b.detail;
    if (typeof b.code === "string" && typeof b.detail === "string") {
      return `${b.code}: ${b.detail}`;
    }
    if (Array.isArray(b.detail)) {
      return b.detail
        .map((item) => {
          if (item && typeof item === "object" && "msg" in item) {
            const loc = "loc" in item ? JSON.stringify(item.loc) : "";
            return `${loc}: ${String(item.msg)}`;
          }
          return JSON.stringify(item);
        })
        .join("; ");
    }
  }

  if (status === 500 || status === 502) {
    return (
      `Request failed (${status}). Start the backend: ` +
      "cd backend && uvicorn app.main:app --reload --port 8001"
    );
  }

  return `Request failed (${status})`;
}

export async function checkHealth(): Promise<boolean> {
  const res = await fetch(`${API_BASE}/health`);
  return res.ok;
}

export async function uploadFile(file: File): Promise<{ file_id: string }> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_BASE}/api/v1/uploads`, {
    method: "POST",
    body: form,
  });
  const body: unknown = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(parseApiError(res.status, body));
  return body as { file_id: string };
}

export async function evaluate(
  request: EvaluationRequest,
): Promise<EvaluationResponse> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE}/api/v1/evaluate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
    });
  } catch (err) {
    const apiBase = import.meta.env.VITE_API_BASE || "(not set)";
    throw new Error(
      `Cannot reach the API at ${apiBase}. ` +
      `Check that VITE_API_BASE is set in Vercel environment variables. ` +
      `Error: ${err instanceof Error ? err.message : String(err)}`,
    );
  }

  const body: unknown = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(parseApiError(res.status, body));
  return body as EvaluationResponse;
}
