from __future__ import annotations

from fastapi import APIRouter, File, UploadFile, status

from app.schemas.upload import DocumentStatusResponse, UploadResponse
from app.services.idempotency import idempotency_store
from app.services.upload_service import upload_service

router = APIRouter(prefix="/api/v1", tags=["documents"])


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(file: UploadFile = File(...)) -> UploadResponse:
    return await upload_service.upload(file)


@router.get("/documents/{document_id}", response_model=DocumentStatusResponse)
async def get_document_status(document_id: str) -> DocumentStatusResponse:
    record = idempotency_store.get(document_id)
    if not record:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Document not found.")
    return DocumentStatusResponse(
        document_id=record.document_id,
        filename=record.filename,
        status=record.status.value,
        chunk_count=record.chunk_count,
        indexed_at=record.indexed_at.isoformat() if record.indexed_at else None,
        error_message=record.error_message,
    )
