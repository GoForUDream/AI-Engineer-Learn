from __future__ import annotations

from uuid import uuid4

from fastapi import status
from fastapi.testclient import TestClient

from collections.abc import Generator

from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.database import get_db_session
from app.main import create_app


def test_database_failure_returns_controlled_response() -> None:
    application = create_app()

    def broken_session_dependency() -> Generator[Session, None, None]:
        raise OperationalError(
            statement="SELECT 1",
            params={},
            orig=RuntimeError("database unavailable"),
        )

        yield  # pragma: no cover

    application.dependency_overrides[get_db_session] = broken_session_dependency

    with TestClient(
        application,
        raise_server_exceptions=False,
    ) as client:
        response = client.get("/api/todos")

    assert response.status_code == (status.HTTP_503_SERVICE_UNAVAILABLE)

    assert response.json()["error"]["code"] == ("database_operation_failed")


def create_todo(
    client: TestClient,
    *,
    title: str = "Learn SQLAlchemy",
    description: str = "Move Todo API to PostgreSQL",
    due_at: str | None = None,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "title": title,
        "description": description,
    }

    if due_at is not None:
        payload["due_at"] = due_at

    response = client.post(
        "/api/todos",
        json=payload,
    )

    assert response.status_code == (status.HTTP_201_CREATED)

    return response.json()


def test_health_check(
    client: TestClient,
) -> None:
    response = client.get("/health")

    assert response.status_code == (status.HTTP_200_OK)

    assert response.json() == {
        "status": "ok",
    }


def test_create_todo(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/todos",
        json={
            "title": "Learn Alembic",
            "description": "Practice migrations",
            "due_at": "2026-08-01T10:00:00Z",
        },
    )

    assert response.status_code == (status.HTTP_201_CREATED)

    body = response.json()

    assert body["title"] == "Learn Alembic"
    assert body["description"] == "Practice migrations"
    assert body["completed"] is False
    assert body["due_at"] == "2026-08-01T10:00:00Z"
    assert body["id"]
    assert body["created_at"]
    assert body["updated_at"]


def test_create_rejects_client_managed_fields(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/todos",
        json={
            "title": "Invalid input",
            "completed": True,
            "created_at": "2026-08-01T10:00:00Z",
        },
    )

    assert response.status_code == (status.HTTP_422_UNPROCESSABLE_ENTITY)

    assert response.json()["error"]["code"] == ("validation_error")


def test_list_todos_returns_empty_list(
    client: TestClient,
) -> None:
    response = client.get("/api/todos")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_list_todos_guarantees_creation_order(
    client: TestClient,
) -> None:
    first = create_todo(
        client,
        title="First",
    )

    second = create_todo(
        client,
        title="Second",
    )

    response = client.get("/api/todos")

    assert response.status_code == status.HTTP_200_OK

    ids = [todo["id"] for todo in response.json()]

    assert ids == [
        first["id"],
        second["id"],
    ]


def test_get_todo(
    client: TestClient,
) -> None:
    created = create_todo(client)

    response = client.get(f"/api/todos/{created['id']}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == created


def test_get_missing_todo_returns_404(
    client: TestClient,
) -> None:
    todo_id = uuid4()

    response = client.get(f"/api/todos/{todo_id}")

    assert response.status_code == (status.HTTP_404_NOT_FOUND)

    assert response.json() == {
        "error": {
            "code": "todo_not_found",
            "message": (f'Todo with ID "{todo_id}" was not found.'),
            "fields": None,
        }
    }


def test_invalid_uuid_returns_422(
    client: TestClient,
) -> None:
    response = client.get("/api/todos/not-a-uuid")

    assert response.status_code == (status.HTTP_422_UNPROCESSABLE_ENTITY)

    assert response.json()["error"]["code"] == ("validation_error")


def test_update_todo(
    client: TestClient,
) -> None:
    created = create_todo(client)

    response = client.patch(
        f"/api/todos/{created['id']}",
        json={
            "title": "Updated title",
            "completed": True,
            "due_at": "2026-09-01T12:00:00Z",
        },
    )

    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    assert body["title"] == "Updated title"
    assert body["completed"] is True
    assert body["description"] == created["description"]
    assert body["due_at"] == "2026-09-01T12:00:00Z"
    assert body["created_at"] == created["created_at"]


def test_patch_distinguishes_false_from_omitted(
    client: TestClient,
) -> None:
    created = create_todo(client)

    response = client.patch(
        f"/api/todos/{created['id']}",
        json={
            "completed": True,
        },
    )

    assert response.json()["completed"] is True

    response = client.patch(
        f"/api/todos/{created['id']}",
        json={
            "completed": False,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["completed"] is False


def test_patch_allows_empty_description(
    client: TestClient,
) -> None:
    created = create_todo(
        client,
        description="Remove me",
    )

    response = client.patch(
        f"/api/todos/{created['id']}",
        json={
            "description": "",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["description"] == ""


def test_patch_allows_clearing_due_at(
    client: TestClient,
) -> None:
    created = create_todo(
        client,
        due_at="2026-09-01T12:00:00Z",
    )

    response = client.patch(
        f"/api/todos/{created['id']}",
        json={
            "due_at": None,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["due_at"] is None


def test_empty_patch_keeps_existing_values(
    client: TestClient,
) -> None:
    created = create_todo(client)

    response = client.patch(
        f"/api/todos/{created['id']}",
        json={},
    )

    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    assert body["id"] == created["id"]
    assert body["title"] == created["title"]
    assert body["description"] == created["description"]
    assert body["completed"] == created["completed"]


def test_patch_missing_todo_returns_404(
    client: TestClient,
) -> None:
    response = client.patch(
        f"/api/todos/{uuid4()}",
        json={
            "completed": True,
        },
    )

    assert response.status_code == (status.HTTP_404_NOT_FOUND)


def test_patch_rejects_null_title(
    client: TestClient,
) -> None:
    created = create_todo(client)

    response = client.patch(
        f"/api/todos/{created['id']}",
        json={
            "title": None,
        },
    )

    assert response.status_code == (status.HTTP_422_UNPROCESSABLE_ENTITY)


def test_delete_todo(
    client: TestClient,
) -> None:
    created = create_todo(client)

    response = client.delete(f"/api/todos/{created['id']}")

    assert response.status_code == (status.HTTP_204_NO_CONTENT)

    assert response.content == b""

    get_response = client.get(f"/api/todos/{created['id']}")

    assert get_response.status_code == (status.HTTP_404_NOT_FOUND)


def test_delete_missing_todo_returns_404(
    client: TestClient,
) -> None:
    response = client.delete(f"/api/todos/{uuid4()}")

    assert response.status_code == (status.HTTP_404_NOT_FOUND)
