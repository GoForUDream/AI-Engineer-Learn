from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.files.repository import SqlAlchemyFileRepository
from app.files.service import FileService
from app.files.storage import LocalFileStorage

from ..config import Settings, get_settings


@lru_cache
def get_file_storage() -> LocalFileStorage:
    settings = get_settings()
    return LocalFileStorage(settings.upload_root)


async def get_current_owner_id() -> str:
    # Lesson-only identity.
    #
    # In production, this dependency should verify a JWT/session and return
    # the authenticated subject. Do not trust an arbitrary owner header.
    return "lesson-user"


def get_file_service(
    session: Annotated[
        AsyncSession,
        Depends(get_session),
    ],
    storage: Annotated[
        LocalFileStorage,
        Depends(get_file_storage),
    ],
    settings: Annotated[
        Settings,
        Depends(get_settings),
    ],
) -> FileService:
    repository = SqlAlchemyFileRepository(session)

    return FileService(
        session=session,
        repository=repository,
        storage=storage,
        max_upload_bytes=settings.max_upload_bytes,
    )
