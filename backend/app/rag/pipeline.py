import json
from pathlib import Path

from app.rag.answer_generation import SourceCitedAnswerGenerator
from app.rag.chunker import chunk_document
from app.rag.document_loader import load_txt_document
from app.rag.embeddings import EmbeddingProvider, HashingEmbeddingProvider
from app.rag.models import EmbeddedChunk, GeneratedAnswer, LoadedDocument
from app.rag.retrieval import Retriever
from app.rag.vector_store import LocalVectorStore


class DocumentIngestionService:
    def __init__(
        self,
        *,
        documents_dir: Path,
        chunks_dir: Path,
        vector_store: LocalVectorStore,
        embedding_provider: EmbeddingProvider,
    ) -> None:
        self.documents_dir = documents_dir
        self.chunks_dir = chunks_dir
        self.vector_store = vector_store
        self.embedding_provider = embedding_provider

    def ingest_txt(
        self,
        *,
        document_id: str,
        filename: str,
        contents: bytes,
        created_at: str,
    ) -> tuple[LoadedDocument, int]:
        document = load_txt_document(
            document_id=document_id,
            filename=filename,
            contents=contents,
            created_at=created_at,
        )
        chunks = chunk_document(document)

        self.documents_dir.mkdir(parents=True, exist_ok=True)
        document_path = self.documents_dir / f"{document.document_id}.txt"
        document_path.write_text(document.text, encoding="utf-8")

        self.chunks_dir.mkdir(parents=True, exist_ok=True)
        chunk_path = self.chunks_dir / f"{document.document_id}.json"
        chunk_path.write_text(
            json.dumps([chunk.to_dict() for chunk in chunks], indent=2),
            encoding="utf-8",
        )

        embeddings = self.embedding_provider.embed_documents(
            [chunk.text for chunk in chunks]
        )
        self.vector_store.upsert(
            [
                EmbeddedChunk(chunk=chunk, embedding=embedding)
                for chunk, embedding in zip(chunks, embeddings)
            ]
        )

        return document, len(chunks)


class RagService:
    def __init__(
        self,
        *,
        retriever: Retriever,
        answer_generator: SourceCitedAnswerGenerator,
    ) -> None:
        self.retriever = retriever
        self.answer_generator = answer_generator

    def answer(self, question: str, top_k: int = 5) -> GeneratedAnswer:
        results = self.retriever.retrieve(question, top_k=top_k)
        return self.answer_generator.generate(question, results)


def build_local_ingestion_service(
    *,
    documents_dir: Path,
    chunks_dir: Path,
    vector_store_path: Path,
) -> DocumentIngestionService:
    embedding_provider = HashingEmbeddingProvider()
    return DocumentIngestionService(
        documents_dir=documents_dir,
        chunks_dir=chunks_dir,
        vector_store=LocalVectorStore(vector_store_path),
        embedding_provider=embedding_provider,
    )


def build_local_rag_service(vector_store_path: Path) -> RagService:
    embedding_provider = HashingEmbeddingProvider()
    vector_store = LocalVectorStore(vector_store_path)
    return RagService(
        retriever=Retriever(
            embedding_provider=embedding_provider,
            vector_store=vector_store,
        ),
        answer_generator=SourceCitedAnswerGenerator(),
    )
