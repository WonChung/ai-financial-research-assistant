# Backend

FastAPI backend skeleton for the AI Financial Research Assistant.

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

Fill in `OPENAI_API_KEY` and `DATABASE_URL` when those integrations are implemented.

## Run Locally

```bash
uvicorn app.main:app --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok"}
```

Upload a UTF-8 `.txt` document:

```bash
curl -F "file=@example.txt" http://127.0.0.1:8000/documents/upload
```

Uploaded document text is stored locally under `backend/data/documents/`.
Chunk metadata is stored locally under `backend/data/chunks/`.
Local vector records are stored under `backend/data/vectors.json`.

Ask a question using retrieved context:

```bash
curl -X POST http://127.0.0.1:8000/research/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What changed in revenue?","top_k":3}'
```

## Test

```bash
pytest
```

The current RAG path uses local deterministic embeddings for development and
tests. OpenAI calls and portfolio-risk workflows are not implemented yet.
