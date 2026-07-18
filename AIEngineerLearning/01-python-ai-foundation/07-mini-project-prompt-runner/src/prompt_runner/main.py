from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Sequence

from pydantic import ValidationError

from prompt_runner.config import AppConfig
from prompt_runner.models import (
    PromptRun,
    PromptRunCreate,
)
from prompt_runner.storage import (
    JsonPromptRunStorage,
    PromptRunnerStorageError,
)

logger = logging.getLogger(__name__)


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format=("%(asctime)s | %(levelname)s | %(name)s | %(message)s"),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="prompt-runner",
        description="Save and inspect prompt experiment runs.",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    add_parser = subparsers.add_parser(
        "add",
        help="Add a new prompt run.",
        description=(
            "Add a new prompt run. Missing values will be requested interactively."
        ),
    )

    add_parser.add_argument(
        "--name",
        dest="prompt_name",
        help=("Prompt name in lowercase kebab-case, for example: summarizer-test."),
    )

    add_parser.add_argument(
        "--prompt",
        dest="prompt_text",
        help="The prompt text sent to the model.",
    )

    add_parser.add_argument(
        "--response",
        dest="response_text",
        help="The response returned by the model.",
    )

    add_parser.add_argument(
        "--tags",
        default=None,
        help="Comma-separated tags, for example: summary,test.",
    )

    subparsers.add_parser(
        "list",
        help="List all saved prompt runs.",
        description="List all previously saved prompt runs.",
    )

    view_parser = subparsers.add_parser(
        "view",
        help="View one prompt run by ID.",
        description="Display the complete JSON for one prompt run.",
    )

    view_parser.add_argument(
        "id",
        help="Prompt run ID, for example: run_001.",
    )

    return parser


def build_storage() -> JsonPromptRunStorage:
    config = AppConfig.from_environment()

    return JsonPromptRunStorage(
        file_path=config.storage_file_path,
        lock_timeout_seconds=config.lock_timeout_seconds,
    )


def request_required_value(
    provided_value: str | None,
    *,
    label: str,
) -> str:
    """
    Return a CLI-provided value or request it interactively.

    Empty interactive values are rejected immediately.
    """

    if provided_value is not None:
        return provided_value

    value = input(f"{label}: ").strip()

    if not value:
        raise ValueError(f"{label} cannot be empty.")

    return value


def parse_tags(raw_tags: str | None) -> list[str]:
    if raw_tags is None:
        raw_tags = input("Tags, separated by commas (optional): ")

    if not raw_tags.strip():
        return []

    return [tag.strip() for tag in raw_tags.split(",") if tag.strip()]


def handle_add(
    storage: JsonPromptRunStorage,
    args: argparse.Namespace,
) -> None:
    prompt_run_input = PromptRunCreate(
        prompt_name=request_required_value(
            args.prompt_name,
            label="Prompt name",
        ),
        prompt_text=request_required_value(
            args.prompt_text,
            label="Prompt text",
        ),
        response_text=request_required_value(
            args.response_text,
            label="Response text",
        ),
        tags=parse_tags(args.tags),
    )

    prompt_run = storage.add(prompt_run_input)

    print("Prompt run created successfully.")
    print(prompt_run.model_dump_json(indent=2))


def handle_list(
    storage: JsonPromptRunStorage,
) -> None:
    prompt_runs = storage.list_all()

    if not prompt_runs:
        print("No prompt runs have been saved yet.")
        return

    id_width = max(
        len("ID"),
        *(len(prompt_run.id) for prompt_run in prompt_runs),
    )

    name_width = max(
        len("PROMPT NAME"),
        *(len(prompt_run.prompt_name) for prompt_run in prompt_runs),
    )

    created_at_width = len("CREATED AT")

    header = (
        f"{'ID':<{id_width}}  "
        f"{'PROMPT NAME':<{name_width}}  "
        f"{'CREATED AT':<{created_at_width}}  "
        f"TAGS"
    )

    print(header)
    print("-" * len(header))

    for prompt_run in prompt_runs:
        created_at = prompt_run.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")

        tags = ", ".join(prompt_run.tags) or "-"

        print(
            f"{prompt_run.id:<{id_width}}  "
            f"{prompt_run.prompt_name:<{name_width}}  "
            f"{created_at:<{created_at_width}}  "
            f"{tags}"
        )


def handle_view(
    storage: JsonPromptRunStorage,
    prompt_run_id: str,
) -> None:
    prompt_run: PromptRun = storage.get_by_id(prompt_run_id)

    print(prompt_run.model_dump_json(indent=2))


def run(
    arguments: Sequence[str] | None = None,
) -> int:
    parser = build_parser()
    args = parser.parse_args(arguments)

    try:
        storage = build_storage()

        match args.command:
            case "add":
                handle_add(storage, args)

            case "list":
                handle_list(storage)

            case "view":
                handle_view(storage, args.id)

            case _:
                parser.error(f"Unsupported command: {args.command}")

    except ValidationError as exc:
        print(
            "Invalid prompt run data:",
            file=sys.stderr,
        )

        for error in exc.errors():
            location = ".".join(str(part) for part in error["loc"])

            message = error["msg"]

            print(
                f"  - {location}: {message}",
                file=sys.stderr,
            )

        return 2

    except ValueError as exc:
        print(
            f"Configuration or input error: {exc}",
            file=sys.stderr,
        )
        return 2

    except PromptRunnerStorageError as exc:
        print(
            f"Storage error: {exc}",
            file=sys.stderr,
        )
        return 1

    except KeyboardInterrupt:
        print(
            "\nOperation cancelled.",
            file=sys.stderr,
        )
        return 130

    except EOFError:
        print(
            "\nInput stream closed unexpectedly.",
            file=sys.stderr,
        )
        return 1

    return 0


def main() -> None:
    configure_logging()
    raise SystemExit(run())


if __name__ == "__main__":
    main()
