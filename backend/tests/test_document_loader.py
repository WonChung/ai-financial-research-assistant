import pytest

from app.rag.document_loader import DocumentValidationError, load_txt_document


def test_load_txt_document_decodes_utf8_text() -> None:
    document = load_txt_document(
        document_id="doc-1",
        filename="notes.txt",
        contents="Revenue grew 8%.".encode("utf-8"),
        created_at="2026-05-22T00:00:00+00:00",
    )

    assert document.document_id == "doc-1"
    assert document.filename == "notes.txt"
    assert document.text == "Revenue grew 8%."
    assert document.character_count == 16


def test_load_txt_document_rejects_non_txt_filename() -> None:
    with pytest.raises(DocumentValidationError, match="Only .txt files are supported."):
        load_txt_document(
            document_id="doc-1",
            filename="notes.pdf",
            contents=b"not a pdf",
            created_at="2026-05-22T00:00:00+00:00",
        )


def test_load_txt_document_rejects_invalid_utf8() -> None:
    with pytest.raises(
        DocumentValidationError,
        match="Uploaded .txt files must be UTF-8 encoded.",
    ):
        load_txt_document(
            document_id="doc-1",
            filename="notes.txt",
            contents=b"\xff",
            created_at="2026-05-22T00:00:00+00:00",
        )
