from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TodoCreate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    title: str = Field(
        min_length=1,
        max_length=200,
        examples=["Learn FastAPI"],
    )

    description: str = Field(
        default="",
        max_length=2_000,
        examples=["Build an in-memory Todo API."],
    )


class TodoUpdate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    description: str | None = Field(
        default=None,
        max_length=2_000,
    )

    completed: bool | None = None

    @field_validator("title", "description")
    @classmethod
    def reject_null_strings(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            raise ValueError("Field cannot be null.")

        return value


class TodoResponse(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
    )

    id: UUID
    title: str
    description: str
    completed: bool
    created_at: datetime


class HealthResponse(BaseModel):
    status: str = "ok"


class ErrorDetail(BaseModel):
    code: str
    message: str
    fields: list[dict[str, Any]] | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail
