import { type FormEvent, useState } from "react";

type HealthState = "idle" | "checking" | "healthy" | "error";
type UploadState = "idle" | "uploading" | "uploaded" | "error";
type AskState = "idle" | "asking" | "answered" | "error";
type RiskState = "idle" | "summarizing" | "summarized" | "error";

type UploadedDocument = {
  document_id: string;
  filename: string;
  character_count: number;
  created_at: string;
  chunk_count: number;
};

type Citation = {
  source_id: number;
  document_id: string;
  filename: string;
  chunk_index: number;
  start_char: number;
  end_char: number;
};

type AskResponse = {
  answer: string;
  citations: Citation[];
};

type HoldingInput = {
  id: number;
  ticker: string;
  name: string;
  sector: string;
  weightPercent: string;
};

type LargestPosition = {
  ticker: string;
  name: string;
  sector: string | null;
  weight_percent: number;
};

type PortfolioRiskSummary = {
  concentration_risk_notes: string[];
  largest_positions: LargestPosition[];
  sector_concentration_notes: string[];
  missing_data_warnings: string[];
  risk_explanation: string;
  disclaimer: string;
};

const apiBaseUrl =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") ??
  "http://127.0.0.1:8000";

const emptyHolding = (id: number): HoldingInput => ({
  id,
  ticker: "",
  name: "",
  sector: "",
  weightPercent: "",
});

const sampleHoldings: HoldingInput[] = [
  {
    id: 1,
    ticker: "AAPL",
    name: "Apple",
    sector: "Technology",
    weightPercent: "20",
  },
  {
    id: 2,
    ticker: "JPM",
    name: "JPMorgan Chase",
    sector: "Financials",
    weightPercent: "15",
  },
  {
    id: 3,
    ticker: "JNJ",
    name: "Johnson & Johnson",
    sector: "Healthcare",
    weightPercent: "15",
  },
  {
    id: 4,
    ticker: "XOM",
    name: "Exxon Mobil",
    sector: "Energy",
    weightPercent: "10",
  },
  {
    id: 5,
    ticker: "VTI",
    name: "Vanguard Total Stock Market ETF",
    sector: "Broad Market",
    weightPercent: "40",
  },
];

