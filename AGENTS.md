# Project Instructions

This is an AI financial research assistant.

Stack:
- Backend: Python FastAPI
- Frontend: React + TypeScript
- RAG: local deterministic pipeline with document ingestion, hash-based embeddings, document-scoped retrieval, and source-cited answer generation
- Database: start simple with local storage or SQLite; later move to Postgres/pgvector
- Future upgrade: OpenAI API or another LLM/embedding provider may be added later, but the current app does not call OpenAI APIs or an LLM.

Rules:
- Make small, reviewable changes.
- Do not add large dependencies without explaining why.
- Do not hardcode API keys.
- Keep .env files out of git.
- Add tests for backend logic.
- After changes, explain what changed and what command to run next.
