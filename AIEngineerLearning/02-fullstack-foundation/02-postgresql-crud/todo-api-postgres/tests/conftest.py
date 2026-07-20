from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db_session
from app.main import create_app


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def require_test_database_url() -> str:
    database_url = os.getenv("TEST_DATABASE_URL")

    if not database_url:
        raise RuntimeError("TEST_DATABASE_URL is required.")

    if "todo_test" not in database_url:
        raise RuntimeError(
            "Refusing to run tests against a database "
            "that does not appear to be a test database."
        )

    return database_url


@pytest.fixture(scope="session")
def test_database_url() -> str:
    return require_test_database_url()


@pytest.fixture(scope="session")
def test_engine(
    test_database_url: str,
) -> Generator[Engine, None, None]:
    engine = create_engine(
        test_database_url,
        pool_pre_ping=True,
    )

    yield engine

    engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def migrate_test_database(
    test_database_url: str,
) -> Generator[None, None, None]:
    """
    Build the test database using Alembic migrations only.
    """

    previous_database_url = os.environ.get("DATABASE_URL")

    os.environ["DATABASE_URL"] = test_database_url

    get_settings.cache_clear()

    alembic_config = Config(str(PROJECT_ROOT / "alembic.ini"))

    alembic_config.set_main_option(
        "sqlalchemy.url",
        test_database_url,
    )

    command.upgrade(
        alembic_config,
        "head",
    )

    try:
        yield
    finally:
        command.downgrade(
            alembic_config,
            "base",
        )

        if previous_database_url is None:
            os.environ.pop(
                "DATABASE_URL",
                None,
            )
        else:
            os.environ["DATABASE_URL"] = previous_database_url

        get_settings.cache_clear()


@pytest.fixture
def database_connection(
    test_engine: Engine,
) -> Generator[Connection, None, None]:
    connection = test_engine.connect()
    transaction = connection.begin()

    try:
        yield connection
    finally:
        if transaction.is_active:
            transaction.rollback()

        connection.close()


@pytest.fixture
def database_session(
    database_connection: Connection,
) -> Generator[Session, None, None]:
    session = Session(
        bind=database_connection,
        autoflush=False,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )

    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(
    database_session: Session,
) -> Generator[TestClient, None, None]:
    application = create_app()

    def override_db_session() -> Generator[Session, None, None]:
        yield database_session

    application.dependency_overrides[get_db_session] = override_db_session

    with TestClient(
        application,
        raise_server_exceptions=False,
    ) as test_client:
        yield test_client

    application.dependency_overrides.clear()
