import json
from pathlib import Path

from fastapi.testclient import TestClient

from app import main


def test_upload_txt_document_stores_file(tmp_path: Path, monkeypatch) -> None:
    documents_dir = tmp_path / "documents"
    chunks_dir = tmp_path / "chunks"
    monkeypatch.setattr(main, "DOCUMENTS_DIR", documents_dir)
    monkeypatch.setattr(main, "CHUNKS_DIR", chunks_dir)
    client = TestClient(main.app)

    response = client.post(
        "/documents/upload",
        files={"file": ("filing.txt", b"Revenue increased year over year.", "text/plain")},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "filing.txt"
    assert data["character_count"] == 33
    assert data["created_at"]
    assert data["chunk_count"] == 1

    stored_file = documents_dir / f"{data['document_id']}.txt"
    assert stored_file.read_text(encoding="utf-8") == "Revenue increased year over year."

    stored_chunks = json.loads(
        (chunks_dir / f"{data['document_id']}.json").read_text(encoding="utf-8")
    )
    assert stored_chunks == [
        {
            "document_id": data["document_id"],
            "chunk_index": 0,
            "text": "Revenue increased year over year.",
            "start_char": 0,
            "end_char": 33,
        }
    ]


def test_upload_rejects_non_txt_file(tmp_path: Path, monkeypatch) -> None:
    documents_dir = tmp_path / "documents"
    chunks_dir = tmp_path / "chunks"
    monkeypatch.setattr(main, "DOCUMENTS_DIR", documents_dir)
    monkeypatch.setattr(main, "CHUNKS_DIR", chunks_dir)
    client = TestClient(main.app)

    response = client.post(
        "/documents/upload",
        files={"file": ("filing.pdf", b"%PDF-1.7", "application/pdf")},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Only .txt files are supported."}
    assert not documents_dir.exists()
    assert not chunks_dir.exists()


def test_upload_rejects_invalid_utf8_txt(tmp_path: Path, monkeypatch) -> None:
    documents_dir = tmp_path / "documents"
    chunks_dir = tmp_path / "chunks"
    monkeypatch.setattr(main, "DOCUMENTS_DIR", documents_dir)
    monkeypatch.setattr(main, "CHUNKS_DIR", chunks_dir)
    client = TestClient(main.app)

    response = client.post(
        "/documents/upload",
        files={"file": ("filing.txt", b"\xff\xfe\x00", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Uploaded .txt files must be UTF-8 encoded."}
    assert not documents_dir.exists()
    assert not chunks_dir.exists()
