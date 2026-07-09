from __future__ import annotations

import json

import structlog
from aiokafka import AIOKafkaConsumer

from app.config import get_settings
from shared.models import UploadEvent
from worker.handlers.ingestion import ingestion_handler

logger = structlog.get_logger()


class IngestionConsumer:
    def __init__(self) -> None:
        settings = get_settings()
        self._topic = settings.kafka_upload_topic
        self._group = settings.kafka_consumer_group
        self._bootstrap = settings.kafka_bootstrap_servers
        self._consumer: AIOKafkaConsumer | None = None

    async def start(self) -> None:
        self._consumer = AIOKafkaConsumer(
            self._topic,
            bootstrap_servers=self._bootstrap,
            group_id=self._group,
            enable_auto_commit=True,
            auto_offset_reset="earliest",
            value_deserializer=lambda v: json.loads(v.decode()),
        )
        await self._consumer.start()
        logger.info("consumer_started", topic=self._topic, group=self._group)

    async def stop(self) -> None:
        if self._consumer is not None:
            await self._consumer.stop()
            self._consumer = None
            logger.info("consumer_stopped")

    async def run(self) -> None:
        await self.start()
        assert self._consumer is not None
        try:
            async for message in self._consumer:
                payload = message.value
                event = UploadEvent.model_validate(payload)
                logger.info("event_received", document_id=event.document_id)
                await ingestion_handler.process(event)
        finally:
            await self.stop()


ingestion_consumer = IngestionConsumer()
