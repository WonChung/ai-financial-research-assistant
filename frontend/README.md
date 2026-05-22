# Frontend

React + TypeScript + Vite frontend for the AI Financial Research Assistant.

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
cd backend
.venv/bin/uvicorn app.main:app --reload
```

Start the frontend:

```bash
cd frontend
npm run dev
```

Open the Vite URL shown in your terminal, usually `http://127.0.0.1:5173`.

The frontend includes a backend health check and a `.txt` document upload form.
Upload and metadata display are available, but AI/RAG workflows are not
implemented yet.

## Checks

```bash
npm run lint
npm run build
```
