"use client";

import { useEffect, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || "";

const DOMAIN_AGENTS = [
  { id: "customer-agent", name: "Customer Agent", description: "Customer intelligence & segmentation" },
  { id: "loan-agent", name: "Loan Agent", description: "Loan processing & risk assessment" },
  { id: "fraud-agent", name: "Fraud Agent", description: "Fraud detection & investigation" },
  { id: "support-agent", name: "Support Agent", description: "IT & customer support automation" },
  { id: "recommendation-agent", name: "Recommendation Agent", description: "Personalized recommendations" },
];

async function apiFetch(path: string, options: RequestInit = {}) {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (API_KEY) headers["X-Api-Key"] = API_KEY;
  const res = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export default function Dashboard() {
  const [health, setHealth] = useState("checking...");
  const [agents, setAgents] = useState<typeof DOMAIN_AGENTS>([]);
  const [selectedAgent, setSelectedAgent] = useState("customer-agent");
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    apiFetch("/api/v1/health")
      .then((d) => setHealth(d.status))
      .catch(() => setHealth("unreachable"));

    apiFetch("/api/v1/platform/agents")
      .then((d) => setAgents(d.agents?.length ? d.agents : DOMAIN_AGENTS))
      .catch(() => setAgents(DOMAIN_AGENTS));
  }, []);

  const executeAgent = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const data = await apiFetch(`/api/v1/platform/agents/${selectedAgent}/execute`, {
        method: "POST",
        body: JSON.stringify({ query, customer_id: "CUST-001", user_id: "USER-001" }),
      });
      setResult(JSON.stringify(data, null, 2));
    } catch (e) {
      setResult(`Error: ${e instanceof Error ? e.message : "Unknown error"}`);
    } finally {
      setLoading(false);
    }
  };

  const orchestrate = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const data = await apiFetch("/api/v1/platform/orchestrate", {
        method: "POST",
        body: JSON.stringify({ message: query }),
      });
      setResult(JSON.stringify(data, null, 2));
    } catch (e) {
      setResult(`Error: ${e instanceof Error ? e.message : "Unknown error"}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main style={{ padding: "2rem", maxWidth: 1200, margin: "0 auto" }}>
      <header style={{ marginBottom: "2rem" }}>
        <h1 style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>Enterprise Agent Platform</h1>
        <p style={{ color: "#94a3b8" }}>
          API Status:{" "}
          <span style={{ color: health === "healthy" ? "#4ade80" : "#f87171" }}>{health}</span>
        </p>
      </header>

      <section style={{ marginBottom: "2rem" }}>
        <h2 style={{ fontSize: "1.25rem", marginBottom: "1rem" }}>Agent Console</h2>
        <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", marginBottom: "1rem" }}>
          <select
            value={selectedAgent}
            onChange={(e) => setSelectedAgent(e.target.value)}
            style={{ padding: "0.5rem", borderRadius: 6, background: "#1e293b", color: "#e2e8f0", border: "1px solid #334155" }}
          >
            {DOMAIN_AGENTS.map((a) => (
              <option key={a.id} value={a.id}>{a.name}</option>
            ))}
          </select>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your query..."
            style={{ flex: 1, minWidth: 200, padding: "0.5rem", borderRadius: 6, background: "#1e293b", color: "#e2e8f0", border: "1px solid #334155" }}
          />
          <button onClick={executeAgent} disabled={loading} style={{ padding: "0.5rem 1rem", borderRadius: 6, background: "#2563eb", color: "#fff", border: "none", cursor: "pointer" }}>
            Execute Agent
          </button>
          <button onClick={orchestrate} disabled={loading} style={{ padding: "0.5rem 1rem", borderRadius: 6, background: "#7c3aed", color: "#fff", border: "none", cursor: "pointer" }}>
            Auto-Route
          </button>
        </div>
        {result && (
          <pre style={{ background: "#1e293b", padding: "1rem", borderRadius: 8, overflow: "auto", fontSize: "0.85rem" }}>
            {result}
          </pre>
        )}
      </section>

      <section>
        <h2 style={{ fontSize: "1.25rem", marginBottom: "1rem" }}>Domain Agents ({agents.length})</h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "1rem" }}>
          {(agents.length ? agents : DOMAIN_AGENTS).map((agent: { id?: string; name: string; description?: string }) => (
            <div key={agent.id || agent.name} style={{ background: "#1e293b", borderRadius: 8, padding: "1.25rem", border: "1px solid #334155" }}>
              <h3 style={{ marginBottom: "0.5rem" }}>{agent.name}</h3>
              <p style={{ color: "#94a3b8", fontSize: "0.875rem" }}>{agent.description || ""}</p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
