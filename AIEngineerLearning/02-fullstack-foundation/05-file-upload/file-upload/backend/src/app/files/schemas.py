import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FileMetadataResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    owner_id: str
    original_name: str
    content_type: str
    size_bytes: int
    uploaded_at: datetime


class ErrorResponse(BaseModel):
    code: str
    message: str
