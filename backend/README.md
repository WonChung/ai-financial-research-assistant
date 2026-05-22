# Backend

FastAPI backend for the AI Financial Research Assistant. It supports document upload, RAG-style document Q&A, source citations, and portfolio risk summary generation.

## Local Setup

Create and activate a virtual environment:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create local configuration:

```bash
cp .env.example .env
```

The current `.env.example` includes placeholders for future integrations:

```bash
OPENAI_API_KEY=
DATABASE_URL=
```

The current backend runs without OpenAI API calls.

## Run Locally

```bash
.venv/bin/uvicorn app.main:app --reload
```

The backend runs at:

```text
http://127.0.0.1:8000
```

## API Endpoints

### `GET /health`

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok"}
```

### `POST /documents/upload`

Uploads a UTF-8 `.txt` document:

```bash
curl -F "file=@../samples/example-financial-summary.txt" \
  http://127.0.0.1:8000/documents/upload
```

Uploaded document text is stored under `backend/data/documents/`.
Chunk metadata is stored under `backend/data/chunks/`.
Local vector records are stored in `backend/data/vectors.json`.

### `POST /research/ask`

Asks a question using retrieved context from one selected document.

The request requires:

- `document_id`
- `question`
- `top_k`

Example:

```bash
curl -X POST http://127.0.0.1:8000/research/ask \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "uuid-from-upload",
    "question": "What changed in revenue?",
    "top_k": 3
  }'
```

The response includes an answer and citations with source IDs, filename, chunk index, and character offsets.

### `POST /portfolio/risk-summary`

Generates a rule-based portfolio risk summary from manually supplied holdings.

Example:

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

The response includes concentration risk notes, largest positions, sector notes, missing-data warnings, a plain-English explanation, and a research/education disclaimer.

## RAG Status

The current RAG path uses deterministic local hash embeddings for development and tests. It does not call an LLM yet.

## Test

```bash
.venv/bin/pytest
```
