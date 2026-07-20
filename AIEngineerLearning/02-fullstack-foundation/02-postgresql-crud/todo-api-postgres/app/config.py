from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Todo API"

    app_env: Literal[
        "development",
        "test",
        "staging",
        "production",
    ] = "development"

    app_debug: bool = False

    database_url: str = Field(min_length=1)
    test_database_url: str | None = None

    database_echo: bool = False

    database_pool_size: int = Field(
        default=5,
        ge=1,
    )

    database_max_overflow: int = Field(
        default=10,
        ge=0,
    )

    database_pool_timeout_seconds: int = Field(
        default=30,
        ge=1,
    )

    database_pool_recycle_seconds: int = Field(
        default=1800,
        ge=1,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
