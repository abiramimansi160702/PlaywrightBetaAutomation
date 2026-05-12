"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { startRun } from "@/src/lib/api";

export default function HomePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const [baseUrl, setBaseUrl] = useState("https://beta.codly.ai");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [mfaCode, setMfaCode] = useState("");

  const [business, setBusiness] = useState("");
  const [environment, setEnvironment] = useState("");
  const [cloudProvider, setCloudProvider] = useState("");
  const [account, setAccount] = useState("");

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErr(null);
    setLoading(true);
    try {
      const resp = await startRun({
        base_url: baseUrl,
        credentials: { email, password, mfa_code: mfaCode || undefined },
        workspace: {
          business: business || undefined,
          environment: environment || undefined,
          cloud_provider: cloudProvider || undefined,
          account: account || undefined,
        },
      });

      router.push(`/runs/${resp.run_id}`);
    } catch (e: any) {
      setErr(e?.message || String(e));
      setLoading(false);
    }
  }

  return (
    <main style={{ maxWidth: 900, margin: "0 auto", padding: 24, fontFamily: "ui-sans-serif, system-ui" }}>
      <h1 style={{ fontSize: 28, fontWeight: 700 }}>Portal E2E Runner</h1>
      <p style={{ color: "#555", marginTop: 8 }}>
        Enter credentials and workspace, then run the full suite (AIOps → FinOps → Inventory → Log Analytics → OS).
      </p>

      <form onSubmit={onSubmit} style={{ marginTop: 24, display: "grid", gap: 14 }}>
        <section style={{ border: "1px solid #eee", borderRadius: 12, padding: 16 }}>
          <h2 style={{ fontSize: 16, fontWeight: 700, marginBottom: 12 }}>Target</h2>
          <label style={{ display: "grid", gap: 6 }}>
            <span>Base URL</span>
            <input value={baseUrl} onChange={(e) => setBaseUrl(e.target.value)} required
              style={inputStyle} placeholder="https://beta.codly.ai" />
          </label>
        </section>

        <section style={{ border: "1px solid #eee", borderRadius: 12, padding: 16 }}>
          <h2 style={{ fontSize: 16, fontWeight: 700, marginBottom: 12 }}>Login</h2>

          <div style={{ display: "grid", gap: 12, gridTemplateColumns: "1fr 1fr" }}>
            <label style={{ display: "grid", gap: 6 }}>
              <span>Email</span>
              <input value={email} onChange={(e) => setEmail(e.target.value)} required style={inputStyle} />
            </label>
            <label style={{ display: "grid", gap: 6 }}>
              <span>MFA code (optional)</span>
              <input value={mfaCode} onChange={(e) => setMfaCode(e.target.value)} style={inputStyle} />
            </label>
          </div>

          <label style={{ display: "grid", gap: 6, marginTop: 12 }}>
            <span>Password</span>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required style={inputStyle} />
          </label>
        </section>

        <section style={{ border: "1px solid #eee", borderRadius: 12, padding: 16 }}>
          <h2 style={{ fontSize: 16, fontWeight: 700, marginBottom: 12 }}>Workspace (optional)</h2>
          <p style={{ color: "#666", marginTop: -6, marginBottom: 12 }}>
            If your app requires workspace selection, fill these. (Your backend can ignore them if not needed.)
          </p>

          <div style={{ display: "grid", gap: 12, gridTemplateColumns: "1fr 1fr" }}>
            <label style={{ display: "grid", gap: 6 }}>
              <span>Business</span>
              <input value={business} onChange={(e) => setBusiness(e.target.value)} style={inputStyle} />
            </label>
            <label style={{ display: "grid", gap: 6 }}>
              <span>Environment</span>
              <input value={environment} onChange={(e) => setEnvironment(e.target.value)} style={inputStyle} />
            </label>
            <label style={{ display: "grid", gap: 6 }}>
              <span>Cloud Provider</span>
              <input value={cloudProvider} onChange={(e) => setCloudProvider(e.target.value)} style={inputStyle} />
            </label>
            <label style={{ display: "grid", gap: 6 }}>
              <span>Account</span>
              <input value={account} onChange={(e) => setAccount(e.target.value)} style={inputStyle} />
            </label>
          </div>
        </section>

        {err && (
          <div style={{ border: "1px solid #f5c2c7", background: "#f8d7da", color: "#842029", padding: 12, borderRadius: 10 }}>
            {err}
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          style={{
            padding: "12px 16px",
            borderRadius: 12,
            border: "1px solid #111",
            background: loading ? "#ddd" : "#111",
            color: loading ? "#444" : "#fff",
            fontWeight: 700,
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          {loading ? "Starting..." : "Run E2E Suite"}
        </button>
      </form>
    </main>
  );
}

const inputStyle: React.CSSProperties = {
  padding: "10px 12px",
  borderRadius: 10,
  border: "1px solid #ddd",
  outline: "none",
};