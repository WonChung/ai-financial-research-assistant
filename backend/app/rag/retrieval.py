from app.rag.embeddings import EmbeddingProvider
from app.rag.models import SearchResult
from app.rag.vector_store import LocalVectorStore


class Retriever:
    def __init__(
        self,
        *,
        embedding_provider: EmbeddingProvider,
        vector_store: LocalVectorStore,
    ) -> None:
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store

    def retrieve(
        self,
        *,
        document_id: str,
        query: str,
        top_k: int = 5,
    ) -> list[SearchResult]:
        query_embedding = self.embedding_provider.embed_query(query)
        return self.vector_store.search(
            query_embedding,
            document_id=document_id,
            top_k=top_k,
        )
