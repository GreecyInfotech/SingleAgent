from __future__ import annotations

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import get_settings


class VectorStore:
    def __init__(self) -> None:
        settings = get_settings()
        self._collection_name = settings.chroma_collection
        self._client = chromadb.PersistentClient(
            path="./chroma_data",
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            name=self._collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def upsert_chunks(
        self,
        document_id: str,
        chunks: list[str],
        embeddings: list[list[float]],
        metadata: dict | None = None,
    ) -> int:
        if not chunks:
            return 0

        base_meta = metadata or {}
        ids = [f"{document_id}:{i}" for i in range(len(chunks))]
        metadatas = [
            {**base_meta, "document_id": document_id, "chunk_index": i}
            for i in range(len(chunks))
        ]
        self._collection.upsert(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
        )
        return len(chunks)

    def document_exists(self, document_id: str) -> bool:
        result = self._collection.get(where={"document_id": document_id}, limit=1)
        return bool(result and result.get("ids"))


vector_store = VectorStore()
