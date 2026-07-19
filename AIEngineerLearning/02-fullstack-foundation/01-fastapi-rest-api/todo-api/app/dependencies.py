from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request

from app.services import TodoService


def get_todo_service(request: Request) -> TodoService:
    service: TodoService = request.app.state.todo_service
    return service


TodoServiceDependency = Annotated[TodoService, Depends(get_todo_service)]
