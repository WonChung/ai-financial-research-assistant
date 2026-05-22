import { type FormEvent, useState } from "react";

type HealthState = "idle" | "checking" | "healthy" | "error";
type UploadState = "idle" | "uploading" | "uploaded" | "error";

type UploadedDocument = {
  document_id: string;
  filename: string;
  character_count: number;
  created_at: string;
};

const apiBaseUrl =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") ??
  "http://127.0.0.1:8000";

function App() {
  const [healthState, setHealthState] = useState<HealthState>("idle");
  const [message, setMessage] = useState("Backend health has not been checked.");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadState, setUploadState] = useState<UploadState>("idle");
  const [uploadMessage, setUploadMessage] = useState("No document uploaded yet.");
  const [uploadedDocument, setUploadedDocument] =
    useState<UploadedDocument | null>(null);

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

      setUploadedDocument(data as UploadedDocument);
      setUploadState("uploaded");
      setUploadMessage("Document uploaded.");
    } catch (error) {
      setUploadedDocument(null);
      setUploadState("error");
      setUploadMessage(error instanceof Error ? error.message : "Upload failed.");
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
                <dd>{uploadedDocument.document_id}</dd>
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
                <dt>Created</dt>
                <dd>{new Date(uploadedDocument.created_at).toLocaleString()}</dd>
              </div>
            </dl>
          ) : null}
        </form>
      </section>
    </main>
  );
}

export default App;
