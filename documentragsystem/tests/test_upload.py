from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from fastapi import UploadFile

from app.services.upload_service import UploadService
from app.services.idempotency import IdempotencyStore


@pytest.mark.asyncio
async def test_upload_rejects_unsupported_type(tmp_path) -> None:
    store = IdempotencyStore(db_path=str(tmp_path / "db.sqlite"))
    service = UploadService(store=store)
    upload = UploadFile(filename="virus.exe", file=__import__("io").BytesIO(b"data"))

    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc:
        await service.upload(upload)
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_upload_new_document(tmp_path) -> None:
    store = IdempotencyStore(db_path=str(tmp_path / "db.sqlite"))
    service = UploadService(store=store)
    content = b"%PDF-1.4 sample"
    upload = UploadFile(filename="sample.pdf", file=__import__("io").BytesIO(content))

    with (
        patch("app.services.upload_service.s3_storage.upload", return_value="key"),
        patch("app.services.upload_service.kafka_publisher.publish_upload", new_callable=AsyncMock),
    ):
        result = await service.upload(upload)

    assert result.is_duplicate is False
    assert result.status == "accepted"
    assert len(result.document_id) == 16


@pytest.mark.asyncio
async def test_upload_duplicate_returns_existing_id(tmp_path) -> None:
    store = IdempotencyStore(db_path=str(tmp_path / "db.sqlite"))
    service = UploadService(store=store)
    content = b"same content"
    upload1 = UploadFile(filename="a.pdf", file=__import__("io").BytesIO(content))
    upload2 = UploadFile(filename="b.pdf", file=__import__("io").BytesIO(content))

    with (
        patch("app.services.upload_service.s3_storage.upload", return_value="key"),
        patch("app.services.upload_service.kafka_publisher.publish_upload", new_callable=AsyncMock),
    ):
        first = await service.upload(upload1)
        second = await service.upload(upload2)

    assert second.is_duplicate is True
    assert second.document_id == first.document_id
