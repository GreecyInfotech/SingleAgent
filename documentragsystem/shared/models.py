from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"


class UploadEvent(BaseModel):
    document_id: str
    s3_key: str
    filename: str
    content_type: str
    file_hash: str
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    retry_count: int = 0


class DocumentRecord(BaseModel):
    document_id: str
    filename: str
    file_hash: str
    s3_key: str
    status: DocumentStatus = DocumentStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    indexed_at: datetime | None = None
    chunk_count: int = 0
    error_message: str | None = None