function App() {
  const [healthState, setHealthState] = useState<HealthState>("idle");
  const [message, setMessage] = useState("Backend health has not been checked.");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadState, setUploadState] = useState<UploadState>("idle");
  const [uploadMessage, setUploadMessage] = useState("No document uploaded yet.");
  const [uploadedDocument, setUploadedDocument] =
    useState<UploadedDocument | null>(null);
  const [documentId, setDocumentId] = useState<string | null>(null);
  const [question, setQuestion] = useState("");
  const [askState, setAskState] = useState<AskState>("idle");
  const [askMessage, setAskMessage] = useState(
    "Upload a document, then ask a question.",
  );
  const [askResponse, setAskResponse] = useState<AskResponse | null>(null);
  const [holdings, setHoldings] = useState<HoldingInput[]>([emptyHolding(1)]);
  const [nextHoldingId, setNextHoldingId] = useState(2);
  const [riskState, setRiskState] = useState<RiskState>("idle");
  const [riskMessage, setRiskMessage] = useState(
    "Enter holdings to summarize portfolio risk.",
  );
  const [riskSummary, setRiskSummary] = useState<PortfolioRiskSummary | null>(
    null,
  );

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

  async function uploadDocument(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!selectedFile) {
      setUploadState("error");
      setUploadMessage("Choose a .txt file before uploading.");
      return;
    }

    setUploadState("uploading");
    setUploadMessage("Uploading document...");

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);

      const response = await fetch(`${apiBaseUrl}/documents/upload`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : `Upload failed with status ${response.status}`,
        );
      }

      const uploaded = data as UploadedDocument;
      setUploadedDocument(uploaded);
      setDocumentId(uploaded.document_id);
      setUploadState("uploaded");
      setUploadMessage("Document uploaded.");
      setAskState("idle");
      setAskMessage("Ready for a question.");
      setAskResponse(null);
    } catch (error) {
      setUploadedDocument(null);
      setDocumentId(null);
      setUploadState("error");
      setUploadMessage(error instanceof Error ? error.message : "Upload failed.");
    }
  }

  async function askQuestion(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmedQuestion = question.trim();

    if (!documentId) {
      setAskState("error");
      setAskMessage("Upload a document before asking a question.");
      return;
    }

    if (!trimmedQuestion) {
      setAskState("error");
      setAskMessage("Enter a question before asking.");
      return;
    }

    setAskState("asking");
    setAskMessage("Retrieving context and generating an answer...");
    setAskResponse(null);

    try {
      const response = await fetch(`${apiBaseUrl}/research/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          document_id: documentId,
          question: trimmedQuestion,
          top_k: 5,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : `Ask failed with status ${response.status}`,
        );
      }

      setAskResponse(data as AskResponse);
      setAskState("answered");
      setAskMessage("Answer generated.");
    } catch (error) {
      setAskState("error");
      setAskMessage(error instanceof Error ? error.message : "Ask failed.");
    }
  }

  function updateHolding(
    id: number,
    field: keyof Omit<HoldingInput, "id">,
    value: string,
  ) {
    setHoldings((currentHoldings) =>
      currentHoldings.map((holding) =>
        holding.id === id ? { ...holding, [field]: value } : holding,
      ),
    );
  }

  function addHolding() {
    setHoldings((currentHoldings) => [
      ...currentHoldings,
      emptyHolding(nextHoldingId),
    ]);
    setNextHoldingId((currentId) => currentId + 1);
  }

  function removeHolding(id: number) {
    setHoldings((currentHoldings) =>
      currentHoldings.length > 1
        ? currentHoldings.filter((holding) => holding.id !== id)
        : currentHoldings,
    );
  }

  function loadSamplePortfolio() {
    setHoldings(sampleHoldings);
    setNextHoldingId(6);
    setRiskState("idle");
    setRiskMessage("Sample portfolio loaded. Weights total 100%.");
    setRiskSummary(null);
  }

  async function summarizeRisk(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const payloadHoldings = holdings
      .map((holding) => ({
        ticker: holding.ticker.trim(),
        name: holding.name.trim(),
        sector: holding.sector.trim() || undefined,
        weightInput: holding.weightPercent.trim(),
        weight_percent: Number(holding.weightPercent),
      }))
      .filter(
        (holding) =>
          holding.ticker ||
          holding.name ||
          holding.sector ||
          holding.weightInput,
      );

    if (payloadHoldings.length === 0) {
      setRiskState("error");
      setRiskMessage("Enter at least one holding.");
      setRiskSummary(null);
      return;
    }

    if (
      payloadHoldings.some(
        (holding) =>
          !holding.ticker ||
          !holding.name ||
          !holding.weightInput ||
          !Number.isFinite(holding.weight_percent) ||
          holding.weight_percent <= 0,
      )
    ) {
      setRiskState("error");
      setRiskMessage("Each holding needs a ticker, name, and positive weight.");
      setRiskSummary(null);
      return;
    }

    setRiskState("summarizing");
    setRiskMessage("Generating portfolio risk summary...");
    setRiskSummary(null);

    const apiHoldings = payloadHoldings.map((holding) => ({
      ticker: holding.ticker,
      name: holding.name,
      sector: holding.sector,
      weight_percent: holding.weight_percent,
    }));

    try {
      const response = await fetch(`${apiBaseUrl}/portfolio/risk-summary`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          holdings: apiHoldings,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : `Risk summary failed with status ${response.status}`,
        );
      }

      setRiskSummary(data as PortfolioRiskSummary);
      setRiskState("summarized");
      setRiskMessage("Risk summary generated.");
    } catch (error) {
      setRiskState("error");
      setRiskMessage(
        error instanceof Error ? error.message : "Risk summary failed.",
      );
      setRiskSummary(null);
    }
  }

  return (
    <main className="page">
      <section className="hero" aria-labelledby="page-title">
        <p className="eyebrow">Research workflow starter</p>
        <h1 id="page-title">AI Financial Research Assistant</h1>
        <p className="lede">
          A focused workspace for financial research, document-backed answers,
          and source citations. Upload a text document, then ask questions
          against the retrieved context.
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

        <form className="upload-panel" onSubmit={uploadDocument}>
          <div>
            <h2>Upload Document</h2>
            <p className={`status status-${uploadState}`}>{uploadMessage}</p>
          </div>

          <label className="file-input">
            <span>Text document</span>
            <input
              type="file"
              accept=".txt,text/plain"
              onChange={(event) => {
                setSelectedFile(event.target.files?.[0] ?? null);
                setUploadState("idle");
                setUploadMessage("Ready to upload a .txt document.");
                setUploadedDocument(null);
                setDocumentId(null);
                setAskState("idle");
                setAskMessage("Upload a document, then ask a question.");
                setAskResponse(null);
              }}
            />
          </label>

          <button type="submit" disabled={uploadState === "uploading"}>
            {uploadState === "uploading" ? "Uploading..." : "Upload"}
          </button>

          {uploadedDocument ? (
            <dl className="metadata">
              <div>
                <dt>Document ID</dt>
                <dd>{documentId}</dd>
              </div>
              <div>
                <dt>Filename</dt>
                <dd>{uploadedDocument.filename}</dd>
              </div>
              <div>
                <dt>Characters</dt>
                <dd>{uploadedDocument.character_count}</dd>
              </div>
              <div>
                <dt>Chunks</dt>
                <dd>{uploadedDocument.chunk_count}</dd>
              </div>
              <div>
                <dt>Created</dt>
                <dd>{new Date(uploadedDocument.created_at).toLocaleString()}</dd>
              </div>
            </dl>
          ) : null}
        </form>

        <form className="ask-panel" onSubmit={askQuestion}>
          <div>
            <h2>Ask a Question</h2>
            <p className={`status status-${askState}`}>{askMessage}</p>
          </div>

          <label className="question-input">
            <span>Question</span>
            <textarea
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="What changed in revenue?"
              rows={4}
            />
          </label>

          <button
            type="submit"
            disabled={askState === "asking" || !documentId}
          >
            {askState === "asking" ? "Asking..." : "Ask"}
          </button>

          {askResponse ? (
            <section className="answer-panel" aria-live="polite">
              <div>
                <h2>Answer</h2>
                <p className="answer-text">{askResponse.answer}</p>
              </div>

              <div>
                <h2>Citations</h2>
                {askResponse.citations.length > 0 ? (
                  <ol className="citations">
                    {askResponse.citations.map((citation) => (
                      <li key={`${citation.document_id}-${citation.chunk_index}`}>
                        <span className="citation-title">
                          [{citation.source_id}] {citation.filename}
                        </span>
                        <span>
                          Chunk {citation.chunk_index}, characters{" "}
                          {citation.start_char}-{citation.end_char}
                        </span>
                        <span className="citation-document">
                          Document ID: {citation.document_id}
                        </span>
                      </li>
                    ))}
                  </ol>
                ) : (
                  <p className="empty-state">No citations returned.</p>
                )}
              </div>
            </section>
          ) : null}
        </form>

        <form className="portfolio-panel" onSubmit={summarizeRisk} autoComplete="off">
          <div>
            <h2>Portfolio Risk Summary</h2>
            <p className={`status status-${riskState}`}>{riskMessage}</p>
          </div>

          <div className="holdings-table">
            <div className="holdings-header" aria-hidden="true">
              <span>Ticker</span>
              <span>Name</span>
              <span>Sector</span>
              <span>Weight %</span>
              <span />
            </div>

            {holdings.map((holding) => (
              <div className="holding-row" key={holding.id}>
                <label>
                  <span>Ticker</span>
                  <input
                    value={holding.ticker}
                    onChange={(event) =>
                      updateHolding(holding.id, "ticker", event.target.value)
                    }
                    placeholder="Ticker"
                  />
                </label>
                <label>
                  <span>Name</span>
                  <input
                    value={holding.name}
                    onChange={(event) =>
                      updateHolding(holding.id, "name", event.target.value)
                    }
                    placeholder="Company or fund name"
                  />
                </label>
                <label>
                  <span>Sector</span>
                  <input
                    value={holding.sector}
                    onChange={(event) =>
                      updateHolding(holding.id, "sector", event.target.value)
                    }
                    placeholder="Optional sector"
                  />
                </label>
                <label>
                  <span>Weight %</span>
                  <input
                    inputMode="decimal"
                    value={holding.weightPercent}
                    onChange={(event) =>
                      updateHolding(
                        holding.id,
                        "weightPercent",
                        event.target.value,
                      )
                    }
                    placeholder="0"
                  />
                </label>
                <button
                  className="secondary-button"
                  type="button"
                  onClick={() => removeHolding(holding.id)}
                  disabled={holdings.length === 1}
                >
                  Remove
                </button>
              </div>
            ))}
          </div>

          <div className="form-actions">
            <button
              className="secondary-button"
              type="button"
              onClick={loadSamplePortfolio}
            >
              Load Sample Portfolio
            </button>
            <button className="secondary-button" type="button" onClick={addHolding}>
              Add Holding
            </button>
            <button type="submit" disabled={riskState === "summarizing"}>
              {riskState === "summarizing" ? "Summarizing..." : "Summarize Risk"}
            </button>
          </div>

          {riskSummary ? (
            <section className="risk-summary-card" aria-live="polite">
              <div>
                <h2>Risk Explanation</h2>
                <p>{riskSummary.risk_explanation}</p>
              </div>

              <div className="summary-grid">
                <div>
                  <h2>Concentration Risk</h2>
                  <ul>
                    {riskSummary.concentration_risk_notes.map((note) => (
                      <li key={note}>{note}</li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h2>Largest Positions</h2>
                  <ol>
                    {riskSummary.largest_positions.map((position) => (
                      <li key={position.ticker}>
                        {position.ticker} - {position.name}:{" "}
                        {position.weight_percent.toFixed(1)}%
                      </li>
                    ))}
                  </ol>
                </div>

                <div>
                  <h2>Sector Concentration</h2>
                  {riskSummary.sector_concentration_notes.length > 0 ? (
                    <ul>
                      {riskSummary.sector_concentration_notes.map((note) => (
                        <li key={note}>{note}</li>
                      ))}
                    </ul>
                  ) : (
                    <p>No complete sector concentration notes available.</p>
                  )}
                </div>

                <div>
                  <h2>Warnings</h2>
                  {riskSummary.missing_data_warnings.length > 0 ? (
                    <ul>
                      {riskSummary.missing_data_warnings.map((warning) => (
                        <li key={warning}>{warning}</li>
                      ))}
                    </ul>
                  ) : (
                    <p>No missing data warnings.</p>
                  )}
                </div>
              </div>

              <p className="disclaimer">{riskSummary.disclaimer}</p>
            </section>
          ) : null}
        </form>
      </section>
    </main>
  );
}

export default App;
