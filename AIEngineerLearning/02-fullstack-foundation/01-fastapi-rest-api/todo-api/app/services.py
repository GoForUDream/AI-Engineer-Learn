from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from threading import RLock
from uuid import UUID, uuid4

from app.exceptions import TodoNotFoundError
from app.schemas import TodoCreate, TodoResponse, TodoUpdate


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""

    return datetime.now(timezone.utc)


@dataclass(frozen=True, slots=True)
class Todo:
    """
    Internal domain entity.

    It is intentionally separate from the API response schema.
    """

    id: UUID
    title: str
    description: str
    completed: bool
    created_at: datetime


class TodoService:
    def __init__(self) -> None:
        self._todos: dict[UUID, Todo] = {}
        self._lock = RLock()

    def create(self, payload: TodoCreate) -> TodoResponse:
        todo = Todo(
            id=uuid4(),
            title=payload.title,
            description=payload.description,
            completed=False,
            created_at=utc_now(),
        )

        with self._lock:
            self._todos[todo.id] = todo

        return self._to_response(todo)

    def list_all(self) -> list[TodoResponse]:
        with self._lock:
            todos = list(self._todos.values())

        ordered_todos = sorted(
            todos,
            key=lambda todo: todo.created_at,
        )

        return [self._to_response(todo) for todo in ordered_todos]

    def get_by_id(self, todo_id: UUID) -> TodoResponse:
        with self._lock:
            todo = self._todos.get(todo_id)

        if todo is None:
            raise TodoNotFoundError(todo_id)

        return self._to_response(todo)

    def update(
        self,
        todo_id: UUID,
        payload: TodoUpdate,
    ) -> TodoResponse:
        changes = payload.model_dump(exclude_unset=True)

        with self._lock:
            existing_todo = self._todos.get(todo_id)

            if existing_todo is None:
                raise TodoNotFoundError(todo_id)

            updated_todo = replace(
                existing_todo,
                **changes,
            )

            self._todos[todo_id] = updated_todo

        return self._to_response(updated_todo)

    def delete(self, todo_id: UUID) -> None:
        with self._lock:
            if todo_id not in self._todos:
                raise TodoNotFoundError(todo_id)

            del self._todos[todo_id]

    def clear(self) -> None:
        with self._lock:
            self._todos.clear()

    @staticmethod
    def _to_response(todo: Todo) -> TodoResponse:
        return TodoResponse.model_validate(todo)
