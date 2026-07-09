from __future__ import annotations

import json

from aiokafka import AIOKafkaProducer

from app.config import get_settings
from shared.models import UploadEvent


class KafkaEventPublisher:
    def __init__(self) -> None:
        self._producer: AIOKafkaProducer | None = None
        settings = get_settings()
        self._bootstrap = settings.kafka_bootstrap_servers
        self._upload_topic = settings.kafka_upload_topic
        self._dlq_topic = settings.kafka_dlq_topic

    async def start(self) -> None:
        if self._producer is None:
            self._producer = AIOKafkaProducer(
                bootstrap_servers=self._bootstrap,
                value_serializer=lambda v: json.dumps(v, default=str).encode(),
            )
            await self._producer.start()

    async def stop(self) -> None:
        if self._producer is not None:
            await self._producer.stop()
            self._producer = None

    async def publish_upload(self, event: UploadEvent) -> None:
        await self.start()
        assert self._producer is not None
        await self._producer.send_and_wait(
            self._upload_topic,
            event.model_dump(mode="json"),
            key=event.document_id.encode(),
        )

    async def publish_dlq(self, event: UploadEvent, error: str) -> None:
        await self.start()
        assert self._producer is not None
        payload = event.model_dump(mode="json")
        payload["error"] = error
        await self._producer.send_and_wait(
            self._dlq_topic,
            payload,
            key=event.document_id.encode(),
        )


kafka_publisher = KafkaEventPublisher()
