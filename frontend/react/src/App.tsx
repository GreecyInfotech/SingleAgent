import { useState } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const API_KEY = import.meta.env.VITE_API_KEY || "";

const agents = [
  "customer-agent",
  "loan-agent",
  "fraud-agent",
  "support-agent",
  "recommendation-agent",
];

async function apiFetch(path: string, options: RequestInit = {}) {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (API_KEY) headers["X-Api-Key"] = API_KEY;
  const res = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (!res.ok) throw new Error(`API ${res.status}`);
  return res.json();
}

export default function App() {
  const [selected, setSelected] = useState(agents[0]);
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    try {
      const data = await apiFetch(`/api/v1/platform/agents/${selected}/execute`, {
        method: "POST",
        body: JSON.stringify({ query }),
      });
      setResult(JSON.stringify(data, null, 2));
    } catch (err) {
      setResult(`Error: ${err instanceof Error ? err.message : "failed"}`);
    } finally {
      setLoading(false);
    }
  };

  const handleOrchestrate = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const data = await apiFetch("/api/v1/platform/orchestrate", {
        method: "POST",
        body: JSON.stringify({ message: query }),
      });
      setResult(JSON.stringify(data, null, 2));
    } catch (err) {
      setResult(`Error: ${err instanceof Error ? err.message : "failed"}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <h1>Agent Console</h1>
      <form onSubmit={handleSubmit}>
        <select value={selected} onChange={(e) => setSelected(e.target.value)}>
          {agents.map((a) => (
            <option key={a} value={a}>{a}</option>
          ))}
        </select>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter your query..."
        />
        <div className="buttons">
          <button type="submit" disabled={loading}>Execute</button>
          <button type="button" onClick={handleOrchestrate} disabled={loading}>Auto-Route</button>
        </div>
      </form>
      {result && <pre className="result">{result}</pre>}
    </div>
  );
}
