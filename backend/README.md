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

## Test

```bash
pytest
```

Embeddings, OpenAI calls, RAG, retrieval, and portfolio-risk workflows are not
implemented yet.
