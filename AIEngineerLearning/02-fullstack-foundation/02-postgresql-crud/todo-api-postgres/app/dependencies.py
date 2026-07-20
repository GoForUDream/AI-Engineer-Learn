from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db_session
from app.repositories.todos import TodoRepository
from app.services.todos import TodoService


DatabaseSession = Annotated[
    Session,
    Depends(get_db_session),
]


def get_todo_service(
    session: DatabaseSession,
) -> TodoService:
    repository = TodoRepository(session)

    return TodoService(
        session=session,
        repository=repository,
    )


TodoServiceDependency = Annotated[
    TodoService,
    Depends(get_todo_service),
]
