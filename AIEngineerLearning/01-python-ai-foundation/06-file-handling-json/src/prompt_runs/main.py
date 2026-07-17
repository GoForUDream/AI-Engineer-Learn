from __future__ import annotations

import logging
import sys

from .exceptions import PromptRunError
from .service import PromptRunService
from .config import StorageSettings
from .repository import JsonPromptRunRepository


logger = logging.getLogger(__name__)


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format=("%(asctime)s | %(levelname)s | %(name)s | %(message)s"),
    )


def build_service() -> PromptRunService:
    settings = StorageSettings()

    repository = JsonPromptRunRepository(
        file_path=settings.file_path,
    )

    return PromptRunService(repository)


def run_exercise(service: PromptRunService) -> None:
    first_run = service.record_run(
        prompt="Explain Python generators in simple terms.",
        response=(
            "A generator lazily produces values one at a time instead of "
            "building the entire result in memory."
        ),
        tags=["python", "generators", "learning"],
    )

    logger.info("Stored first prompt run: %s", first_run.id)

    document_after_first_write = service.list_runs()

    logger.info(
        "Record count after first write: %d",
        len(document_after_first_write.records),
    )

    second_run = service.record_run(
        prompt="What problem does Pydantic solve?",
        response=(
            "Pydantic validates and serializes data based on Python type annotations."
        ),
        tags=["python", "pydantic", "validation"],
    )

    logger.info("Stored second prompt run: %s", second_run.id)

    final_document = service.list_runs()

    print("\nFinal prompt-run document:")
    print(final_document.model_dump_json(indent=2))


def main() -> None:
    configure_logging()

    try:
        service = build_service()
        run_exercise(service)
    except PromptRunError:
        logger.exception("Prompt-run exercise failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
