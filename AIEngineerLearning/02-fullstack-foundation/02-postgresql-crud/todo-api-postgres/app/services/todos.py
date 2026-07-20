from __future__ import annotations

from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.exceptions import (
    DatabaseOperationError,
    TodoNotFoundError,
)
from app.models import Todo
from app.repositories.todos import TodoRepository
from app.schemas import (
    TodoCreate,
    TodoResponse,
    TodoUpdate,
)


class TodoService:
    """Todo application use cases."""

    def __init__(
        self,
        *,
        session: Session,
        repository: TodoRepository,
    ) -> None:
        self._session = session
        self._repository = repository

    def create(
        self,
        payload: TodoCreate,
    ) -> TodoResponse:
        todo = Todo(
            title=payload.title,
            description=payload.description,
            completed=False,
            due_at=payload.due_at,
        )

        try:
            created_todo = self._repository.create(todo)

            self._session.commit()
            self._session.refresh(created_todo)

            return TodoResponse.model_validate(created_todo)

        except DatabaseOperationError:
            self._session.rollback()
            raise

        except SQLAlchemyError as exc:
            self._session.rollback()

            raise DatabaseOperationError(operation="create_todo") from exc

    def list_all(self) -> list[TodoResponse]:
        todos = self._repository.list_all()

        return [TodoResponse.model_validate(todo) for todo in todos]

    def get_by_id(
        self,
        todo_id: UUID,
    ) -> TodoResponse:
        todo = self._get_existing(todo_id)

        return TodoResponse.model_validate(todo)

    def update(
        self,
        todo_id: UUID,
        payload: TodoUpdate,
    ) -> TodoResponse:
        todo = self._get_existing(todo_id)

        changes = payload.model_dump(exclude_unset=True)

        for field_name, value in changes.items():
            setattr(todo, field_name, value)

        try:
            updated_todo = self._repository.save(todo)

            self._session.commit()
            self._session.refresh(updated_todo)

            return TodoResponse.model_validate(updated_todo)

        except DatabaseOperationError:
            self._session.rollback()
            raise

        except SQLAlchemyError as exc:
            self._session.rollback()

            raise DatabaseOperationError(operation="update_todo") from exc

    def delete(
        self,
        todo_id: UUID,
    ) -> None:
        todo = self._get_existing(todo_id)

        try:
            self._repository.delete(todo)
            self._session.commit()

        except DatabaseOperationError:
            self._session.rollback()
            raise

        except SQLAlchemyError as exc:
            self._session.rollback()

            raise DatabaseOperationError(operation="delete_todo") from exc

    def _get_existing(
        self,
        todo_id: UUID,
    ) -> Todo:
        todo = self._repository.get_by_id(todo_id)

        if todo is None:
            raise TodoNotFoundError(todo_id)

        return todo
