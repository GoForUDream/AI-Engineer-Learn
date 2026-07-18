# 01. FastAPI and REST APIs

Goal: Build a small, predictable HTTP API with FastAPI.

## Why This Matters

AI capabilities still need normal endpoints. A chat request, document ingestion job, or prompt evaluation starts as an HTTP contract between a client and a backend.

## Exercise

Build an in-memory Todo API. Do not add a database yet.

Each todo contains:

- `id`
- `title`
- `description`
- `completed`
- `created_at`

Support these endpoints:

```text
GET    /health
POST   /api/todos
GET    /api/todos
GET    /api/todos/{todo_id}
PATCH  /api/todos/{todo_id}
DELETE /api/todos/{todo_id}
```

## Build Steps

1. Create an `app/` package with `main.py`, `schemas.py`, and `routers/todos.py`.
2. Define separate Pydantic models for create, update, and response data.
3. Return `201` after creation and `204` after deletion.
4. Return a consistent JSON error when a todo does not exist.
5. Add pytest tests using FastAPI's test client.
6. Inspect the generated OpenAPI page at `/docs`.

## Rules

- Route functions should not contain every piece of business logic.
- A PATCH request must distinguish an omitted field from a supplied false or empty value.
- Do not expose a Python traceback as an API response.

## Done When

- Every endpoint has a success test.
- Missing and invalid resources return useful `4xx` responses.
- Request and response bodies are validated.
- You can explain why create, update, and response schemas are different.

## Reflection

- What makes an API resource-oriented?
- What is the difference between `400`, `404`, and `422`?
- Why should an API response shape remain stable?
