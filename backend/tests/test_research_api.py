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
        json={"question": "Why did revenue increase?", "top_k": 1},
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
        json={"question": "What changed?", "top_k": 0},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "top_k must be greater than 0."}
