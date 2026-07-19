from __future__ import annotations

from uuid import UUID


class TodoError(Exception):
    """Base exception for todo-related application errors."""


class TodoNotFoundError(TodoError):
    def __init__(self, todo_id: UUID) -> None:
        self.todo_id = todo_id

        super().__init__(f'Todo with ID "{todo_id}" was not found.')
