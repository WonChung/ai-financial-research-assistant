from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class LoadedDocument:
    document_id: str
    filename: str
    text: str
    created_at: str

    @property
    def character_count(self) -> int:
        return len(self.text)


@dataclass(frozen=True)
class DocumentChunk:
    document_id: str
    chunk_index: int
    text: str
    start_char: int
    end_char: int
    filename: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "DocumentChunk":
        return cls(
            document_id=str(data["document_id"]),
            chunk_index=int(data["chunk_index"]),
            text=str(data["text"]),
            start_char=int(data["start_char"]),
            end_char=int(data["end_char"]),
            filename=str(data["filename"]),
        )


@dataclass(frozen=True)
class EmbeddedChunk:
    chunk: DocumentChunk
    embedding: list[float]

    def to_dict(self) -> dict[str, object]:
        return {
            "chunk": self.chunk.to_dict(),
            "embedding": self.embedding,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "EmbeddedChunk":
        return cls(
            chunk=DocumentChunk.from_dict(data["chunk"]),  # type: ignore[arg-type]
            embedding=[float(value) for value in data["embedding"]],  # type: ignore[index]
        )


@dataclass(frozen=True)
class SearchResult:
    chunk: DocumentChunk
    score: float


@dataclass(frozen=True)
class SourceCitation:
    source_id: int
    document_id: str
    filename: str
    chunk_index: int
    start_char: int
    end_char: int


@dataclass(frozen=True)
class GeneratedAnswer:
    answer: str
    citations: list[SourceCitation]
