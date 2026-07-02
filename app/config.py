from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "production-ai-app"
    app_env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    jwt_secret: str = "change-me"
    log_level: str = "INFO"
    llm_provider: str = "mock"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
