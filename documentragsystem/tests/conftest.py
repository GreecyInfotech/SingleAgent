from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import os

os.environ.setdefault("IDEMPOTENCY_DB_PATH", "./data/test_idempotency.db")


@pytest.fixture(autouse=True)
def mock_kafka():
    with pytest.MonkeyPatch.context() as mp:
        from app.services import kafka_producer

        mp.setattr(kafka_producer.kafka_publisher, "start", AsyncMock())
        mp.setattr(kafka_producer.kafka_publisher, "stop", AsyncMock())
        mp.setattr(kafka_producer.kafka_publisher, "publish_upload", AsyncMock())
        mp.setattr(kafka_producer.kafka_publisher, "publish_dlq", AsyncMock())
        yield
