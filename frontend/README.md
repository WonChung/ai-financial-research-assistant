# Frontend

React + TypeScript + Vite frontend for the AI Financial Research Assistant.

## Current Workflows

- Backend health check.
- `.txt` document upload.
- Document-scoped Q&A against the latest uploaded document.
- Source citation display for RAG answers.
- RAG evaluation harness with editable JSON cases.
- Evaluation pass/fail metrics, check details, latency, answers, and citations.
- Manual portfolio holdings entry.
- Portfolio risk summary display.

## Local Setup

Install dependencies:

```bash
cd frontend
npm install
```

Create local configuration:

```bash
cp .env.example .env
```

Start the backend from a separate terminal:

```bash
cd ..
cd backend
.venv/bin/uvicorn app.main:app --reload
```

Start the frontend:

```bash
cd frontend
npm run dev
```

The frontend runs at the URL printed by Vite, usually `http://localhost:5173`.

## Usage Flow

1. Click `Check Health`.
2. Upload a UTF-8 `.txt` document, such as `samples/example-financial-summary.txt`.
3. Ask a question about the uploaded document.
4. Review the answer and citations.
5. Load sample evaluation cases or enter custom JSON cases.
6. Click `Run Evaluation`.
7. Review pass/fail metrics, check details, latency, answers, and citations.
8. Enter portfolio holdings manually or click `Load Sample Portfolio`.
9. Click `Summarize Risk`.
10. Review concentration notes, sector notes, warnings, and disclaimer.

## Checks

```bash
npm run lint
npm run build
```
