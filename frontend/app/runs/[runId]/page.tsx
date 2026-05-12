"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { getRun, RunStatusResponse, RunFeatureStatus, API_BASE } from "@/src/lib/api";

export default function RunPage() {
  const params = useParams<{ runId: string }>();
  const runId = params.runId;

  const [data, setData] = useState<RunStatusResponse | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [polling, setPolling] = useState(true);

  useEffect(() => {
    if (!runId || !polling) return;

    let alive = true;

    async function tick() {
      try {
        const d = await getRun(runId);
        if (!alive) return;
        setData(d);
        setErr(null);
        if (d.state === "completed" || d.state === "failed") {
          setPolling(false);
        }
      } catch (e: any) {
        if (!alive) return;
        setErr(e?.message || String(e));
      }
    }

    tick();
    const id = setInterval(tick, 1500);
    return () => {
      alive = false;
      clearInterval(id);
    };
  }, [runId, polling]);

  const progress = useMemo(() => {
    const features = data?.features || [];
    if (!features.length) return 0;
    const done = features.filter((f) => f.status === "passed" || f.status === "failed").length;
    return Math.round((done / features.length) * 100);
  }, [data]);

  return (
    <main style={{ maxWidth: 900, margin: "0 auto", padding: 24, fontFamily: "ui-sans-serif, system-ui" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", gap: 12, flexWrap: "wrap" }}>
        <div>
          <h1 style={{ fontSize: 24, fontWeight: 800 }}>Run Progress</h1>
          <div style={{ color: "#555", marginTop: 6 }}>
            Run ID: <code>{runId}</code>
          </div>
        </div>

        <Link href="/" style={{ color: "#111", textDecoration: "underline" }}>
          Start another run
        </Link>
      </div>

      <section style={{ marginTop: 18, border: "1px solid #eee", borderRadius: 12, padding: 16 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
          <Badge text={data?.state || "loading"} kind={stateKind(data?.state)} />
          <div style={{ color: "#555" }}>
            Current feature: <b>{data?.current_feature || "-"}</b>
          </div>
          <div style={{ marginLeft: "auto", color: "#555" }}>{progress}%</div>
        </div>

        <div style={{ marginTop: 12, height: 10, background: "#f2f2f2", borderRadius: 999 }}>
          <div style={{ width: `${progress}%`, height: "100%", background: "#111", borderRadius: 999 }} />
        </div>

        {err && (
          <div style={{ marginTop: 12, border: "1px solid #f5c2c7", background: "#f8d7da", color: "#842029", padding: 12, borderRadius: 10 }}>
            {err}
          </div>
        )}
      </section>

      <section style={{ marginTop: 18 }}>
        <h2 style={{ fontSize: 16, fontWeight: 800, marginBottom: 10 }}>Features</h2>
        <div style={{ display: "grid", gap: 10 }}>
          {(data?.features || []).map((f) => (
            <FeatureRow key={f.feature} f={f} />
          ))}
        </div>
      </section>

      <section style={{ marginTop: 24, color: "#666" }}>
        <div>
          API: <code>{API_BASE}</code>
        </div>
      </section>
    </main>
  );
}

function FeatureRow({ f }: { f: RunFeatureStatus }) {
  return (
    <div style={{ border: "1px solid #eee", borderRadius: 12, padding: 14 }}>
      <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
        <div style={{ fontWeight: 800 }}>{humanFeatureName(f.feature)}</div>
        <Badge text={f.status} kind={featureKind(f.status)} />
        <div style={{ marginLeft: "auto", color: "#666", fontSize: 12 }}>
          {f.started_at ? `started: ${f.started_at}` : ""}
          {f.finished_at ? ` • finished: ${f.finished_at}` : ""}
        </div>
      </div>

      {f.message && (
        <div style={{ marginTop: 8, color: f.status === "failed" ? "#842029" : "#444" }}>
          {f.message}
        </div>
      )}

      {f.artifacts && (
        <div style={{ marginTop: 10, display: "flex", gap: 10, flexWrap: "wrap" }}>
          {"screenshot" in f.artifacts && <code style={artifactStyle}>{String(f.artifacts["screenshot"])}</code>}
          {"html" in f.artifacts && <code style={artifactStyle}>{String(f.artifacts["html"])}</code>}
        </div>
      )}
    </div>
  );
}

function Badge({ text, kind }: { text: string; kind: "neutral" | "good" | "bad" | "warn" }) {
  const colors =
    kind === "good"
      ? { bg: "#d1e7dd", fg: "#0f5132", bd: "#badbcc" }
      : kind === "bad"
        ? { bg: "#f8d7da", fg: "#842029", bd: "#f5c2c7" }
        : kind === "warn"
          ? { bg: "#fff3cd", fg: "#664d03", bd: "#ffecb5" }
          : { bg: "#e2e3e5", fg: "#41464b", bd: "#d3d6d8" };

  return (
    <span
      style={{
        padding: "4px 10px",
        borderRadius: 999,
        background: colors.bg,
        color: colors.fg,
        border: `1px solid ${colors.bd}`,
        fontSize: 12,
        fontWeight: 800,
        textTransform: "uppercase",
        letterSpacing: 0.4,
      }}
    >
      {text}
    </span>
  );
}

function stateKind(state?: string) {
  if (!state) return "neutral" as const;
  if (state === "completed") return "good" as const;
  if (state === "failed") return "bad" as const;
  if (state === "running") return "warn" as const;
  return "neutral" as const;
}

function featureKind(status: RunFeatureStatus["status"]) {
  if (status === "passed") return "good" as const;
  if (status === "failed") return "bad" as const;
  if (status === "running") return "warn" as const;
  return "neutral" as const;
}

function humanFeatureName(key: string) {
  const map: Record<string, string> = {
    aiops: "AIOps (Create EC2)",
    finops_cost_analytics: "FinOps (Cost Analytics)",
    inventory_management: "Inventory Management",
    log_analytics_agent: "Log Analytics Agent",
    os_management: "OS Management",
  };
  return map[key] || key;
}

const artifactStyle: React.CSSProperties = {
  fontSize: 12,
  padding: "6px 8px",
  background: "#f6f6f6",
  border: "1px solid #eee",
  borderRadius: 8,
};