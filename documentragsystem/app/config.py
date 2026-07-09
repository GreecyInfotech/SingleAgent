from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "documentragsystem"
    app_env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8100

    s3_endpoint_url: str = "http://localhost:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket: str = "documents"
    s3_region: str = "us-east-1"

    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_upload_topic: str = "document.upload"
    kafka_dlq_topic: str = "document.upload.dlq"
    kafka_consumer_group: str = "ingestion-worker"

    chroma_host: str = "localhost"
    chroma_port: int = 8000
    chroma_collection: str = "documents"

    max_retries: int = 3
    chunk_size: int = 1000
    chunk_overlap: int = 200
    allowed_extensions: str = ".pdf,.docx,.csv"

    idempotency_db_path: str = "./data/idempotency.db"

    @property
    def allowed_ext_set(self) -> set[str]:
        return {ext.strip().lower() for ext in self.allowed_extensions.split(",") if ext.strip()}


@lru_cache
def get_settings() -> Settings:
    return Settings()
