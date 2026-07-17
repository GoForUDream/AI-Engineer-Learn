from __future__ import annotations
from collections.abc import Sequence

from .repository import PromptRunRepository, PromptRun, PromptRunDocument


class PromptRunService:
    """
    Application service containing prompt-run use cases.

    This layer does not know whether records are stored in JSON, PostgreSQL,
    Redis, or another persistence system.
    """

    def __init__(self, repository: PromptRunRepository) -> None:
        self._repository = repository

    def record_run(
        self, *, prompt: str, response: str, tags: Sequence[str] = ()
    ) -> PromptRun:
        prompt_run = PromptRun(prompt=prompt, response=response, tags=list(tags))

        self._repository.append(prompt_run)

        return prompt_run

    def list_runs(self) -> PromptRunDocument:
        return self._repository.read_all()
