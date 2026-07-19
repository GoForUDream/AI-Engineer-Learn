from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Response, status

from app.dependencies import TodoServiceDependency
from app.schemas import (
    ErrorResponse,
    TodoCreate,
    TodoResponse,
    TodoUpdate,
)

router = APIRouter(
    prefix="/api/todos",
    tags=["todos"],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorResponse,
            "description": "Todo not found.",
        },
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": ErrorResponse,
            "description": "Request validation failed.",
        },
    },
)


@router.post(
    "",
    response_model=TodoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a todo",
)
def create_todo(payload: TodoCreate, service: TodoServiceDependency) -> TodoResponse:
    return service.create(payload)


@router.get(
    "",
    response_model=list[TodoResponse],
    summary="List todos",
)
def list_todo(service: TodoServiceDependency) -> list[TodoResponse]:
    return service.list_all()


@router.get("/{todo_id}", response_model=TodoResponse, summary="Get a todo")
def get_todo(todo_id: UUID, service: TodoServiceDependency) -> TodoResponse:
    return service.get_by_id(todo_id=todo_id)


@router.patch(
    "/{todo_id}", response_model=TodoResponse, summary="Partially update a todo"
)
def update_todo(
    todo_id: UUID, payload: TodoUpdate, service: TodoServiceDependency
) -> TodoResponse:
    return service.update(todo_id, payload)


@router.delete(
    "/{todo_id}", response_class=Response, status_code=status.HTTP_204_NO_CONTENT
)
def delete_todo(todo_id: UUID, service: TodoServiceDependency) -> Response:
    service.delete(todo_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
