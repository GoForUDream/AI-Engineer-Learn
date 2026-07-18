from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path

import portalocker
from pydantic import ValidationError

from prompt_runner.models import (
    PromptRun,
    PromptRunCreate,
    PromptRunDocument,
    utc_now,
)


class PromptRunnerStorageError(Exception):
    """Base exception for storage-related failures."""


class StorageReadError(PromptRunnerStorageError):
    """Raised when the storage file cannot be read."""


class StorageWriteError(PromptRunnerStorageError):
    """Raised when the storage file cannot be written."""


class InvalidStorageDocumentError(PromptRunnerStorageError):
    """Raised when the JSON file is invalid or has an unexpected shape."""


class PromptRunNotFoundError(PromptRunnerStorageError):
    """Raised when a prompt run cannot be found by ID."""


class StorageLockError(PromptRunnerStorageError):
    """Raised when the application cannot acquire its storage lock."""


class JsonPromptRunStorage:
    _ID_PATTERN = re.compile(r"^run_(\d+)$")

    def __init__(
        self,
        file_path: Path,
        *,
        lock_timeout_seconds: float = 10.0,
    ) -> None:
        self._file_path = file_path
        self._lock_file_path = file_path.with_suffix(f"{file_path.suffix}.lock")
        self._lock_timeout_seconds = lock_timeout_seconds

    @property
    def file_path(self) -> Path:
        return self._file_path

    def initialize(self) -> None:
        """
        Create the output directory and initial JSON document if missing.
        """

        self._file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if self._file_path.exists():
            return

        try:
            with portalocker.Lock(
                self._lock_file_path,
                mode="a",
                timeout=self._lock_timeout_seconds,
            ):
                if not self._file_path.exists():
                    self._write_atomic(PromptRunDocument())

        except portalocker.exceptions.LockException as exc:
            raise StorageLockError(
                f"Could not acquire storage lock: {self._lock_file_path}"
            ) from exc

    def add(self, input_data: PromptRunCreate) -> PromptRun:
        """
        Create and persist a new prompt run.

        ID generation and writing happen inside the same file lock to prevent
        two concurrent processes from generating the same ID.
        """

        self._file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        try:
            with portalocker.Lock(
                self._lock_file_path,
                mode="a",
                timeout=self._lock_timeout_seconds,
            ):
                document = self._read_document_or_default()

                prompt_run = PromptRun(
                    id=self._generate_next_id(document.runs),
                    created_at=utc_now(),
                    prompt_name=input_data.prompt_name,
                    prompt_text=input_data.prompt_text,
                    response_text=input_data.response_text,
                    tags=input_data.tags,
                )

                updated_document = PromptRunDocument(
                    version=document.version,
                    runs=[*document.runs, prompt_run],
                )

                self._write_atomic(updated_document)

                return prompt_run

        except portalocker.exceptions.LockException as exc:
            raise StorageLockError(
                f"Could not acquire storage lock: {self._lock_file_path}"
            ) from exc

    def list_all(self) -> list[PromptRun]:
        """
        Return all prompt runs in creation order.
        """

        self.initialize()
        document = self._read_document()

        return list(document.runs)

    def get_by_id(self, prompt_run_id: str) -> PromptRun:
        """
        Return one prompt run by ID.

        Raises PromptRunNotFoundError when no matching record exists.
        """

        normalized_id = prompt_run_id.strip().lower()

        for prompt_run in self.list_all():
            if prompt_run.id == normalized_id:
                return prompt_run

        raise PromptRunNotFoundError(f'Prompt run "{prompt_run_id}" was not found.')

    def _read_document_or_default(self) -> PromptRunDocument:
        if not self._file_path.exists():
            return PromptRunDocument()

        return self._read_document()

    def _read_document(self) -> PromptRunDocument:
        try:
            raw_content = self._file_path.read_text(
                encoding="utf-8",
            )
        except OSError as exc:
            raise StorageReadError(
                f"Could not read storage file: {self._file_path}"
            ) from exc

        if not raw_content.strip():
            raise InvalidStorageDocumentError(
                f"Storage file is empty: {self._file_path}"
            )

        try:
            raw_document = json.loads(raw_content)
        except json.JSONDecodeError as exc:
            raise InvalidStorageDocumentError(
                f"Storage file contains invalid JSON at "
                f"line {exc.lineno}, column {exc.colno}: "
                f"{self._file_path}"
            ) from exc

        try:
            return PromptRunDocument.model_validate(raw_document)
        except ValidationError as exc:
            raise InvalidStorageDocumentError(
                "Storage file contains data that does not match the "
                f"expected schema:\n{exc}"
            ) from exc

    def _write_atomic(
        self,
        document: PromptRunDocument,
    ) -> None:
        """
        Write to a temporary file before replacing the destination file.

        The temporary file is created in the same directory so os.replace()
        can perform an atomic replacement on the same filesystem.
        """

        self._file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        serialized_document = document.model_dump_json(
            indent=2,
        )

        temporary_file_path: Path | None = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self._file_path.parent,
                prefix=f".{self._file_path.name}.",
                suffix=".tmp",
                delete=False,
            ) as temporary_file:
                temporary_file.write(serialized_document)
                temporary_file.write("\n")
                temporary_file.flush()

                os.fsync(temporary_file.fileno())

                temporary_file_path = Path(temporary_file.name)

            os.replace(
                temporary_file_path,
                self._file_path,
            )

        except OSError as exc:
            if temporary_file_path is not None:
                temporary_file_path.unlink(missing_ok=True)

            raise StorageWriteError(
                f"Could not write storage file: {self._file_path}"
            ) from exc

    def _generate_next_id(
        self,
        prompt_runs: list[PromptRun],
    ) -> str:
        """
        Generate an ID using the highest existing numeric suffix.

        Deleting a record will therefore not cause an old ID to be reused.
        """

        highest_number = 0

        for prompt_run in prompt_runs:
            match = self._ID_PATTERN.fullmatch(prompt_run.id)

            if match is None:
                raise InvalidStorageDocumentError(
                    f'Existing prompt run has invalid ID: "{prompt_run.id}".'
                )

            current_number = int(match.group(1))
            highest_number = max(
                highest_number,
                current_number,
            )

        next_number = highest_number + 1

        return f"run_{next_number:03d}"
