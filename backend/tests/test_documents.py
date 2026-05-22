from pathlib import Path

from fastapi.testclient import TestClient

from app import main


def test_upload_txt_document_stores_file(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(main, "DOCUMENTS_DIR", tmp_path)
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

    stored_file = tmp_path / f"{data['document_id']}.txt"
    assert stored_file.read_text(encoding="utf-8") == "Revenue increased year over year."


def test_upload_rejects_non_txt_file(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(main, "DOCUMENTS_DIR", tmp_path)
    client = TestClient(main.app)

    response = client.post(
        "/documents/upload",
        files={"file": ("filing.pdf", b"%PDF-1.7", "application/pdf")},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Only .txt files are supported."}
    assert list(tmp_path.iterdir()) == []


def test_upload_rejects_invalid_utf8_txt(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(main, "DOCUMENTS_DIR", tmp_path)
    client = TestClient(main.app)

    response = client.post(
        "/documents/upload",
        files={"file": ("filing.txt", b"\xff\xfe\x00", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Uploaded .txt files must be UTF-8 encoded."}
    assert list(tmp_path.iterdir()) == []
