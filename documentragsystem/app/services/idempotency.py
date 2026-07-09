from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path

from app.config import get_settings
from shared.models import DocumentRecord, DocumentStatus


class IdempotencyStore:
    """SQLite-backed idempotency and document status store."""

    def __init__(self, db_path: str | None = None) -> None:
        settings = get_settings()
        self._db_path = Path(db_path or settings.idempotency_db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    document_id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    file_hash TEXT NOT NULL UNIQUE,
                    s3_key TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    created_at TEXT NOT NULL,
                    indexed_at TEXT,
                    chunk_count INTEGER DEFAULT 0,
                    error_message TEXT
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_file_hash ON documents(file_hash)")
            conn.commit()

    @staticmethod
    def compute_file_hash(content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

    @staticmethod
    def generate_document_id(file_hash: str, filename: str) -> str:
        digest = hashlib.sha256(f"{file_hash}:{filename}".encode()).hexdigest()
        return digest[:16]

    def find_by_hash(self, file_hash: str) -> DocumentRecord | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM documents WHERE file_hash = ?", (file_hash,)
            ).fetchone()
        return self._row_to_record(row) if row else None

    def get(self, document_id: str) -> DocumentRecord | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM documents WHERE document_id = ?", (document_id,)
            ).fetchone()
        return self._row_to_record(row) if row else None

    def save(self, record: DocumentRecord) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO documents (
                    document_id, filename, file_hash, s3_key, status,
                    created_at, indexed_at, chunk_count, error_message
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.document_id,
                    record.filename,
                    record.file_hash,
                    record.s3_key,
                    record.status.value,
                    record.created_at.isoformat(),
                    record.indexed_at.isoformat() if record.indexed_at else None,
                    record.chunk_count,
                    record.error_message,
                ),
            )
            conn.commit()

    def update_status(
        self,
        document_id: str,
        status: DocumentStatus,
        *,
        chunk_count: int | None = None,
        indexed_at: str | None = None,
        error_message: str | None = None,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE documents
                SET status = ?,
                    chunk_count = COALESCE(?, chunk_count),
                    indexed_at = COALESCE(?, indexed_at),
                    error_message = ?
                WHERE document_id = ?
                """,
                (status.value, chunk_count, indexed_at, error_message, document_id),
            )
            conn.commit()

    def is_indexed(self, document_id: str) -> bool:
        record = self.get(document_id)
        return record is not None and record.status == DocumentStatus.INDEXED

    @staticmethod
    def _row_to_record(row: sqlite3.Row) -> DocumentRecord:
        from datetime import datetime

        return DocumentRecord(
            document_id=row["document_id"],
            filename=row["filename"],
            file_hash=row["file_hash"],
            s3_key=row["s3_key"],
            status=DocumentStatus(row["status"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            indexed_at=datetime.fromisoformat(row["indexed_at"]) if row["indexed_at"] else None,
            chunk_count=row["chunk_count"],
            error_message=row["error_message"],
        )


idempotency_store = IdempotencyStore()
