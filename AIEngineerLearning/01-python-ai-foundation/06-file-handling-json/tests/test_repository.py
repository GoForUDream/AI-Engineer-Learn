from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.prompt_runs.exceptions import InvalidPromptRunDocumentError
from src.prompt_runs.repository import JsonPromptRunRepository
from src.prompt_runs.service import PromptRun


def test_append_preserves_existing_records(tmp_path: Path) -> None:
    file_path = tmp_path / "outputs" / "prompt_runs.json"
    repository = JsonPromptRunRepository(file_path)

    first_run = PromptRun(
        prompt="First prompt",
        response="First response",
        tags=["first"],
    )

    second_run = PromptRun(
        prompt="Second prompt",
        response="Second response",
        tags=["second"],
    )

    repository.append(first_run)
    repository.append(second_run)

    document = repository.read_all()

    assert len(document.records) == 2
    assert document.records[0].id == first_run.id
    assert document.records[1].id == second_run.id


def test_repository_creates_parent_directory(tmp_path: Path) -> None:
    file_path = tmp_path / "nested" / "outputs" / "prompt_runs.json"
    repository = JsonPromptRunRepository(file_path)

    repository.append(
        PromptRun(
            prompt="Prompt",
            response="Response",
        )
    )

    assert file_path.exists()
    assert file_path.parent.exists()


def test_file_remains_valid_json(tmp_path: Path) -> None:
    file_path = tmp_path / "prompt_runs.json"
    repository = JsonPromptRunRepository(file_path)

    repository.append(
        PromptRun(
            prompt="Prompt",
            response="Response",
        )
    )

    raw_document = json.loads(file_path.read_text(encoding="utf-8"))

    assert raw_document["version"] == 1
    assert isinstance(raw_document["records"], list)
    assert len(raw_document["records"]) == 1


def test_invalid_json_raises_domain_exception(tmp_path: Path) -> None:
    file_path = tmp_path / "prompt_runs.json"
    file_path.write_text("{invalid-json", encoding="utf-8")

    repository = JsonPromptRunRepository(file_path)

    with pytest.raises(InvalidPromptRunDocumentError):
        repository.read_all()


def test_tags_are_normalized(tmp_path: Path) -> None:
    repository = JsonPromptRunRepository(tmp_path / "prompt_runs.json")

    prompt_run = PromptRun(
        prompt="Prompt",
        response="Response",
        tags=[" Python ", "python", "", "AI"],
    )

    repository.append(prompt_run)

    document = repository.read_all()

    assert document.records[0].tags == ["python", "ai"]
