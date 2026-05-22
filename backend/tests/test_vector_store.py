from pathlib import Path

import pytest

from app.rag.embeddings import HashingEmbeddingProvider
from app.rag.models import DocumentChunk, EmbeddedChunk
from app.rag.vector_store import LocalVectorStore, cosine_similarity


def test_hashing_embedding_provider_returns_normalized_vectors() -> None:
    provider = HashingEmbeddingProvider(dimensions=16)

    embedding = provider.embed_query("revenue growth revenue")

    assert len(embedding) == 16
    assert cosine_similarity(embedding, embedding) == pytest.approx(1.0)


def test_local_vector_store_searches_by_similarity(tmp_path: Path) -> None:
    provider = HashingEmbeddingProvider(dimensions=64)
    store = LocalVectorStore(tmp_path / "vectors.json")
    chunks = [
        DocumentChunk(
            document_id="doc-1",
            chunk_index=0,
            text="Revenue increased because services grew.",
            start_char=0,
            end_char=41,
            filename="filing.txt",
        ),
        DocumentChunk(
            document_id="doc-1",
            chunk_index=1,
            text="Supply chain costs pressured gross margin.",
            start_char=42,
            end_char=83,
            filename="filing.txt",
        ),
    ]
    embeddings = provider.embed_documents([chunk.text for chunk in chunks])

    store.upsert(
        [
            EmbeddedChunk(chunk=chunk, embedding=embedding)
            for chunk, embedding in zip(chunks, embeddings)
        ]
    )

    results = store.search(
        provider.embed_query("services revenue"),
        document_id="doc-1",
        top_k=1,
    )

    assert len(results) == 1
    assert results[0].chunk.chunk_index == 0
    assert results[0].score > 0


def test_cosine_similarity_rejects_dimension_mismatch() -> None:
    with pytest.raises(ValueError, match="Embedding dimensions must match."):
        cosine_similarity([1.0], [1.0, 0.0])


def test_local_vector_store_filters_by_document_id(tmp_path: Path) -> None:
    provider = HashingEmbeddingProvider(dimensions=64)
    store = LocalVectorStore(tmp_path / "vectors.json")
    chunks = [
        DocumentChunk(
            document_id="doc-1",
            chunk_index=0,
            text="Revenue increased because services grew.",
            start_char=0,
            end_char=40,
            filename="example.txt",
        ),
        DocumentChunk(
            document_id="doc-2",
            chunk_index=0,
            text="Revenue increased because services grew.",
            start_char=0,
            end_char=40,
            filename="example.txt",
        ),
    ]
    embeddings = provider.embed_documents([chunk.text for chunk in chunks])
    store.upsert(
        [
            EmbeddedChunk(chunk=chunk, embedding=embedding)
            for chunk, embedding in zip(chunks, embeddings)
        ]
    )

    results = store.search(
        provider.embed_query("services revenue"),
        document_id="doc-2",
        top_k=5,
    )

    assert len(results) == 1
    assert results[0].chunk.document_id == "doc-2"
