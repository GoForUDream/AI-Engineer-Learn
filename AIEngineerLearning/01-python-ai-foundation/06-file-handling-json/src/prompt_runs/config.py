from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StorageSettings:
    output_directory: Path = Path("outputs")
    file_name: str = "prompt_runs.json"

    @property
    def file_path(self) -> Path:
        return self.output_directory / self.file_name
