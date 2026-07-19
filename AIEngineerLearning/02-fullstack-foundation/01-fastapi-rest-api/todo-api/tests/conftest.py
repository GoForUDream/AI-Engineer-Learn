from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """
    Create a new application for every test.

    Because each app owns a new TodoService, in-memory data cannot leak
    between tests.
    """

    application = create_app()

    with TestClient(application) as test_client:
        yield test_client
