from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.exceptions import TodoNotFoundError
from app.routers.todos import router as todos_router
from app.schemas import (
    ErrorDetail,
    ErrorResponse,
    HealthResponse,
)
from app.services import TodoService

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    application = FastAPI(
        title="In-Memory Todo API",
        version="1.0.0",
        description=(
            "A small Todo API demonstrating FastAPI, Pydantic validation, "
            "application services, error handling and automated tests."
        ),
        debug=False,
    )

    application.state.todo_service = TodoService()

    register_routes(application)
    register_exception_handlers(application)

    return application


def register_routes(application: FastAPI) -> None:
    @application.get(
        "/health",
        response_model=HealthResponse,
        tags=["health"],
        summary="Check API health",
    )
    def health_check() -> HealthResponse:
        return HealthResponse()

    application.include_router(todos_router)


def register_exception_handlers(
    application: FastAPI,
) -> None:
    @application.exception_handler(TodoNotFoundError)
    async def handle_todo_not_found(
        request: Request,
        exc: TodoNotFoundError,
    ) -> JSONResponse:
        response = ErrorResponse(
            error=ErrorDetail(
                code="todo_not_found",
                message=str(exc),
            )
        )

        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=response.model_dump(mode="json"),
        )

    @application.exception_handler(RequestValidationError)
    async def handle_request_validation_error(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        fields: list[dict[str, Any]] = []

        for error in exc.errors():
            fields.append(
                {
                    "location": [str(part) for part in error["loc"]],
                    "message": error["msg"],
                    "type": error["type"],
                }
            )

        response = ErrorResponse(
            error=ErrorDetail(
                code="validation_error",
                message="Request validation failed.",
                fields=fields,
            )
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=response.model_dump(mode="json"),
        )

    @application.exception_handler(Exception)
    async def handle_unexpected_error(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        logger.exception(
            "Unhandled application error",
            extra={
                "method": request.method,
                "path": request.url.path,
            },
        )

        response = ErrorResponse(
            error=ErrorDetail(
                code="internal_server_error",
                message="An unexpected error occurred.",
            )
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=response.model_dump(mode="json"),
        )


app = create_app()
