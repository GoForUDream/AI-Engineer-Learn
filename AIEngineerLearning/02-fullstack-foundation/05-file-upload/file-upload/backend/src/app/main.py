from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.errors import ApplicationError
from app.files.dependencies import get_file_storage
from app.files.router import router as files_router

from .config import get_settings


@asynccontextmanager
async def lifespan(
    application: FastAPI,
) -> AsyncIterator[None]:
    storage = get_file_storage()
    await storage.initialize()

    yield


def create_application() -> FastAPI:
    settings = get_settings()

    application = FastAPI(
        title="Text file upload API",
        version="1.0.0",
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["Content-Type"],
    )

    application.include_router(
        files_router,
        prefix="/api",
    )

    @application.exception_handler(ApplicationError)
    async def handle_application_error(
        request: Request,
        error: ApplicationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=error.status_code,
            content={
                "code": error.code,
                "message": error.message,
            },
        )

    return application


app = create_application()
