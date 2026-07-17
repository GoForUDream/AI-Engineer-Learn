from __future__ import annotations

from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict, field_validator
from uuid import UUID, uuid4


def utc_now() -> datetime:
    """Return a timezone-aware UTC datetime."""

    return datetime.now(timezone.utc)


class PromptRun(BaseModel):
    """Represents one prompt execution."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=utc_now)
    prompt: str = Field(min_length=1)
    response: str = Field(min_length=1)
    tags: list[str] = Field(default_factory=list)

    @field_validator("created_at")
    @classmethod
    def validate_created_at(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("created_at must be timezone-aware")

        return value.astimezone(timezone.utc)

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, tags: list[str]) -> list[str]:
        normalized_tags: list[str] = []
        seen: set[str] = set()

        for tag in tags:
            normalized_tag = tag.strip().lower()

            if not normalized_tag or normalized_tag in seen:
                continue

            normalized_tags.append(normalized_tag)
            seen.add(normalized_tag)

        return normalized_tags


class PromptRunDocument(BaseModel):
    """
    Root shape persisted to prompt_runs.json.

    Versioning the document gives us a migration path if the JSON structure
    changes later.
    """

    model_config = ConfigDict(extra="forbid")
    version: int = Field(default=1, ge=1)
    records: list[PromptRun] = Field(default_factory=list)
