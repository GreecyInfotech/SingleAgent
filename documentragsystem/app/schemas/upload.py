from __future__ import annotations

from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    document_id: str
    status: str
    message: str
    is_duplicate: bool = False


class DocumentStatusResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    chunk_count: int = 0
    indexed_at: str | None = None
    error_message: str | None = None


class HealthResponse(BaseModel):
    status: str
    service: str
