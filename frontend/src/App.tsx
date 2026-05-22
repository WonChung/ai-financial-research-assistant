import { useState } from "react";

type HealthState = "idle" | "checking" | "healthy" | "error";

const apiBaseUrl =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") ??
  "http://127.0.0.1:8000";

function App() {
  const [healthState, setHealthState] = useState<HealthState>("idle");
  const [message, setMessage] = useState("Backend health has not been checked.");

  async function checkHealth() {
    setHealthState("checking");
    setMessage("Checking backend health...");

    try {
      const response = await fetch(`${apiBaseUrl}/health`);

      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`);
      }

      const data = (await response.json()) as { status?: string };

      if (data.status !== "ok") {
        throw new Error("Backend returned an unexpected health response.");
      }

      setHealthState("healthy");
      setMessage("Backend is healthy.");
    } catch (error) {
      setHealthState("error");
      setMessage(error instanceof Error ? error.message : "Health check failed.");
    }
  }

  return (
    <main className="page">
      <section className="hero" aria-labelledby="page-title">
        <p className="eyebrow">Research workflow starter</p>
        <h1 id="page-title">AI Financial Research Assistant</h1>
        <p className="lede">
          A focused workspace for financial research, document-backed answers,
          and portfolio-risk summaries. Upload and RAG workflows are intentionally
          not enabled yet.
        </p>

        <div className="health-panel">
          <div>
            <h2>Backend Status</h2>
            <p className={`status status-${healthState}`}>{message}</p>
          </div>
          <button
            type="button"
            onClick={checkHealth}
            disabled={healthState === "checking"}
          >
            {healthState === "checking" ? "Checking..." : "Check Health"}
          </button>
        </div>
      </section>
    </main>
  );
}

export default App;
