from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


class TodoCreate(BaseModel):
    """Request body used to create a todo."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    title: str = Field(
        min_length=1,
        max_length=200,
    )

    description: str = Field(
        default="",
        max_length=5_000,
    )

    due_at: datetime | None = None


class TodoUpdate(BaseModel):
    """PATCH request body."""

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
        max_length=5_000,
    )

    completed: bool | None = None
    due_at: datetime | None = None

    @model_validator(mode="after")
    def reject_null_for_required_fields(
        self,
    ) -> TodoUpdate:
        non_nullable_fields = {
            "title",
            "description",
            "completed",
        }

        for field_name in self.model_fields_set & non_nullable_fields:
            if getattr(self, field_name) is None:
                raise ValueError(f"{field_name} cannot be null.")

        return self


class TodoResponse(BaseModel):
    """Response representation of a todo."""

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
    )

    id: UUID
    title: str
    description: str
    completed: bool
    created_at: datetime
    updated_at: datetime
    due_at: datetime | None


class HealthResponse(BaseModel):
    status: str


class ErrorField(BaseModel):
    location: list[str]
    message: str
    type: str


class ErrorDetail(BaseModel):
    code: str
    message: str
    fields: list[ErrorField] | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail
