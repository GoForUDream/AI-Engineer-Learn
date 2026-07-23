from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql+asyncpg://app:app@localhost:5432/file_upload"

    upload_root: Path = Path("./var/uploads")

    max_upload_bytes: int = Field(
        default=5 * 1024 * 1024,
        gt=0,
    )

    cors_origins: list[str] = [
        "http://localhost:5173",
    ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
