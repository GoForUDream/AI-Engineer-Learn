import os
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import aiofiles
from anyio import to_thread
from fastapi import UploadFile

from app.errors import (
    InvalidUploadError,
    StorageConsistencyError,
    UploadTooLargeError,
)

CHUNK_SIZE = 64 * 1024
STORAGE_SUFFIX = ".upload"


@dataclass(frozen=True, slots=True)
class StoredUpload:
    stored_name: str
    size_bytes: int


@dataclass(frozen=True, slots=True)
class QuarantinedUpload:
    stored_name: str
    quarantine_name: str


class FileStorageProtocol(Protocol):
    async def initialize(self) -> None: ...

    async def save(
        self,
        upload: UploadFile,
        max_bytes: int,
    ) -> StoredUpload: ...

    async def discard(
        self,
        stored_name: str,
    ) -> None: ...

    async def quarantine(
        self,
        stored_name: str,
    ) -> QuarantinedUpload: ...

    async def restore(
        self,
        quarantined: QuarantinedUpload,
    ) -> None: ...

    async def purge(
        self,
        quarantined: QuarantinedUpload,
    ) -> None: ...


class LocalFileStorage:
    def __init__(self, root: Path) -> None:
        self._root = root.resolve()
        self._objects = self._root / "objects"
        self._quarantine = self._root / ".quarantine"

    async def initialize(self) -> None:
        await to_thread.run_sync(
            self._objects.mkdir,
            0o750,
            True,
            True,
        )

        await to_thread.run_sync(
            self._quarantine.mkdir,
            0o750,
            True,
            True,
        )

    @staticmethod
    def _generate_name() -> str:
        return f"{uuid.uuid4().hex}{STORAGE_SUFFIX}"

    @staticmethod
    def _validate_storage_name(stored_name: str) -> None:
        path = Path(stored_name)

        if path.name != stored_name:
            raise ValueError("Storage key must not contain a path.")

        if path.suffix != STORAGE_SUFFIX:
            raise ValueError("Invalid storage key suffix.")

        try:
            parsed_id = uuid.UUID(path.stem)
        except ValueError as exc:
            raise ValueError("Invalid storage key identifier.") from exc

        if parsed_id.hex != path.stem:
            raise ValueError("Storage key is not canonical.")

    def _safe_path(
        self,
        directory: Path,
        stored_name: str,
    ) -> Path:
        self._validate_storage_name(stored_name)

        directory = directory.resolve()
        candidate = (directory / stored_name).resolve()

        if candidate.parent != directory:
            raise ValueError("Storage path escaped its directory.")

        return candidate

    async def save(
        self,
        upload: UploadFile,
        max_bytes: int,
    ) -> StoredUpload:
        final_name = self._generate_name()
        temporary_name = self._generate_name()

        final_path = self._safe_path(
            self._objects,
            final_name,
        )
        temporary_path = self._safe_path(
            self._quarantine,
            temporary_name,
        )

        total_size = 0

        try:
            async with aiofiles.open(
                temporary_path,
                mode="xb",
            ) as destination:
                while chunk := await upload.read(CHUNK_SIZE):
                    total_size += len(chunk)

                    if total_size > max_bytes:
                        raise UploadTooLargeError(f"File exceeds the {max_bytes}-byte limit.")

                    await destination.write(chunk)

                await destination.flush()

            if total_size == 0:
                raise InvalidUploadError("Empty files are not allowed.")

            await to_thread.run_sync(
                os.replace,
                temporary_path,
                final_path,
            )

            return StoredUpload(
                stored_name=final_name,
                size_bytes=total_size,
            )

        except Exception:
            temporary_path.unlink(missing_ok=True)
            final_path.unlink(missing_ok=True)
            raise

        finally:
            await upload.close()

    async def discard(
        self,
        stored_name: str,
    ) -> None:
        path = self._safe_path(
            self._objects,
            stored_name,
        )

        await to_thread.run_sync(
            path.unlink,
            True,
        )

    async def quarantine(
        self,
        stored_name: str,
    ) -> QuarantinedUpload:
        source = self._safe_path(
            self._objects,
            stored_name,
        )

        quarantine_name = self._generate_name()

        destination = self._safe_path(
            self._quarantine,
            quarantine_name,
        )

        try:
            await to_thread.run_sync(
                os.replace,
                source,
                destination,
            )
        except FileNotFoundError as exc:
            raise StorageConsistencyError("Metadata exists but stored bytes are missing.") from exc

        return QuarantinedUpload(
            stored_name=stored_name,
            quarantine_name=quarantine_name,
        )

    async def restore(
        self,
        quarantined: QuarantinedUpload,
    ) -> None:
        source = self._safe_path(
            self._quarantine,
            quarantined.quarantine_name,
        )

        destination = self._safe_path(
            self._objects,
            quarantined.stored_name,
        )

        await to_thread.run_sync(
            os.replace,
            source,
            destination,
        )

    async def purge(
        self,
        quarantined: QuarantinedUpload,
    ) -> None:
        path = self._safe_path(
            self._quarantine,
            quarantined.quarantine_name,
        )

        await to_thread.run_sync(
            path.unlink,
            True,
        )
