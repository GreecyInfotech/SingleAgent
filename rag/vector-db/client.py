from pydantic import BaseModel


class VectorDocument(BaseModel):
    id: str
    content: str
    vector: list[float]
    metadata: dict
    score: float = 0.0


class VectorDBClient:
    """Vector database client (pgvector / Pinecone / Weaviate adapter)."""

    def __init__(self, collection: str = "default") -> None:
        self.collection = collection
        self._store: dict[str, VectorDocument] = {}

    async def upsert(self, documents: list[VectorDocument]) -> int:
        for doc in documents:
            self._store[doc.id] = doc
        return len(documents)

    async def search(
        self,
        query_vector: list[float],
        top_k: int = 5,
        filter_metadata: dict | None = None,
    ) -> list[VectorDocument]:
        results = list(self._store.values())
        if filter_metadata:
            results = [
                d for d in results if all(d.metadata.get(k) == v for k, v in filter_metadata.items())
            ]
        for doc in results:
            doc.score = self._cosine_similarity(query_vector, doc.vector)
        results.sort(key=lambda d: d.score, reverse=True)
        return results[:top_k]

    async def delete(self, doc_id: str) -> bool:
        return self._store.pop(doc_id, None) is not None

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        if not a or not b or len(a) != len(b):
            return 0.0
        dot = sum(x * y for x, y in zip(a, b, strict=True))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0
