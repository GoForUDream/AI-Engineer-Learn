from io import BytesIO
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from fastapi import UploadFile
from starlette.datastructures import Headers

from src.app.errors import InvalidUploadError
from src.app.files.repository import FileRepositoryProtocol
from src.app.files.service import FileService
from src.app.files.storage import LocalFileStorage


def make_upload(
    filename: str,
    content: bytes = b"hello",
    content_type: str = "text/plain",
) -> UploadFile:
    return UploadFile(
        filename=filename,
        file=BytesIO(content),
        headers=Headers(
            {
                "content-type": content_type,
            }
        ),
    )


@pytest.fixture
def session() -> AsyncMock:
    result = AsyncMock()
    result.commit = AsyncMock()
    result.rollback = AsyncMock()

    return result


@pytest.fixture
def repository() -> AsyncMock:
    result = AsyncMock(spec=FileRepositoryProtocol)

    async def return_uploaded_file(
        uploaded_file,
    ):
        return uploaded_file

    result.add.side_effect = return_uploaded_file

    return result


@pytest.mark.asyncio
async def test_unsupported_extension_is_rejected(
    tmp_path: Path,
    session: AsyncMock,
    repository: AsyncMock,
) -> None:
    storage = LocalFileStorage(tmp_path)
    await storage.initialize()

    service = FileService(
        session=session,
        repository=repository,
        storage=storage,
        max_upload_bytes=100,
    )

    with pytest.raises(
        InvalidUploadError,
        match="Only .txt and .md",
    ):
        await service.upload_file(
            upload=make_upload("payload.exe"),
            owner_id="user-1",
        )

    repository.add.assert_not_awaited()


@pytest.mark.asyncio
async def test_invalid_reported_content_type_is_rejected(
    tmp_path: Path,
    session: AsyncMock,
    repository: AsyncMock,
) -> None:
    storage = LocalFileStorage(tmp_path)
    await storage.initialize()

    service = FileService(
        session=session,
        repository=repository,
        storage=storage,
        max_upload_bytes=100,
    )

    with pytest.raises(
        InvalidUploadError,
        match="Invalid content type",
    ):
        await service.upload_file(
            upload=make_upload(
                filename="notes.txt",
                content_type="application/pdf",
            ),
            owner_id="user-1",
        )


@pytest.mark.asyncio
async def test_filename_path_is_rejected(
    tmp_path: Path,
    session: AsyncMock,
    repository: AsyncMock,
) -> None:
    storage = LocalFileStorage(tmp_path)
    await storage.initialize()

    service = FileService(
        session=session,
        repository=repository,
        storage=storage,
        max_upload_bytes=100,
    )

    with pytest.raises(
        InvalidUploadError,
        match="must not contain a path",
    ):
        await service.upload_file(
            upload=make_upload("../../notes.txt"),
            owner_id="user-1",
        )


@pytest.mark.asyncio
async def test_database_failure_removes_stored_bytes(
    tmp_path: Path,
    session: AsyncMock,
    repository: AsyncMock,
) -> None:
    storage = LocalFileStorage(tmp_path)
    await storage.initialize()

    repository.add.side_effect = RuntimeError("database unavailable")

    service = FileService(
        session=session,
        repository=repository,
        storage=storage,
        max_upload_bytes=100,
    )

    with pytest.raises(
        RuntimeError,
        match="database unavailable",
    ):
        await service.upload_file(
            upload=make_upload("notes.txt"),
            owner_id="user-1",
        )

    session.rollback.assert_awaited_once()

    assert list((tmp_path / "objects").iterdir()) == []
