from pathlib import Path

from app.rag.evaluation import EvaluationCase, RagEvaluator
from app.rag.pipeline import build_local_ingestion_service, build_local_rag_service


def test_evaluator_passes_golden_question_case(tmp_path: Path) -> None:
    vector_store_path = tmp_path / "vectors.json"
    ingestion_service = build_local_ingestion_service(
        documents_dir=tmp_path / "documents",
        chunks_dir=tmp_path / "chunks",
        vector_store_path=vector_store_path,
    )
    ingestion_service.ingest_txt(
        document_id="doc-1",
        filename="earnings.txt",
        contents=(
            b"Revenue increased because cloud services grew. "
            b"Operating margin declined due to higher data center costs."
        ),
        created_at="2026-05-22T00:00:00+00:00",
    )

    evaluator = RagEvaluator(build_local_rag_service(vector_store_path))
    result = evaluator.evaluate_case(
        EvaluationCase(
            case_id="revenue-growth",
            document_id="doc-1",
            question="Why did revenue increase?",
            expected_answer_phrases=["cloud services grew"],
            expected_citation_phrases=["Revenue increased"],
            top_k=1,
        )
    )

    assert result.passed is True
    assert result.cited_source_count == 1
    assert result.latency_ms >= 0
    assert [check.passed for check in result.checks] == [True, True, True, True]
    assert result.to_dict()["passed"] is True


def test_evaluator_returns_clear_failure_reasons(tmp_path: Path) -> None:
    vector_store_path = tmp_path / "vectors.json"
    ingestion_service = build_local_ingestion_service(
        documents_dir=tmp_path / "documents",
        chunks_dir=tmp_path / "chunks",
        vector_store_path=vector_store_path,
    )
    ingestion_service.ingest_txt(
        document_id="doc-1",
        filename="earnings.txt",
        contents=b"Revenue increased because cloud services grew.",
        created_at="2026-05-22T00:00:00+00:00",
    )

    evaluator = RagEvaluator(build_local_rag_service(vector_store_path))
    result = evaluator.evaluate_case(
        EvaluationCase(
            document_id="doc-1",
            question="Why did revenue increase?",
            expected_answer_phrases=["subscription revenue doubled"],
            expected_citation_phrases=["enterprise backlog expanded"],
            top_k=1,
        )
    )

    failures = {
        check.name: check.failure_reason
        for check in result.checks
        if not check.passed
    }

    assert result.passed is False
    assert failures == {
        "expected_answer_phrases": (
            "Missing expected answer phrase(s): 'subscription revenue doubled'"
        ),
        "expected_citation_phrases": (
            "Missing expected cited context phrase(s): "
            "'enterprise backlog expanded'"
        ),
    }


def test_evaluator_fails_retrieval_when_no_sources_are_cited(
    tmp_path: Path,
) -> None:
    vector_store_path = tmp_path / "vectors.json"
    evaluator = RagEvaluator(build_local_rag_service(vector_store_path))

    result = evaluator.evaluate_case(
        EvaluationCase(
            document_id="missing-doc",
            question="What happened to revenue?",
            expected_answer_phrases=[],
            expected_citation_phrases=[],
        )
    )

    failures = {
        check.name: check.failure_reason
        for check in result.checks
        if not check.passed
    }

    assert result.passed is False
    assert result.cited_source_count == 0
    assert failures == {
        "retrieval_has_citations": (
            "Expected at least one cited source, but none were returned."
        )
    }


def test_evaluator_summary_reports_pass_fail_metrics(tmp_path: Path) -> None:
    vector_store_path = tmp_path / "vectors.json"
    ingestion_service = build_local_ingestion_service(
        documents_dir=tmp_path / "documents",
        chunks_dir=tmp_path / "chunks",
        vector_store_path=vector_store_path,
    )
    ingestion_service.ingest_txt(
        document_id="doc-1",
        filename="earnings.txt",
        contents=b"Revenue increased because cloud services grew.",
        created_at="2026-05-22T00:00:00+00:00",
    )

    evaluator = RagEvaluator(build_local_rag_service(vector_store_path))
    summary = evaluator.evaluate(
        [
            EvaluationCase(
                document_id="doc-1",
                question="Why did revenue increase?",
                expected_answer_phrases=["cloud services grew"],
                expected_citation_phrases=["Revenue increased"],
                top_k=1,
            ),
            EvaluationCase(
                document_id="doc-1",
                question="Why did revenue increase?",
                expected_answer_phrases=["margin expanded"],
                expected_citation_phrases=[],
                top_k=1,
            ),
        ]
    )
    report = summary.to_dict()

    assert summary.total_cases == 2
    assert summary.passed_cases == 1
    assert summary.failed_cases == 1
    assert summary.pass_rate == 0.5
    assert summary.average_latency_ms >= 0
    assert report["total_cases"] == 2
    assert len(report["results"]) == 2


def test_empty_evaluation_summary_has_zero_metrics(tmp_path: Path) -> None:
    evaluator = RagEvaluator(build_local_rag_service(tmp_path / "vectors.json"))

    summary = evaluator.evaluate([])

    assert summary.total_cases == 0
    assert summary.passed_cases == 0
    assert summary.failed_cases == 0
    assert summary.pass_rate == 0.0
    assert summary.average_latency_ms == 0.0
