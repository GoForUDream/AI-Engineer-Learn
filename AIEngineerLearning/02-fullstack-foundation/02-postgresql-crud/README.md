# 02. PostgreSQL CRUD and Migrations

Goal: Replace in-memory storage with durable PostgreSQL data.

## Why This Matters

AI applications need durable records for users, conversations, messages, prompt versions, document metadata, and evaluations. Database migrations make schema changes repeatable across machines and deployments.

## Exercise

Move the Todo API from lesson 1 to PostgreSQL using SQLAlchemy. Manage schema changes with Alembic.

## Build Steps

1. Start PostgreSQL with a small `docker-compose.yml`.
2. Load `DATABASE_URL` from `.env` and document it in `.env.example`.
3. Create a SQLAlchemy `Todo` table model.
4. Create a database session dependency for FastAPI.
5. Implement create, list, get, update, and delete queries.
6. Generate and apply the first Alembic migration.
7. Add a second field through a new migration to practice schema evolution.
8. Run API tests against an isolated test database or transaction.

## Database Constraints

- Use a primary key.
- Make required columns non-nullable.
- Add timestamps deliberately rather than relying on client input.
- Decide which sorting order the list endpoint guarantees.
- Never build SQL by concatenating user strings.

## Done When

- Data survives an API restart.
- A new database can be created using migrations only.
- CRUD behavior is covered by tests.
- The API converts database failures into controlled responses.
- You can explain the difference between a Pydantic schema and a database model.

## Reflection

- Why are migrations safer than manually editing a production database?
- Where should a transaction begin and end?
- What is the N+1 query problem?
