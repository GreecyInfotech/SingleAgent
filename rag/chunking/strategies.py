from abc import ABC, abstractmethod
from enum import StrEnum

from pydantic import BaseModel


class ChunkStrategy(StrEnum):
    FIXED_SIZE = "fixed_size"
    SENTENCE = "sentence"
    PARAGRAPH = "paragraph"
    SEMANTIC = "semantic"


class DocumentChunk(BaseModel):
    id: str
    content: str
    metadata: dict
    start_index: int
    end_index: int


class Chunker(ABC):
    @abstractmethod
    def chunk(self, text: str, metadata: dict | None = None) -> list[DocumentChunk]: ...


class FixedSizeChunker(Chunker):
    def __init__(self, chunk_size: int = 512, overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str, metadata: dict | None = None) -> list[DocumentChunk]:
        chunks: list[DocumentChunk] = []
        meta = metadata or {}
        start = 0
        idx = 0

        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            content = text[start:end]
            chunks.append(
                DocumentChunk(
                    id=f"chunk-{idx}",
                    content=content,
                    metadata={**meta, "chunk_index": idx},
                    start_index=start,
                    end_index=end,
                )
            )
            start = end - self.overlap if end < len(text) else end
            idx += 1

        return chunks


class SentenceChunker(Chunker):
    def chunk(self, text: str, metadata: dict | None = None) -> list[DocumentChunk]:
        import re

        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        meta = metadata or {}
        return [
            DocumentChunk(
                id=f"chunk-{i}",
                content=sentence,
                metadata={**meta, "chunk_index": i},
                start_index=0,
                end_index=len(sentence),
            )
            for i, sentence in enumerate(sentences)
            if sentence
        ]


def get_chunker(strategy: ChunkStrategy, **kwargs) -> Chunker:
    if strategy == ChunkStrategy.SENTENCE:
        return SentenceChunker()
    return FixedSizeChunker(**kwargs)
