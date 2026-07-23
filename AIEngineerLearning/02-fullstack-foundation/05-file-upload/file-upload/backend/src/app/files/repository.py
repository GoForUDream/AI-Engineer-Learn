import uuid
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.files.model import UploadedFile


class FileRepositoryProtocol(Protocol):
    async def add(
        self,
        uploaded_file: UploadedFile,
    ) -> UploadedFile: ...

    async def find_owned(
        self,
        file_id: uuid.UUID,
        owner_id: str,
    ) -> UploadedFile | None: ...

    async def list_owned(
        self,
        owner_id: str,
    ) -> list[UploadedFile]: ...

    async def delete(
        self,
        uploaded_file: UploadedFile,
    ) -> None: ...


class SqlAlchemyFileRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(
        self,
        uploaded_file: UploadedFile,
    ) -> UploadedFile:
        self._session.add(uploaded_file)

        await self._session.flush()
        await self._session.refresh(uploaded_file)

        return uploaded_file

    async def find_owned(
        self,
        file_id: uuid.UUID,
        owner_id: str,
    ) -> UploadedFile | None:
        statement = select(UploadedFile).where(
            UploadedFile.id == file_id,
            UploadedFile.owner_id == owner_id,
        )

        return await self._session.scalar(statement)

    async def list_owned(
        self,
        owner_id: str,
    ) -> list[UploadedFile]:
        statement = (
            select(UploadedFile)
            .where(UploadedFile.owner_id == owner_id)
            .order_by(UploadedFile.uploaded_at.desc())
        )

        result = await self._session.scalars(statement)

        return list(result)

    async def delete(
        self,
        uploaded_file: UploadedFile,
    ) -> None:
        await self._session.delete(uploaded_file)
        await self._session.flush()
