from __future__ import annotations

from app.config import get_settings


class TextChunker:
    def __init__(self, chunk_size: int | None = None, overlap: int | None = None) -> None:
        settings = get_settings()
        self._chunk_size = chunk_size or settings.chunk_size
        self._overlap = overlap or settings.chunk_overlap

    def split(self, text: str) -> list[str]:
        if not text:
            return []

        chunks: list[str] = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = min(start + self._chunk_size, text_len)
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            if end >= text_len:
                break
            start = max(end - self._overlap, start + 1)

        return chunks


text_chunker = TextChunker()
