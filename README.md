# AI Financial Research Assistant

A full-stack financial research assistant built with React, TypeScript, and FastAPI. It supports document upload, document-scoped RAG question answering with citations, and portfolio concentration-risk summaries from manually entered holdings.

## Why I Built It

Financial research workflows often require jumping between filings, notes, portfolio spreadsheets, and ad hoc summaries. I built this project to show how a practical AI research tool can combine document-grounded answers, source citations, and simple portfolio risk analysis in one clean interface.

The goal is a portfolio-ready full-stack app: useful product behavior, clear architecture, local development ergonomics, and backend test coverage.

## Key Features

- Upload UTF-8 `.txt` research documents.
- Chunk documents and store source metadata locally.
- Ask questions against the currently uploaded document.
- Return concise answers with source citations and character ranges.
- Scope retrieval by `document_id` to avoid duplicate answers from repeated uploads.
- Enter holdings manually or load a sample portfolio.
- Generate concentration-risk notes, largest positions, sector-risk notes, and missing-data warnings.
- Include a clear research/education disclaimer.

## Screenshots

### Full Workflow

![Full app workflow](docs/screenshots/app-full-workflow.png)

### RAG Answer With Citations

![RAG answer with citations](docs/screenshots/rag-answer-citations.png)

### Portfolio Risk Summary

![Portfolio risk summary](docs/screenshots/portfolio-risk-summary.png)

## Tech Stack

- Frontend: React, TypeScript, Vite
- Backend: Python, FastAPI, Pydantic
- Testing: pytest
- RAG prototype: local chunking, deterministic hash embeddings, JSON vector store
- Storage: local files under `backend/data/`

## Architecture Overview

```text
React UI
  -> FastAPI API
  -> document validation and storage
  -> text chunking
  -> local deterministic embeddings
  -> JSON vector store
  -> document-scoped retrieval
  -> source-cited answer
```

Portfolio risk summary is a separate rule-based flow:

```text
React holdings form
  -> FastAPI portfolio endpoint
  -> input validation
  -> concentration and sector analysis
  -> risk summary response
```

More detail: [docs/architecture.md](docs/architecture.md)

## Local Setup

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
.venv/bin/uvicorn app.main:app --reload
```

Backend runs at:

```text
http://127.0.0.1:8000
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Frontend runs at the Vite URL shown in the terminal. Locally, use:

```text
http://localhost:5173
```

## Environment Variables

Backend `.env`:

```bash
OPENAI_API_KEY=
DATABASE_URL=
```

Frontend `.env`:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Do not commit `.env` files or real API keys. See [docs/security.md](docs/security.md).

## API Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Backend health check |
| `POST` | `/documents/upload` | Upload a UTF-8 `.txt` document |
| `POST` | `/research/ask` | Ask a document-scoped RAG question |
| `POST` | `/portfolio/risk-summary` | Generate a portfolio risk summary |

Example RAG request:

```bash
curl -X POST http://127.0.0.1:8000/research/ask \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "uuid-from-upload",
    "question": "What changed in revenue?",
    "top_k": 3
  }'
```

Example portfolio request:

```bash
curl -X POST http://127.0.0.1:8000/portfolio/risk-summary \
  -H "Content-Type: application/json" \
  -d '{
    "holdings": [
      {"ticker": "AAPL", "name": "Apple", "sector": "Technology", "weight_percent": 20},
      {"ticker": "JPM", "name": "JPMorgan Chase", "sector": "Financials", "weight_percent": 15},
      {"ticker": "JNJ", "name": "Johnson & Johnson", "sector": "Healthcare", "weight_percent": 15},
      {"ticker": "XOM", "name": "Exxon Mobil", "sector": "Energy", "weight_percent": 10},
      {"ticker": "VTI", "name": "Vanguard Total Stock Market ETF", "sector": "Broad Market", "weight_percent": 40}
    ]
  }'
```

## Example Workflow

1. Start the backend and frontend.
2. Open `http://localhost:5173`.
3. Check backend health.
4. Upload a `.txt` document.
5. Ask a question about the uploaded document.
6. Review the answer and citations.
7. Load the sample portfolio or enter holdings manually.
8. Generate the portfolio risk summary.

## Testing Commands

Backend tests:

```bash
cd backend
.venv/bin/pytest
```

Frontend build:

```bash
cd frontend
npm run build
```

## Limitations

- RAG uses deterministic local hash embeddings, not production semantic embeddings.
- Document ingestion currently supports UTF-8 `.txt` files only.
- The JSON vector store is intended for local development, not concurrent production use.
- Answer generation is intentionally simple and does not call an LLM yet.
- Portfolio risk summary is rule-based and only uses user-entered holdings.
- The app does not connect to brokerage accounts, live market data, or real account data.
- Authentication, authorization, deployment hardening, and encrypted document storage are not included.

## Financial Disclaimer

This project is for research and education only. It is not financial advice and should not be used as the sole basis for investment, trading, tax, legal, or financial planning decisions.

## Resume Bullet

Built a full-stack AI financial research assistant with React, TypeScript, FastAPI, and a local RAG pipeline, featuring document ingestion, document-scoped retrieval, source-cited Q&A, portfolio concentration-risk summaries, and backend test coverage.
