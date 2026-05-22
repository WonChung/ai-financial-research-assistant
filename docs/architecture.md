# Architecture

This project is a full-stack financial research assistant with a React frontend, a FastAPI backend, a local RAG pipeline, and a rule-based portfolio risk summary feature.

## React Frontend

The frontend is built with React, TypeScript, and Vite. It provides the user-facing workflows:

- Check backend health.
- Upload a `.txt` research document.
- Ask questions against the uploaded document.
- Display source-cited answers.
- Enter portfolio holdings manually or load a sample portfolio.
- Display portfolio concentration and sector-risk summaries.

The frontend stores the latest uploaded `document_id` in component state. Every RAG question sends that `document_id` to the backend so answers are scoped to the selected document.

## FastAPI Backend

The backend is a Python FastAPI app. It exposes:

- `GET /health`
- `POST /documents/upload`
- `POST /research/ask`
- `POST /portfolio/risk-summary`

Pydantic models define request and response shapes. Development data is stored locally under `backend/data/`.

## Document Upload

`POST /documents/upload` accepts UTF-8 `.txt` files. On upload, the backend:

1. Validates the file extension.
2. Decodes the uploaded bytes as UTF-8.
3. Generates a `document_id`.
4. Stores the raw text in `backend/data/documents/`.
5. Passes the document into the chunking and indexing flow.

PDF, spreadsheet, and HTML ingestion are not implemented.

## Chunking

Uploaded text is split into fixed-size overlapping chunks. Each chunk stores:

- `document_id`
- `chunk_index`
- text
- `start_char`
- `end_char`
- source filename

The character offsets make it possible to cite where retrieved context came from in the original document.

## Retrieval

The current RAG implementation uses deterministic local hash embeddings. This is intentionally simple and test-friendly.

For each question, the backend:

1. Embeds the query.
2. Searches the local JSON vector store.
3. Filters candidate chunks by the requested `document_id`.
4. Deduplicates results by `(document_id, chunk_index)` and normalized text.
5. Returns the top relevant unique chunks.

Document-scoped retrieval prevents repeated uploads of the same file from producing duplicated answers across different document IDs.

## Answer Generation

The answer generator builds a concise answer from retrieved context and appends citation markers such as `[1]`.

This prototype does not call an LLM for answer generation yet. The current approach keeps local development deterministic and covered by tests.

## Source Citations

Each answer includes citations with:

- source ID
- document ID
- filename
- chunk index
- start character
- end character

Citations are limited to the selected document. This keeps answers traceable and avoids mixing sources from prior uploads.

## Portfolio Risk Summary

`POST /portfolio/risk-summary` accepts manually entered holdings with:

- ticker
- name
- optional sector
- weight percent

The backend returns:

- concentration risk notes
- largest positions
- sector concentration notes when sector data is available
- missing data warnings
- plain-English risk explanation
- research/education disclaimer

This feature is rule-based. It does not use brokerage connections, live prices, or buy/sell recommendations.

## High-Level Data Flow

```text
React UI
  -> FastAPI document upload
  -> text validation
  -> chunking
  -> deterministic local embeddings
  -> JSON vector store
  -> document-scoped retrieval
  -> source-cited answer
  -> React UI
```

Portfolio risk summary flow:

```text
React holdings form
  -> FastAPI portfolio endpoint
  -> input validation
  -> rule-based concentration and sector analysis
  -> summary response
  -> React UI
```
