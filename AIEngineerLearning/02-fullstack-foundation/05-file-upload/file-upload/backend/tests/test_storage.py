from io import BytesIO
from pathlib import Path

import pytest
from fastapi import UploadFile
from starlette.datastructures import Headers

from src.app.errors import (
    InvalidUploadError,
    UploadTooLargeError,
)
from src.app.files.storage import LocalFileStorage


def make_upload(
    content: bytes,
    filename: str = "notes.txt",
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


@pytest.mark.asyncio
async def test_valid_upload_uses_generated_name(
    tmp_path: Path,
) -> None:
    storage = LocalFileStorage(tmp_path)
    await storage.initialize()

    result = await storage.save(
        upload=make_upload(b"hello"),
        max_bytes=100,
    )

    stored_path = tmp_path / "objects" / result.stored_name

    assert result.size_bytes == 5
    assert result.stored_name != "notes.txt"
    assert stored_path.read_bytes() == b"hello"


@pytest.mark.asyncio
async def test_empty_upload_is_rejected_and_cleaned(
    tmp_path: Path,
) -> None:
    storage = LocalFileStorage(tmp_path)
    await storage.initialize()

    with pytest.raises(
        InvalidUploadError,
        match="Empty files",
    ):
        await storage.save(
            upload=make_upload(b""),
            max_bytes=100,
        )

    assert list((tmp_path / "objects").iterdir()) == []

    assert list((tmp_path / ".quarantine").iterdir()) == []


@pytest.mark.asyncio
async def test_oversized_upload_is_rejected_and_cleaned(
    tmp_path: Path,
) -> None:
    storage = LocalFileStorage(tmp_path)
    await storage.initialize()

    with pytest.raises(
        UploadTooLargeError,
        match="exceeds",
    ):
        await storage.save(
            upload=make_upload(b"123456"),
            max_bytes=5,
        )

    assert list((tmp_path / "objects").iterdir()) == []

    assert list((tmp_path / ".quarantine").iterdir()) == []


@pytest.mark.asyncio
async def test_binary_upload_is_rejected(
    tmp_path: Path,
) -> None:
    storage = LocalFileStorage(tmp_path)
    await storage.initialize()

    with pytest.raises(
        InvalidUploadError,
        match="UTF-8",
    ):
        await storage.save(
            upload=make_upload(b"\xff\xfe\x00"),
            max_bytes=100,
        )


@pytest.mark.asyncio
async def test_storage_key_cannot_escape_directory(
    tmp_path: Path,
) -> None:
    storage = LocalFileStorage(tmp_path)
    await storage.initialize()

    with pytest.raises(ValueError):
        await storage.discard("../../secret.upload")
