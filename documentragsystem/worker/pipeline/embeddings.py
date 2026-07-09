from __future__ import annotations

import hashlib


class EmbeddingProvider:
    """Deterministic mock embeddings for local/dev without external API."""

    def __init__(self, dimensions: int = 384) -> None:
        self._dimensions = dimensions

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(text) for text in texts]

    def _embed_one(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode()).digest()
        base = [b / 255.0 for b in digest]
        vector = [base[i % len(base)] + (i * 0.0001) for i in range(self._dimensions)]
        norm = sum(v * v for v in vector) ** 0.5 or 1.0
        return [v / norm for v in vector]


embedding_provider = EmbeddingProvider()
