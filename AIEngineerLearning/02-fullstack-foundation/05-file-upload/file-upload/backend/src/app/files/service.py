import logging
import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.errors import (
    InvalidUploadError,
    UploadedFileNotFoundError,
)
from app.files.model import UploadedFile
from app.files.repository import FileRepositoryProtocol
from app.files.storage import FileStorageProtocol

logger = logging.getLogger(__name__)


ALLOWED_CONTENT_TYPES: dict[str, set[str]] = {
    ".txt": {
        "text/plain",
    },
    ".md": {
        "text/markdown",
        "text/plain",
    },
}


class FileService:
    def __init__(
        self,
        session: AsyncSession,
        repository: FileRepositoryProtocol,
        storage: FileStorageProtocol,
        max_upload_bytes: int,
    ) -> None:
        self._session = session
        self._repository = repository
        self._storage = storage
        self._max_upload_bytes = max_upload_bytes

    @staticmethod
    def _validate_upload_metadata(
        upload: UploadFile,
    ) -> tuple[str, str]:
        original_name = upload.filename

        if not original_name:
            raise InvalidUploadError("A filename is required.")

        if "\x00" in original_name:
            raise InvalidUploadError("Filename contains an invalid character.")

        if "/" in original_name or "\\" in original_name:
            raise InvalidUploadError("Filename must not contain a path.")

        if len(original_name) > 255:
            raise InvalidUploadError("Filename must not exceed 255 characters.")

        extension = Path(original_name).suffix.lower()

        allowed_content_types = ALLOWED_CONTENT_TYPES.get(extension)

        if allowed_content_types is None:
            raise InvalidUploadError("Only .txt and .md files are allowed.")

        reported_content_type = upload.content_type or "application/octet-stream"

        normalized_content_type = reported_content_type.partition(";")[0].strip().lower()

        if normalized_content_type not in allowed_content_types:
            allowed_values = ", ".join(sorted(allowed_content_types))

            raise InvalidUploadError(
                f"Invalid content type for {extension}. Expected one of: {allowed_values}."
            )

        return original_name, normalized_content_type

    async def upload_file(
        self,
        upload: UploadFile,
        owner_id: str,
    ) -> UploadedFile:
        (
            original_name,
            content_type,
        ) = self._validate_upload_metadata(upload)

        stored_upload = await self._storage.save(
            upload=upload,
            max_bytes=self._max_upload_bytes,
        )

        uploaded_file = UploadedFile(
            owner_id=owner_id,
            original_name=original_name,
            stored_name=stored_upload.stored_name,
            content_type=content_type,
            size_bytes=stored_upload.size_bytes,
        )

        try:
            uploaded_file = await self._repository.add(uploaded_file)

            await self._session.commit()

            return uploaded_file

        except Exception:
            await self._session.rollback()

            await self._storage.discard(stored_upload.stored_name)

            raise

    async def list_files(
        self,
        owner_id: str,
    ) -> list[UploadedFile]:
        return await self._repository.list_owned(owner_id)

    async def get_file(
        self,
        file_id: uuid.UUID,
        owner_id: str,
    ) -> UploadedFile:
        uploaded_file = await self._repository.find_owned(
            file_id=file_id,
            owner_id=owner_id,
        )

        if uploaded_file is None:
            raise UploadedFileNotFoundError()

        return uploaded_file

    async def delete_file(
        self,
        file_id: uuid.UUID,
        owner_id: str,
    ) -> None:
        uploaded_file = await self.get_file(
            file_id=file_id,
            owner_id=owner_id,
        )

        quarantined = await self._storage.quarantine(uploaded_file.stored_name)

        try:
            await self._repository.delete(uploaded_file)

            await self._session.commit()

        except Exception:
            await self._session.rollback()

            await self._storage.restore(quarantined)

            raise

        try:
            await self._storage.purge(quarantined)
        except Exception:
            logger.exception(
                "Could not purge quarantined file %s",
                quarantined.quarantine_name,
            )
