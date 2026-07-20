from __future__ import annotations

from uuid import UUID


class ApplicationError(Exception):
    """Base class for controlled application errors."""


class TodoNotFoundError(ApplicationError):
    """Raised when a todo cannot be found."""

    def __init__(self, todo_id: UUID) -> None:
        self.todo_id = todo_id

        super().__init__(f'Todo with ID "{todo_id}" was not found.')


class DatabaseOperationError(ApplicationError):
    """
    Raised when a database operation fails unexpectedly.

    Internal database details must not be returned to clients.
    """

    def __init__(self, operation: str) -> None:
        self.operation = operation

        super().__init__("The database operation could not be completed.")
