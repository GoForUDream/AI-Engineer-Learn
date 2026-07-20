from __future__ import annotations

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.config import get_settings
from app.database import SessionFactory
from app.exceptions import (
    DatabaseOperationError,
    TodoNotFoundError,
)
from app.routers.todos import router as todos_router
from app.schemas import (
    ErrorDetail,
    ErrorField,
    ErrorResponse,
    HealthResponse,
)


logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    settings = get_settings()

    application = FastAPI(
        title=settings.app_name,
        version="2.0.0",
        debug=settings.app_debug,
        description=("Todo API backed by PostgreSQL, SQLAlchemy and Alembic."),
    )

    register_routes(application)
    register_exception_handlers(application)

    return application


def register_routes(
    application: FastAPI,
) -> None:
    @application.get(
        "/health",
        response_model=HealthResponse,
        tags=["health"],
    )
    def health_check() -> HealthResponse:
        try:
            with SessionFactory() as session:
                session.execute(text("SELECT 1"))

            return HealthResponse(status="ok")

        except SQLAlchemyError as exc:
            raise DatabaseOperationError(operation="health_check") from exc

    application.include_router(todos_router)


def register_exception_handlers(
    application: FastAPI,
) -> None:
    @application.exception_handler(TodoNotFoundError)
    async def handle_todo_not_found(
        request: Request,
        exc: TodoNotFoundError,
    ) -> JSONResponse:
        del request

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

    @application.exception_handler(DatabaseOperationError)
    async def handle_database_operation_error(
        request: Request,
        exc: DatabaseOperationError,
    ) -> JSONResponse:
        logger.exception(
            "Database operation failed",
            extra={
                "operation": exc.operation,
                "method": request.method,
                "path": request.url.path,
            },
        )

        response = ErrorResponse(
            error=ErrorDetail(
                code="database_operation_failed",
                message=(
                    "The requested operation could not be completed. "
                    "Please try again later."
                ),
            )
        )

        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=response.model_dump(mode="json"),
        )

    @application.exception_handler(RequestValidationError)
    async def handle_request_validation_error(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        del request

        fields = [
            ErrorField(
                location=[str(part) for part in error["loc"]],
                message=error["msg"],
                type=error["type"],
            )
            for error in exc.errors()
        ]

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

    @application.exception_handler(SQLAlchemyError)
    async def handle_raw_sqlalchemy_error(
        request: Request,
        exc: SQLAlchemyError,
    ) -> JSONResponse:
        logger.exception(
            "Unhandled SQLAlchemy error",
            extra={
                "method": request.method,
                "path": request.url.path,
            },
        )

        response = ErrorResponse(
            error=ErrorDetail(
                code="database_operation_failed",
                message=(
                    "The requested operation could not be completed. "
                    "Please try again later."
                ),
            )
        )

        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=response.model_dump(mode="json"),
        )


app = create_app()
