# RAG Evaluation Harness

The RAG evaluation harness validates source-grounded behavior for the local deterministic RAG prototype. It is designed around golden-question cases, retrieval validation, answer phrase checks, citation coverage, latency measurement, pass/fail metrics, and structured reports.

This aligns with the kind of evaluation workflow expected in an NVIDIA NeMo Evaluator role story, but the current project does not call NVIDIA NeMo services, OpenAI APIs, or any external LLM.

## Evaluation Case Schema

Each evaluation case is scoped to the currently uploaded document through the top-level `document_id` in the API request.

```json
{
  "question": "Why did revenue increase?",
  "expected_answer_phrases": ["online sales", "store traffic"],
  "expected_citation_phrases": ["Management attributed the increase"]
}
```

Fields:

- `question`: The golden question to ask through the existing RAG pipeline.
- `expected_answer_phrases`: Phrases that should appear in the generated answer. Defaults to an empty list in the API.
- `expected_citation_phrases`: Phrases that should appear in retrieved cited context. Defaults to an empty list in the API.

The phrase checks are deterministic, case-insensitive, and whitespace-normalized. They are intentionally simple so tests remain stable.

## API Example

```json
{
  "document_id": "uuid-from-upload",
  "top_k": 5,
  "cases": [
    {
      "question": "Why did revenue increase?",
      "expected_answer_phrases": ["online sales", "store traffic"],
      "expected_citation_phrases": ["Management attributed the increase"]
    },
    {
      "question": "What risks did management identify?",
      "expected_answer_phrases": ["consumer spending pressure"],
      "expected_citation_phrases": ["Key risks include"]
    }
  ]
}
```

The backend caps requests at 20 cases.

## Checks and Metrics

For each case, the evaluator:

- Calls the existing `RagService.answer()` path.
- Measures `latency_ms` with Python `time.perf_counter()`.
- Counts returned citations as citation coverage.
- Checks whether expected answer phrases appear in the answer.
- Checks whether expected citation phrases appear in retrieved cited context.
- Checks whether citation markers such as `[1]` appear in the answer for returned citations.
- Emits pass/fail checks with failure details.

The response includes aggregate metrics:

- `total_cases`
- `passed_cases`
- `failed_cases`
- `pass_rate`
- per-case results with answer, citations, latency, citation count, and checks

## Example Response

```json
{
  "document_id": "uuid-from-upload",
  "total_cases": 1,
  "passed_cases": 1,
  "failed_cases": 0,
  "pass_rate": 1.0,
  "results": [
    {
      "question": "Why did revenue increase?",
      "answer": "Northstar Retail Group reported revenue... [1]",
      "passed": true,
      "latency_ms": 2.4,
      "citation_count": 1,
      "checks": [
        {
          "name": "retrieval_has_citations",
          "passed": true,
          "detail": null
        },
        {
          "name": "expected_answer_phrases",
          "passed": true,
          "detail": null
        },
        {
          "name": "expected_citation_phrases",
          "passed": true,
          "detail": null
        },
        {
          "name": "answer_citation_markers",
          "passed": true,
          "detail": null
        }
      ],
      "citations": [
        {
          "source_id": 1,
          "document_id": "uuid-from-upload",
          "filename": "example-financial-summary.txt",
          "chunk_index": 0,
          "start_char": 0,
          "end_char": 1000
        }
      ]
    }
  ]
}
```

## What It Measures

The harness measures repeatable local behavior:

- Whether retrieval returns at least one cited source.
- Whether expected answer phrases are present.
- Whether expected cited-context phrases are present.
- Whether answer citation markers match returned citations.
- How many citations were returned.
- How long each evaluated RAG answer took.

This is useful for regression tests after changing chunking, retrieval, answer generation, or citation formatting.

## What It Does Not Measure

The harness does not measure:

- Semantic answer quality beyond exact phrase checks.
- Faithfulness using an LLM judge.
- Recall against a large labeled benchmark.
- Production traffic quality.
- User satisfaction.
- Drift over time.
- Security or policy compliance.

## Limitations

- The current RAG implementation is deterministic and local.
- Embeddings are hash-based and are not production semantic embeddings.
- Answer generation is not LLM-based.
- There is no LLM judge.
- There is no production monitoring.
- There is no authentication or authorization.
- Uploaded documents and vector data are stored locally for development.
