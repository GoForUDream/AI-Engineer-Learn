from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.exceptions import DatabaseOperationError
from app.models import Todo


class TodoRepository:
    """SQLAlchemy persistence operations for todos."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, todo: Todo) -> Todo:
        try:
            self._session.add(todo)
            self._session.flush()
            self._session.refresh(todo)

            return todo

        except SQLAlchemyError as exc:
            raise DatabaseOperationError(operation="create_todo") from exc

    def list_all(self) -> list[Todo]:
        """
        Guaranteed sorting order:

        1. created_at ascending
        2. id ascending as a deterministic tie-breaker
        """

        statement = select(Todo).order_by(
            Todo.created_at.asc(),
            Todo.id.asc(),
        )

        try:
            result = self._session.scalars(statement)
            return list(result.all())

        except SQLAlchemyError as exc:
            raise DatabaseOperationError(operation="list_todos") from exc

    def get_by_id(
        self,
        todo_id: UUID,
    ) -> Todo | None:
        try:
            return self._session.get(Todo, todo_id)

        except SQLAlchemyError as exc:
            raise DatabaseOperationError(operation="get_todo") from exc

    def save(self, todo: Todo) -> Todo:
        try:
            self._session.flush()
            self._session.refresh(todo)

            return todo

        except SQLAlchemyError as exc:
            raise DatabaseOperationError(operation="update_todo") from exc

    def delete(self, todo: Todo) -> None:
        try:
            self._session.delete(todo)
            self._session.flush()

        except SQLAlchemyError as exc:
            raise DatabaseOperationError(operation="delete_todo") from exc
