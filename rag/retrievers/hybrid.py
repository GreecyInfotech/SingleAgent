from pydantic import BaseModel

from rag.embeddings.provider import EmbeddingProvider
from rag.vector_db.client import VectorDBClient, VectorDocument


class RetrievalResult(BaseModel):
    query: str
    documents: list[VectorDocument]
    total_found: int


class HybridRetriever:
    """Combines vector similarity search with keyword filtering."""

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_db: VectorDBClient,
        top_k: int = 5,
        score_threshold: float = 0.5,
    ) -> None:
        self._embeddings = embedding_provider
        self._vector_db = vector_db
        self._top_k = top_k
        self._score_threshold = score_threshold

    async def retrieve(
        self,
        query: str,
        filter_metadata: dict | None = None,
    ) -> RetrievalResult:
        query_vector = await self._embeddings.embed_query(query)
        documents = await self._vector_db.search(
            query_vector,
            top_k=self._top_k,
            filter_metadata=filter_metadata,
        )
        filtered = [d for d in documents if d.score >= self._score_threshold]
        return RetrievalResult(
            query=query,
            documents=filtered,
            total_found=len(filtered),
        )

    async def index_documents(self, texts: list[str], metadata: list[dict] | None = None) -> int:
        embeddings = await self._embeddings.embed(texts)
        docs = [
            VectorDocument(
                id=f"doc-{i}",
                content=emb.text,
                vector=emb.vector,
                metadata=(metadata[i] if metadata else {}),
            )
            for i, emb in enumerate(embeddings)
        ]
        return await self._vector_db.upsert(docs)
