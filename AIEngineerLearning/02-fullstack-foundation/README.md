# 02. Full-Stack Foundation

This block builds the normal application layer that AI features need: an API, a database, a browser UI, authentication, file uploads, and streaming.

Do not call an LLM in this block. Use predictable fake responses so you can focus on how the application works. LangChain will be added after the raw application flow is reliable.

## Recommended Stack

- Backend: FastAPI and Pydantic.
- Database: PostgreSQL.
- Database access: SQLAlchemy and Alembic.
- Frontend: React, TypeScript, and Vite.
- Local services: Docker Compose.
- Tests: pytest for the backend and Vitest/React Testing Library for the frontend.

Redis is intentionally postponed. Add it only when a later feature needs a queue, shared cache, or distributed coordination.

## What You Will Learn

- REST API design and HTTP status codes.
- PostgreSQL CRUD and database migrations.
- React components, state, forms, and routing.
- Frontend-to-backend API integration.
- Loading, empty, success, and error states.
- File upload validation and storage boundaries.
- Authentication basics and protected routes.
- Streaming a response from backend to frontend.
- Running a multi-service app with Docker Compose.

## Study Flow

Follow these folders in order:

```text
02-fullstack-foundation/
  01-fastapi-rest-api/
  02-postgresql-crud/
  03-react-typescript-vite/
  04-frontend-backend-integration/
  05-file-upload/
  06-authentication-basics/
  07-streaming-chat-ui/
  08-mini-project-ai-workspace/
```

## How To Study Each Topic

For every folder:

1. Read the topic README.
2. Build the smallest working version yourself.
3. Test the success path and at least two failure paths.
4. Inspect requests in the browser Network tab or API client.
5. Write the bug and fix in `../00-learning-logs/`.
6. Commit the working result.

## Local Prerequisites

Your machine currently has Python, Node.js, npm, Docker, and Docker Compose available.

Use a separate virtual environment for each backend project:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

Create React projects with the TypeScript Vite template:

```powershell
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
npm run dev
```

Never commit `.env`, database volumes, uploaded user files, `node_modules`, or frontend build output. Commit `.env.example` files instead.

## Required Outcome

By the end of this block, you should be able to build this without following a tutorial:

```text
A browser application that:
  - registers and signs in a user
  - sends validated requests to FastAPI
  - creates, reads, updates, and deletes PostgreSQL records
  - uploads a text file safely
  - streams a fake assistant response into a chat UI
  - displays useful loading, empty, and error states
  - starts its local services with Docker Compose
```

## Block Completion Checklist

- [ ] I can design predictable REST endpoints and status codes.
- [ ] I can create and apply a database migration.
- [ ] I can implement and test PostgreSQL CRUD.
- [ ] I can build typed React forms and reusable components.
- [ ] I can connect the frontend to FastAPI and handle failures.
- [ ] I can validate a file upload on the server.
- [ ] I can explain authentication versus authorization.
- [ ] I can protect backend routes and frontend pages.
- [ ] I can stream a backend response into the UI.
- [ ] I can run the final project locally with Docker Compose.

## Connection To AI Engineering

- REST endpoints become chat, ingestion, and evaluation APIs.
- PostgreSQL stores users, conversations, messages, and document metadata.
- File uploads become RAG ingestion inputs.
- Authentication separates each user's chats and documents.
- Streaming delivers model tokens as they are generated.
- Loading and error states make slow or unreliable AI calls understandable.
- Docker Compose later runs the API, database, vector store, and workers together.
