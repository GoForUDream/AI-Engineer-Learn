from __future__ import annotations

import os

from dotenv import load_dotenv
from pathlib import Path
from dataclasses import dataclass

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE_PATH = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE_PATH)


@dataclass(frozen=True, slots=True)
class AppConfig:
    output_directory: Path
    storage_file_name: str
    lock_timeout_seconds: float

    @property
    def storage_file_path(self) -> Path:
        return self.output_directory / self.storage_file_name

    @classmethod
    def from_environment(cls) -> AppConfig:
        output_directory_value = os.getenv(
            "PROMPT_RUNNER_OUTPUT_DIRECTORY", str(PROJECT_ROOT / "outputs")
        )

        storage_file_name = os.getenv("PROMPT_RUNNER_STORAGE_FILE", "prompt_runs.json")

        lock_timeout_value = os.getenv("PROMPT_RUNNER_LOCK_TIMEOUT_SECONDS", "10")

        try:
            lock_timeout_seconds = float(lock_timeout_value)
        except ValueError as exc:
            raise ValueError(
                "PROMPT_RUNNER_LOCK_TIMEOUT_SECONDS must be a number."
            ) from exc

        if lock_timeout_seconds <= 0:
            raise ValueError(
                "PROMPT_RUNNER_LOCK_TIMEOUT_SECONDS must be greater than zero."
            )

        if not storage_file_name.strip():
            raise ValueError("PROMPT_RUNNER_STORAGE_FILE cannot be empty.")

        return cls(
            output_directory=Path(output_directory_value).expanduser(),
            storage_file_name=storage_file_name,
            lock_timeout_seconds=lock_timeout_seconds,
        )
