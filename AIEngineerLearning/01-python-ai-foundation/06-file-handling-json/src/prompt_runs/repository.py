from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Protocol

import portalocker
from pydantic import ValidationError

from .models import PromptRun, PromptRunDocument
from .exceptions import (
    PromptRunStorageError,
    InvalidPromptRunDocumentError,
)


class PromptRunRepository(Protocol):
    """
    Repository contract.

    The service layer depends on this abstraction rather than a concrete
    JSON implementation.
    """

    def append(self, prompt_run: PromptRun) -> PromptRunDocument:
        """Persist one record and return the updated document."""
        ...

    def read_all(self) -> PromptRunDocument:
        """Return all persisted records."""
        ...


class JsonPromptRunRepository:
    def __init__(self, file_path: Path, *, lock_timeout_seconds: float = 10.0) -> None:
        self._file_path = file_path
        self._lock_path = file_path.with_suffix(f"{file_path.suffix}.lock")
        self._lock_timeout_seconds = lock_timeout_seconds

    @property
    def file_path(self) -> Path:
        return self._file_path

    def initialize(self) -> None:
        self._file_path.parent.mkdir(parents=True, exist_ok=True)

        if self._file_path.exists():
            return

        try:
            with portalocker.Lock(
                self._lock_path,
                mode="a",
                timeout=self._lock_timeout_seconds,
            ):
                if not self._file_path.exists():
                    self._write_atomic(PromptRunDocument())
        except portalocker.exceptions.LockException as exc:
            raise PromptRunStorageError(
                f"Could not acquire storage lock: {self._lock_path}"
            ) from exc

    def read_all(self) -> PromptRunDocument:
        self.initialize()
        return self._read_document()

    def append(self, prompt_run: PromptRun) -> PromptRunDocument:
        self._file_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with portalocker.Lock(
                self._lock_path, mode="a", timeout=self._lock_timeout_seconds
            ):
                document = self._read_document_or_default()

                updated_document = PromptRunDocument(
                    version=document.version, records=[*document.records, prompt_run]
                )

                self._write_atomic(updated_document)

                return updated_document

        except portalocker.exceptions.LockException as exc:
            raise PromptRunStorageError(
                f"Could not acquire storage lock: {self._lock_path}"
            ) from exc

    def _read_document_or_default(self) -> PromptRunDocument:
        if not self._file_path.exists():
            return PromptRunDocument()

        return self._read_document()

    def _read_document(self) -> PromptRunDocument:
        try:
            raw_content = self._file_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise PromptRunStorageError(
                f"Could not read prompt-run file: {self._file_path}"
            ) from exc

        if not raw_content.strip():
            raise InvalidPromptRunDocumentError(
                f"Prompt-run file is empty: {self._file_path}"
            )

        try:
            raw_document = json.loads(raw_content)
        except json.JSONDecodeError as exc:
            raise InvalidPromptRunDocumentError(
                f"Prompt-run file contains invalid JSON: {self._file_path}"
            ) from exc

        try:
            return PromptRunDocument.model_validate(raw_document)
        except ValidationError as exc:
            raise InvalidPromptRunDocumentError(
                f"Prompt-run file has an invalid data structure: {self._file_path}"
            ) from exc

    def _write_atomic(self, document: PromptRunDocument) -> None:

        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        serialized_document = document.model_dump_json(indent=2)
        temporary_path: Path | None = None

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

                temporary_path = Path(temporary_file.name)

            os.replace(temporary_path, self._file_path)

        except OSError as exc:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)

            raise PromptRunStorageError(
                f"Could not write prompt-run file: {self._file_path}"
            ) from exc
