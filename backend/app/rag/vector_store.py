import json
import math
from pathlib import Path

from app.rag.models import DocumentChunk, EmbeddedChunk, SearchResult


class LocalVectorStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def upsert(self, embedded_chunks: list[EmbeddedChunk]) -> None:
        existing = self._load()
        by_key = {
            self._chunk_key(embedded_chunk.chunk): embedded_chunk
            for embedded_chunk in existing
        }

        for embedded_chunk in embedded_chunks:
            by_key[self._chunk_key(embedded_chunk.chunk)] = embedded_chunk

        self._save(list(by_key.values()))

    def search(
        self,
        query_embedding: list[float],
        *,
        document_id: str,
        top_k: int = 5,
    ) -> list[SearchResult]:
        if top_k <= 0:
            raise ValueError("top_k must be greater than 0.")

        results = [
            SearchResult(
                chunk=embedded_chunk.chunk,
                score=cosine_similarity(query_embedding, embedded_chunk.embedding),
            )
            for embedded_chunk in self._load()
            if embedded_chunk.chunk.document_id == document_id
        ]
        results.sort(key=lambda result: result.score, reverse=True)
        return deduplicate_results(results)[:top_k]

    def chunks_for_document(self, document_id: str) -> list[DocumentChunk]:
        return [
            embedded_chunk.chunk
            for embedded_chunk in self._load()
            if embedded_chunk.chunk.document_id == document_id
        ]

    def _load(self) -> list[EmbeddedChunk]:
        if not self.path.exists():
            return []

        data = json.loads(self.path.read_text(encoding="utf-8"))
        return [EmbeddedChunk.from_dict(item) for item in data]

    def _save(self, embedded_chunks: list[EmbeddedChunk]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = [embedded_chunk.to_dict() for embedded_chunk in embedded_chunks]
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @staticmethod
    def _chunk_key(chunk: DocumentChunk) -> tuple[str, int]:
        return (chunk.document_id, chunk.chunk_index)


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        raise ValueError("Embedding dimensions must match.")

    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0

    dot_product = sum(left_value * right_value for left_value, right_value in zip(left, right))
    return dot_product / (left_norm * right_norm)


def deduplicate_results(results: list[SearchResult]) -> list[SearchResult]:
    unique_results: list[SearchResult] = []
    seen_chunk_keys: set[tuple[str, int]] = set()
    seen_texts: set[str] = set()

    for result in results:
        chunk_key = (result.chunk.document_id, result.chunk.chunk_index)
        normalized_text = " ".join(result.chunk.text.split()).casefold()

        if chunk_key in seen_chunk_keys or normalized_text in seen_texts:
            continue

        seen_chunk_keys.add(chunk_key)
        seen_texts.add(normalized_text)
        unique_results.append(result)

    return unique_results
