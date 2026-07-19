from __future__ import annotations

from uuid import uuid4

from fastapi import status
from fastapi.testclient import TestClient


def create_todo(
    client: TestClient,
    *,
    title: str = "Learn FastAPI",
    description: str = "Build a Todo API",
) -> dict[str, object]:
    response = client.post(
        "/api/todos",
        json={
            "title": title,
            "description": description,
        },
    )

    assert response.status_code == status.HTTP_201_CREATED

    return response.json()


def test_health_check(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "status": "ok",
    }


def test_create_todo(client: TestClient) -> None:
    response = client.post(
        "/api/todos",
        json={
            "title": "Learn FastAPI",
            "description": "Build an in-memory API",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED

    body = response.json()

    assert body["title"] == "Learn FastAPI"
    assert body["description"] == "Build an in-memory API"
    assert body["completed"] is False
    assert body["id"]
    assert body["created_at"]


def test_create_todo_with_default_description(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/todos",
        json={
            "title": "Write tests",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["description"] == ""


def test_list_todos(client: TestClient) -> None:
    first_todo = create_todo(
        client,
        title="First todo",
    )

    second_todo = create_todo(
        client,
        title="Second todo",
    )

    response = client.get("/api/todos")

    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    assert len(body) == 2
    assert body[0]["id"] == first_todo["id"]
    assert body[1]["id"] == second_todo["id"]


def test_list_todos_returns_empty_list(
    client: TestClient,
) -> None:
    response = client.get("/api/todos")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_todo_by_id(client: TestClient) -> None:
    created_todo = create_todo(client)

    response = client.get(f"/api/todos/{created_todo['id']}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == created_todo


def test_get_missing_todo_returns_consistent_error(
    client: TestClient,
) -> None:
    missing_id = uuid4()

    response = client.get(f"/api/todos/{missing_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "error": {
            "code": "todo_not_found",
            "message": (f'Todo with ID "{missing_id}" was not found.'),
            "fields": None,
        }
    }


def test_get_todo_with_invalid_uuid_returns_422(
    client: TestClient,
) -> None:
    response = client.get("/api/todos/not-a-valid-uuid")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    body = response.json()

    assert body["error"]["code"] == "validation_error"
    assert body["error"]["message"] == ("Request validation failed.")
    assert body["error"]["fields"]


def test_patch_todo(client: TestClient) -> None:
    created_todo = create_todo(client)

    response = client.patch(
        f"/api/todos/{created_todo['id']}",
        json={
            "title": "Updated title",
            "completed": True,
        },
    )

    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    assert body["title"] == "Updated title"
    assert body["description"] == created_todo["description"]
    assert body["completed"] is True
    assert body["created_at"] == created_todo["created_at"]


def test_patch_can_set_completed_to_false(
    client: TestClient,
) -> None:
    created_todo = create_todo(client)

    complete_response = client.patch(
        f"/api/todos/{created_todo['id']}",
        json={
            "completed": True,
        },
    )

    assert complete_response.status_code == status.HTTP_200_OK
    assert complete_response.json()["completed"] is True

    incomplete_response = client.patch(
        f"/api/todos/{created_todo['id']}",
        json={
            "completed": False,
        },
    )

    assert incomplete_response.status_code == status.HTTP_200_OK
    assert incomplete_response.json()["completed"] is False


def test_patch_can_set_description_to_empty_string(
    client: TestClient,
) -> None:
    created_todo = create_todo(
        client,
        description="Description to remove",
    )

    response = client.patch(
        f"/api/todos/{created_todo['id']}",
        json={
            "description": "",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["description"] == ""


def test_empty_patch_keeps_existing_values(
    client: TestClient,
) -> None:
    created_todo = create_todo(client)

    response = client.patch(
        f"/api/todos/{created_todo['id']}",
        json={},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == created_todo


def test_patch_missing_todo_returns_404(
    client: TestClient,
) -> None:
    missing_id = uuid4()

    response = client.patch(
        f"/api/todos/{missing_id}",
        json={
            "completed": True,
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["error"]["code"] == "todo_not_found"


def test_delete_todo(client: TestClient) -> None:
    created_todo = create_todo(client)

    response = client.delete(f"/api/todos/{created_todo['id']}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.content == b""

    get_response = client.get(f"/api/todos/{created_todo['id']}")

    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_missing_todo_returns_404(
    client: TestClient,
) -> None:
    missing_id = uuid4()

    response = client.delete(f"/api/todos/{missing_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["error"]["code"] == "todo_not_found"


def test_create_rejects_empty_title(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/todos",
        json={
            "title": "",
            "description": "Invalid todo",
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["error"]["code"] == "validation_error"


def test_create_rejects_unknown_fields(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/todos",
        json={
            "title": "Valid title",
            "description": "",
            "unknown_field": "not allowed",
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["error"]["code"] == "validation_error"


def test_patch_rejects_null_title(
    client: TestClient,
) -> None:
    created_todo = create_todo(client)

    response = client.patch(
        f"/api/todos/{created_todo['id']}",
        json={
            "title": None,
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["error"]["code"] == "validation_error"
