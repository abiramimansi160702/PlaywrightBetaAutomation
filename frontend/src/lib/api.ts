export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE?.replace(/\/$/, "") || "http://127.0.0.1:8000";

export type RunFeatureStatus = {
  feature: string;
  status: "pending" | "running" | "passed" | "failed";
  started_at?: string | null;
  finished_at?: string | null;
  message?: string | null;
  artifacts?: Record<string, string> | null;
};

export type RunStatusResponse = {
  run_id: string;
  state: "queued" | "running" | "completed" | "failed";
  created_at?: string | null;
  finished_at?: string | null;
  current_feature?: string | null;
  features: RunFeatureStatus[];
};

export type StartRunRequest = {
  base_url: string;
  credentials: { email: string; password: string; mfa_code?: string };
  workspace: {
    business?: string;
    environment?: string;
    cloud_provider?: string;
    account?: string;
  };
};

export async function startRun(payload: StartRunRequest): Promise<{ run_id: string }> {
  const res = await fetch(`${API_BASE}/runs/e2e`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`Start run failed: ${res.status} ${await res.text()}`);
  return res.json();
}

export async function getRun(runId: string): Promise<RunStatusResponse> {
  const res = await fetch(`${API_BASE}/runs/${runId}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Get run failed: ${res.status} ${await res.text()}`);
  return res.json();
}