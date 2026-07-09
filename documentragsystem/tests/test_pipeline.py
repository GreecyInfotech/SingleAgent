from __future__ import annotations

import io

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.idempotency import IdempotencyStore


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def store(tmp_path) -> IdempotencyStore:
    return IdempotencyStore(db_path=str(tmp_path / "test.db"))


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "UP"


def test_idempotency_hash_and_lookup(store: IdempotencyStore) -> None:
    content = b"hello world"
    file_hash = store.compute_file_hash(content)
    doc_id = store.generate_document_id(file_hash, "test.pdf")
    assert len(doc_id) == 16
    assert store.find_by_hash(file_hash) is None


def test_chunker_splits_text() -> None:
    from worker.pipeline.chunker import TextChunker

    chunker = TextChunker(chunk_size=10, overlap=2)
    chunks = chunker.split("abcdefghijklmnopqrstuvwxyz")
    assert len(chunks) >= 2


def test_parser_csv() -> None:
    from worker.pipeline.parser import DocumentParser

    parser = DocumentParser()
    content = b"name,role\nAlice,Engineer\nBob,Manager"
    text = parser.parse(content, "data.csv")
    assert "Alice" in text
    assert "Engineer" in text


def test_embeddings_dimensions() -> None:
    from worker.pipeline.embeddings import EmbeddingProvider

    provider = EmbeddingProvider(dimensions=128)
    vectors = provider.embed(["hello", "world"])
    assert len(vectors) == 2
    assert len(vectors[0]) == 128
