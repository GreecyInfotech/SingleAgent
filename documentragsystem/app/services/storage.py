from __future__ import annotations

import boto3
from botocore.client import Config

from app.config import get_settings


class S3Storage:
    def __init__(self) -> None:
        self._client = None
        settings = get_settings()
        self._bucket = settings.s3_bucket
        self._settings = settings

    def _get_client(self):
        if self._client is None:
            self._client = boto3.client(
                "s3",
                endpoint_url=self._settings.s3_endpoint_url,
                aws_access_key_id=self._settings.s3_access_key,
                aws_secret_access_key=self._settings.s3_secret_key,
                region_name=self._settings.s3_region,
                config=Config(signature_version="s3v4"),
            )
            self._ensure_bucket()
        return self._client

    def _ensure_bucket(self) -> None:
        assert self._client is not None
        try:
            self._client.head_bucket(Bucket=self._bucket)
        except Exception:
            self._client.create_bucket(Bucket=self._bucket)

    def upload(self, key: str, content: bytes, content_type: str) -> str:
        client = self._get_client()
        client.put_object(
            Bucket=self._bucket,
            Key=key,
            Body=content,
            ContentType=content_type,
        )
        return key

    def download(self, key: str) -> bytes:
        client = self._get_client()
        response = client.get_object(Bucket=self._bucket, Key=key)
        return response["Body"].read()


s3_storage = S3Storage()
