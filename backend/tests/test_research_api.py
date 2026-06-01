from pathlib import Path

from fastapi.testclient import TestClient

from app import main


def test_ask_question_returns_source_citations(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(main, "DOCUMENTS_DIR", tmp_path / "documents")
    monkeypatch.setattr(main, "CHUNKS_DIR", tmp_path / "chunks")
    monkeypatch.setattr(main, "VECTOR_STORE_PATH", tmp_path / "vectors.json")
    client = TestClient(main.app)

    upload_response = client.post(
        "/documents/upload",
        files={
            "file": (
                "filing.txt",
                b"Revenue increased because services grew.",
                "text/plain",
            )
        },
    )
    assert upload_response.status_code == 200

    response = client.post(
        "/research/ask",
        json={
            "document_id": upload_response.json()["document_id"],
            "question": "Why did revenue increase?",
            "top_k": 1,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "Revenue increased because services grew." in data["answer"]
    assert data["citations"] == [
        {
            "source_id": 1,
            "document_id": upload_response.json()["document_id"],
            "filename": "filing.txt",
            "chunk_index": 0,
            "start_char": 0,
            "end_char": 40,
        }
    ]


def test_ask_question_rejects_invalid_top_k() -> None:
    client = TestClient(main.app)

    response = client.post(
        "/research/ask",
        json={"document_id": "doc-1", "question": "What changed?", "top_k": 0},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "top_k must be greater than 0."}


def test_ask_question_is_scoped_to_selected_document(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(main, "DOCUMENTS_DIR", tmp_path / "documents")
    monkeypatch.setattr(main, "CHUNKS_DIR", tmp_path / "chunks")
    monkeypatch.setattr(main, "VECTOR_STORE_PATH", tmp_path / "vectors.json")
    client = TestClient(main.app)

    first_upload = client.post(
        "/documents/upload",
        files={
            "file": (
                "example.txt",
                b"Revenue increased because services grew.",
                "text/plain",
            )
        },
    )
    second_upload = client.post(
        "/documents/upload",
        files={
            "file": (
                "example.txt",
                b"Revenue increased because services grew.",
                "text/plain",
            )
        },
    )
    assert first_upload.status_code == 200
    assert second_upload.status_code == 200
    selected_document_id = second_upload.json()["document_id"]

    response = client.post(
        "/research/ask",
        json={
            "document_id": selected_document_id,
            "question": "Why did revenue increase?",
            "top_k": 5,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["answer"].count("Revenue increased because services grew.") == 1
    assert data["citations"] == [
        {
            "source_id": 1,
            "document_id": selected_document_id,
            "filename": "example.txt",
            "chunk_index": 0,
            "start_char": 0,
            "end_char": 40,
        }
    ]


def test_ask_question_requires_document_id() -> None:
    client = TestClient(main.app)

    response = client.post(
        "/research/ask",
        json={"question": "What changed?"},
    )

    assert response.status_code == 422


def test_evaluate_research_returns_passing_golden_question(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(main, "DOCUMENTS_DIR", tmp_path / "documents")
    monkeypatch.setattr(main, "CHUNKS_DIR", tmp_path / "chunks")
    monkeypatch.setattr(main, "VECTOR_STORE_PATH", tmp_path / "vectors.json")
    client = TestClient(main.app)

    upload_response = client.post(
        "/documents/upload",
        files={
            "file": (
                "filing.txt",
                b"Revenue increased because services grew.",
                "text/plain",
            )
        },
    )
    assert upload_response.status_code == 200

    response = client.post(
        "/research/evaluate",
        json={
            "document_id": upload_response.json()["document_id"],
            "top_k": 1,
            "cases": [
                {
                    "question": "Why did revenue increase?",
                    "expected_answer_phrases": ["services grew"],
                    "expected_citation_phrases": [
                        "Revenue increased because services grew"
                    ],
                }
            ],
        },
    )

    assert response.status_code == 200
    data = response.json()
    result = data["results"][0]
    assert data["document_id"] == upload_response.json()["document_id"]
    assert data["total_cases"] == 1
    assert data["passed_cases"] == 1
    assert data["failed_cases"] == 0
    assert data["pass_rate"] == 1.0
    assert result["question"] == "Why did revenue increase?"
    assert result["passed"] is True
    assert result["citation_count"] == 1
    assert result["latency_ms"] >= 0
    assert all(check["passed"] for check in result["checks"])
    assert result["citations"] == [
        {
            "source_id": 1,
            "document_id": upload_response.json()["document_id"],
            "filename": "filing.txt",
            "chunk_index": 0,
            "start_char": 0,
            "end_char": 40,
        }
    ]


def test_evaluate_research_returns_failed_check_for_missing_phrase(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(main, "DOCUMENTS_DIR", tmp_path / "documents")
    monkeypatch.setattr(main, "CHUNKS_DIR", tmp_path / "chunks")
    monkeypatch.setattr(main, "VECTOR_STORE_PATH", tmp_path / "vectors.json")
    client = TestClient(main.app)

    upload_response = client.post(
        "/documents/upload",
        files={
            "file": (
                "filing.txt",
                b"Revenue increased because services grew.",
                "text/plain",
            )
        },
    )
    assert upload_response.status_code == 200

    response = client.post(
        "/research/evaluate",
        json={
            "document_id": upload_response.json()["document_id"],
            "top_k": 1,
            "cases": [
                {
                    "question": "Why did revenue increase?",
                    "expected_answer_phrases": ["hardware sales doubled"],
                    "expected_citation_phrases": [],
                }
            ],
        },
    )

    assert response.status_code == 200
    data = response.json()
    failed_checks = [
        check for check in data["results"][0]["checks"] if not check["passed"]
    ]
    assert data["pass_rate"] == 0.0
    assert failed_checks == [
        {
            "name": "expected_answer_phrases",
            "passed": False,
            "detail": "Missing expected answer phrase(s): 'hardware sales doubled'",
        }
    ]


def test_evaluate_research_rejects_invalid_top_k() -> None:
    client = TestClient(main.app)

    response = client.post(
        "/research/evaluate",
        json={
            "document_id": "doc-1",
            "top_k": 0,
            "cases": [
                {
                    "question": "What changed?",
                }
            ],
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "top_k must be greater than 0."}


def test_evaluate_research_rejects_empty_cases() -> None:
    client = TestClient(main.app)

    response = client.post(
        "/research/evaluate",
        json={
            "document_id": "doc-1",
            "top_k": 1,
            "cases": [],
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "At least one case is required."}
