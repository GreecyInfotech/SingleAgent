from abc import ABC, abstractmethod

from pydantic import BaseModel

from enterprise_agent_platform.core.config import get_settings
from enterprise_agent_platform.core.logging import get_logger

logger = get_logger(__name__)


class EmbeddingResult(BaseModel):
    text: str
    vector: list[float]
    model: str
    dimensions: int


class EmbeddingProvider(ABC):
    @abstractmethod
    async def embed(self, texts: list[str]) -> list[EmbeddingResult]: ...

    @abstractmethod
    async def embed_query(self, query: str) -> list[float]: ...


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self, api_key: str | None = None, model: str = "text-embedding-3-small") -> None:
        self._api_key = get_settings().openai_api_key if api_key is None else api_key
        self._model = model
        self._dimensions = 1536

    async def embed(self, texts: list[str]) -> list[EmbeddingResult]:
        if not self._api_key:
            logger.warning("openai_api_key_missing_using_mock_embeddings")
            return [
                EmbeddingResult(
                    text=text,
                    vector=self._mock_vector(text),
                    model=self._model,
                    dimensions=self._dimensions,
                )
                for text in texts
            ]

        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=self._api_key)
        response = await client.embeddings.create(model=self._model, input=texts)
        return [
            EmbeddingResult(
                text=texts[i],
                vector=item.embedding,
                model=self._model,
                dimensions=len(item.embedding),
            )
            for i, item in enumerate(response.data)
        ]

    async def embed_query(self, query: str) -> list[float]:
        results = await self.embed([query])
        return results[0].vector

    @staticmethod
    def _mock_vector(text: str) -> list[float]:
        base = sum(ord(c) for c in text[:50]) % 1000 / 1000
        return [base + (i % 10) * 0.001 for i in range(1536)]
