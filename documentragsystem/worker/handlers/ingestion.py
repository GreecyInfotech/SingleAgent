from __future__ import annotations

from datetime import datetime, timezone

import structlog

from app.config import get_settings
from app.services.idempotency import idempotency_store
from app.services.kafka_producer import kafka_publisher
from app.services.storage import s3_storage
from shared.models import DocumentStatus, UploadEvent
from worker.pipeline.chunker import text_chunker
from worker.pipeline.embeddings import embedding_provider
from worker.pipeline.parser import document_parser
from worker.pipeline.vector_store import vector_store

logger = structlog.get_logger()


class IngestionHandler:
    async def process(self, event: UploadEvent) -> None:
        settings = get_settings()

        if idempotency_store.is_indexed(event.document_id):
            logger.info("document_already_indexed", document_id=event.document_id)
            return

        if vector_store.document_exists(event.document_id):
            logger.info("vector_store_already_has_document", document_id=event.document_id)
            idempotency_store.update_status(event.document_id, DocumentStatus.INDEXED)
            return

        idempotency_store.update_status(event.document_id, DocumentStatus.PROCESSING)

        try:
            content = s3_storage.download(event.s3_key)
            text = document_parser.parse(content, event.filename)
            chunks = text_chunker.split(text)
            embeddings = embedding_provider.embed(chunks)
            count = vector_store.upsert_chunks(
                event.document_id,
                chunks,
                embeddings,
                metadata={"filename": event.filename, "file_hash": event.file_hash},
            )

            idempotency_store.update_status(
                event.document_id,
                DocumentStatus.INDEXED,
                chunk_count=count,
                indexed_at=datetime.now(timezone.utc).isoformat(),
            )
            logger.info("ingestion_success", document_id=event.document_id, chunks=count)

        except Exception as exc:
            await self._handle_failure(event, str(exc), settings.max_retries)

    async def _handle_failure(self, event: UploadEvent, error: str, max_retries: int) -> None:
        event.retry_count += 1
        logger.error(
            "ingestion_failed",
            document_id=event.document_id,
            retry=event.retry_count,
            error=error,
        )

        if event.retry_count < max_retries:
            await kafka_publisher.publish_upload(event)
            idempotency_store.update_status(
                event.document_id,
                DocumentStatus.PENDING,
                error_message=f"Retry {event.retry_count}/{max_retries}: {error}",
            )
            return

        await kafka_publisher.publish_dlq(event, error)
        idempotency_store.update_status(
            event.document_id,
            DocumentStatus.FAILED,
            error_message=error,
        )


ingestion_handler = IngestionHandler()
