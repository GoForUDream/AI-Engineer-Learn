# 08. Mini Project: AI Workspace Foundation

Goal: Combine the block into the product shell that later LangChain lessons can extend.

This project contains no real AI call yet. The fake chat response is a deliberate test double for the future model layer.

## Product Idea

Build a small authenticated workspace where a user can:

- Register, sign in, and sign out.
- Create and organize prompt templates.
- Upload text or Markdown context files.
- Select a provider name and model name in settings.
- Send a message to a fake streaming assistant.
- View useful loading and error states.

Do not store provider API keys in the database during this block.

## Required Structure

```text
08-mini-project-ai-workspace/
  backend/
    app/
      api/
      core/
      db/
      models/
      schemas/
      services/
      main.py
    migrations/
    tests/
    .env.example
    alembic.ini
    requirements.txt
  frontend/
    src/
      api/
      components/
      features/
      pages/
      types/
    tests/
    .env.example
    package.json
  docker-compose.yml
  README.md
```

## Core Data Model

- `User`: identity and password hash.
- `PromptTemplate`: name, content, tags, owner, timestamps.
- `UploadedFile`: original name, storage key, type, size, owner, timestamp.
- `UserSetting`: provider name and model name only.

Chat messages may remain in frontend memory for this block. Conversation persistence belongs to the later full-stack AI integration block.

## Build Order

1. Create the repository structure and health endpoint.
2. Start PostgreSQL with Docker Compose.
3. Add database settings, SQLAlchemy, and Alembic.
4. Add authentication and user ownership.
5. Add prompt-template CRUD.
6. Add safe text-file upload and deletion.
7. Create the React shell, routes, and API client.
8. Build authentication, prompt library, upload, and settings pages.
9. Add the fake streaming chat endpoint and chat UI.
10. Add backend and frontend tests for the critical workflows.
11. Document setup, migration, test, and run commands.

## Minimum API Surface

```text
GET    /health
POST   /api/auth/register
POST   /api/auth/login
POST   /api/auth/logout
GET    /api/auth/me
POST   /api/prompts
GET    /api/prompts
GET    /api/prompts/{prompt_id}
PATCH  /api/prompts/{prompt_id}
DELETE /api/prompts/{prompt_id}
POST   /api/files
GET    /api/files
DELETE /api/files/{file_id}
GET    /api/settings
PUT    /api/settings
POST   /api/chat/stream
```

## Definition Of Done

- A clean checkout can be configured from committed example environment files.
- PostgreSQL starts with Docker Compose and migrations create the schema.
- A user can register, sign in, and access protected pages.
- Prompt templates persist and are isolated by user.
- Text files can be uploaded, listed, and deleted safely.
- Settings persist provider and model names.
- The fake assistant response streams into the chat UI and can be cancelled.
- Loading, empty, validation, authorization, and server-error states are visible.
- Backend tests cover authentication, ownership, CRUD, upload validation, and streaming.
- Frontend tests cover one form, one failed API request, and streaming display.

## Final Reflection

Write a short architecture note answering:

- Where will LangChain enter this system later?
- Which data belongs in PostgreSQL, file/object storage, and a vector database?
- Which work should become a background job?
- What would need to change before deploying this publicly?
