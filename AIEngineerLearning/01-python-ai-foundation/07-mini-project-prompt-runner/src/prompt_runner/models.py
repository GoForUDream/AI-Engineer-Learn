from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class PromptRunCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    prompt_name: str = Field(
        min_length=1,
        max_length=100,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
        description=("Lowercase kebab-case name, for example: summarizer-test"),
    )

    prompt_text: str = Field(
        min_length=1,
        max_length=20_000,
    )

    response_text: str = Field(
        min_length=1,
        max_length=100_000,
    )

    tags: list[str] = Field(
        default_factory=list,
        max_length=20,
    )

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, tags: list[str]) -> list[str]:
        normalized_tags: list[str] = []
        seen: set[str] = set()

        for tag in tags:
            normalized_tag = tag.strip().lower()

            if not normalized_tag:
                continue

            if len(normalized_tag) > 50:
                raise ValueError("Each tag must contain at most 50 characters.")

            if normalized_tag in seen:
                continue

            normalized_tags.append(normalized_tag)
            seen.add(normalized_tag)

        return normalized_tags


class PromptRun(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    id: str = Field(
        pattern=r"^run_\d{3,}$",
        examples=["run_001"],
    )

    created_at: datetime

    prompt_name: str = Field(
        min_length=1,
        max_length=100,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )

    prompt_text: str = Field(
        min_length=1,
        max_length=20_000,
    )

    response_text: str = Field(
        min_length=1,
        max_length=100_000,
    )

    tags: list[str] = Field(
        default_factory=list,
        max_length=20,
    )

    @field_validator("created_at")
    @classmethod
    def ensure_utc_datetime(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("created_at must include timezone information.")

        return value.astimezone(timezone.utc)


class PromptRunDocument(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: int = Field(default=1, ge=1)
    runs: list[PromptRun] = Field(default_factory=list)
