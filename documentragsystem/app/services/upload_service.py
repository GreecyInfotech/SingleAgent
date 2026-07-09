from __future__ import annotations

import mimetypes
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.config import get_settings
from app.schemas.upload import UploadResponse
from app.services.idempotency import IdempotencyStore, idempotency_store
from app.services.kafka_producer import kafka_publisher
from app.services.storage import s3_storage
from shared.models import DocumentRecord, DocumentStatus, UploadEvent


class UploadService:
    def __init__(self, store: IdempotencyStore | None = None) -> None:
        self._store = store or idempotency_store
        self._settings = get_settings()

    def _validate_extension(self, filename: str) -> None:
        ext = Path(filename).suffix.lower()
        if ext not in self._settings.allowed_ext_set:
            allowed = ", ".join(sorted(self._settings.allowed_ext_set))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type '{ext}'. Allowed: {allowed}",
            )

    async def upload(self, file: UploadFile) -> UploadResponse:
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required.")

        self._validate_extension(file.filename)
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty file.")

        file_hash = self._store.compute_file_hash(content)
        existing = self._store.find_by_hash(file_hash)
        if existing:
            return UploadResponse(
                document_id=existing.document_id,
                status=existing.status.value,
                message="Document already exists.",
                is_duplicate=True,
            )

        document_id = self._store.generate_document_id(file_hash, file.filename)
        s3_key = f"uploads/{document_id}/{file.filename}"
        content_type = file.content_type or mimetypes.guess_type(file.filename)[0] or "application/octet-stream"

        s3_storage.upload(s3_key, content, content_type)

        record = DocumentRecord(
            document_id=document_id,
            filename=file.filename,
            file_hash=file_hash,
            s3_key=s3_key,
            status=DocumentStatus.PENDING,
        )
        self._store.save(record)

        event = UploadEvent(
            document_id=document_id,
            s3_key=s3_key,
            filename=file.filename,
            content_type=content_type,
            file_hash=file_hash,
        )
        await kafka_publisher.publish_upload(event)

        return UploadResponse(
            document_id=document_id,
            status="accepted",
            message="Upload accepted. Ingestion queued.",
            is_duplicate=False,
        )


upload_service = UploadService()
