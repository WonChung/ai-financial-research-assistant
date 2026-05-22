import json
from pathlib import Path

from app.rag.pipeline import (
    build_local_ingestion_service,
    build_local_rag_service,
)


def test_ingestion_indexes_chunks_for_retrieval(tmp_path: Path) -> None:
    vector_store_path = tmp_path / "vectors.json"
    ingestion_service = build_local_ingestion_service(
        documents_dir=tmp_path / "documents",
        chunks_dir=tmp_path / "chunks",
        vector_store_path=vector_store_path,
    )
    document, chunk_count = ingestion_service.ingest_txt(
        document_id="doc-1",
        filename="filing.txt",
        contents=b"Revenue increased from services. Margins declined from costs.",
        created_at="2026-05-22T00:00:00+00:00",
    )

    assert document.character_count == 61
    assert chunk_count == 1
    assert (tmp_path / "documents" / "doc-1.txt").exists()
    chunk_data = json.loads((tmp_path / "chunks" / "doc-1.json").read_text())
    assert chunk_data[0]["document_id"] == "doc-1"
    assert chunk_data[0]["filename"] == "filing.txt"
    assert vector_store_path.exists()


def test_rag_service_generates_answer_with_citations(tmp_path: Path) -> None:
    vector_store_path = tmp_path / "vectors.json"
    ingestion_service = build_local_ingestion_service(
        documents_dir=tmp_path / "documents",
        chunks_dir=tmp_path / "chunks",
        vector_store_path=vector_store_path,
    )
    ingestion_service.ingest_txt(
        document_id="doc-1",
        filename="filing.txt",
        contents=b"Services revenue increased. Hardware demand softened.",
        created_at="2026-05-22T00:00:00+00:00",
    )

    rag_service = build_local_rag_service(vector_store_path)
    generated_answer = rag_service.answer("What happened to services revenue?", top_k=1)

    assert "Services revenue increased." in generated_answer.answer
    assert len(generated_answer.citations) == 1
    assert generated_answer.citations[0].filename == "filing.txt"
