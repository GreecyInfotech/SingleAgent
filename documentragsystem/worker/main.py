from __future__ import annotations

import asyncio

import structlog

from app.services.kafka_producer import kafka_publisher
from worker.consumer import ingestion_consumer

logger = structlog.get_logger()


async def main() -> None:
    await kafka_publisher.start()
    logger.info("ingestion_worker_starting")
    try:
        await ingestion_consumer.run()
    except KeyboardInterrupt:
        logger.info("ingestion_worker_interrupted")
    finally:
        await kafka_publisher.stop()


if __name__ == "__main__":
    asyncio.run(main())
