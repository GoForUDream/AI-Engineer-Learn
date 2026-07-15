# AI Engineer Learning Roadmap

This folder is the main learning track for becoming a full-stack developer who can build real applications with AI features using LangChain, LangGraph, RAG, tools, and production-ready APIs.

The goal is not only to call an LLM API. The goal is to build full-stack products where AI is part of the application architecture.

## Target Role

Become a developer who can:

- Build full-stack web applications.
- Design backend APIs for AI-powered features.
- Use LangChain and LangGraph to connect LLMs, prompts, tools, memory, and workflows.
- Build RAG systems with vector databases.
- Evaluate, debug, and improve AI outputs.
- Deploy full-stack AI applications with environment variables, Docker, databases, and observability.

## Recommended Folder Structure

Use this structure as the learning map. Each folder should contain notes, small exercises, and mini-projects.

```text
AIEngineerLearning/
  00-learning-log/
  01-python-ai-foundation/
  02-fullstack-foundation/
  03-llm-api-basics/
  04-langchain-core/
  05-rag-and-vector-databases/
  06-tools-agents-and-langgraph/
  07-fullstack-ai-integration/
  08-evaluation-observability/
  09-deployment-production/
  10-capstone-projects/
```

## Study Order

### 00. Learning Log

Purpose: Track what you learn and what you build.

Create:

- `daily-log.md`
- `concepts.md`
- `bugs-and-fixes.md`
- `project-ideas.md`

Done when:

- Every study session has a short note.
- Every bug you solve has a short explanation.
- Every mini-project has a short README.

### 01. Python AI Foundation

Purpose: Become comfortable writing Python for AI backend work.

Learn:

- Python project structure.
- Virtual environments.
- Environment variables with `.env`.
- HTTP requests.
- Pydantic models.
- Async basics.
- File handling.
- JSON and structured outputs.

Build:

- CLI chatbot.
- API key config loader.
- Weather API tool.
- JSON output validator.
- Small prompt runner.

Done when:

- You can write a Python script that calls an LLM, validates the response, and handles errors cleanly.

### 02. Full-Stack Foundation

Purpose: Build the normal application layer around AI features.

Recommended stack:

- Frontend: React, TypeScript, Vite.
- Backend: FastAPI or Node.js/NestJS.
- Database: PostgreSQL.
- Cache/queue: Redis later, not at the beginning.
- Local runtime: Docker Compose.

Learn:

- REST API design.
- Authentication basics.
- Database CRUD.
- File upload.
- Streaming responses.
- Frontend forms and chat UI.
- API error handling.

Build:

- Todo API.
- File upload API.
- Chat UI.
- User settings page for model/provider configuration.

Done when:

- You can build a frontend that talks to your backend, stores data, and displays loading/error states properly.

### 03. LLM API Basics

Purpose: Understand the raw model layer before adding LangChain.

Learn:

- Chat messages: system, user, assistant, tool.
- Temperature and model settings.
- Token usage.
- JSON mode and structured output.
- Streaming.
- Tool/function calling.
- Retry and timeout handling.

Build:

- Basic chatbot.
- Coding-only assistant.
- Structured JSON extractor.
- Tool-calling weather assistant.
- Streaming chat endpoint.

Done when:

- You can explain what messages are sent to the model and why the model responds the way it does.

### 04. LangChain Core

Purpose: Learn LangChain as an application composition framework.

Learn:

- Chat models.
- Prompt templates.
- Output parsers.
- Runnables.
- Chains.
- Document loaders.
- Text splitters.
- Retrievers.
- Model provider abstraction.

Build:

- Prompt template playground.
- Resume parser.
- Text summarizer.
- SQL-style question formatter.
- Chain with structured output.

Done when:

- You can build a LangChain pipeline without hiding all logic in one large function.

### 05. RAG and Vector Databases

Purpose: Build AI features that answer from your own documents.

Learn:

- Embeddings.
- Chunking strategy.
- Metadata.
- Vector search.
- Hybrid search basics.
- Reranking basics.
- Source citation.
- Qdrant or Chroma.

Build:

- PDF ingestion pipeline.
- Local Qdrant setup.
- Document chat CLI.
- Document chat API.
- Frontend document chat UI.

Done when:

- A user can upload a document, ask a question, get an answer, and see the source pages or chunks.

### 06. Tools, Agents, and LangGraph

Purpose: Build AI workflows that can make decisions and call tools.

Learn:

- Tool calling.
- Agent loops.
- LangGraph state.
- Nodes and edges.
- Conditional routing.
- Human-in-the-loop flows.
- Safe tool execution.
- Memory and checkpoints.

Build:

- Calculator tool without unsafe `eval`.
- Weather agent.
- Research assistant with search and summarization.
- Multi-step support agent.
- LangGraph workflow with approval before action.

Done when:

- You can draw the graph of your agent workflow and explain each node, state field, and route.

### 07. Full-Stack AI Integration

Purpose: Put AI features inside real applications.

Learn:

- Chat session persistence.
- Message history storage.
- Streaming from backend to frontend.
- User-specific document collections.
- Background jobs for ingestion.
- API rate limits.
- Frontend UX for AI responses.

Build:

- AI document assistant.
- AI coding helper dashboard.
- AI study planner.
- AI customer support chatbot.
- AI data extraction tool.

Done when:

- Your app feels like a product, not a script. It should have UI, backend, database, AI workflow, and error handling.

### 08. Evaluation and Observability

Purpose: Learn how to know whether your AI app is actually good.

Learn:

- Prompt versioning.
- Golden test datasets.
- Retrieval quality checks.
- Answer correctness checks.
- Hallucination checks.
- Logs and traces.
- Latency and cost tracking.

Build:

- Small evaluation dataset.
- RAG answer evaluator.
- Prompt comparison script.
- LangSmith or custom tracing experiment.

Done when:

- You can compare two prompts or retrieval strategies and decide which one is better using evidence.

### 09. Deployment and Production

Purpose: Run AI applications outside your local machine.

Learn:

- Docker.
- Docker Compose.
- Environment variables.
- Secret management.
- Database migrations.
- Background workers.
- Reverse proxy basics.
- Deployment logs.

Build:

- Dockerized full-stack AI app.
- Backend health check.
- Production-style `.env.example`.
- Simple deployment README.

Done when:

- Someone else can clone the repo, follow the README, configure secrets, and run the app.

### 10. Capstone Projects

Purpose: Prove the full skill set.

Build at least three:

- Personal document assistant with RAG.
- AI learning coach with memory and progress tracking.
- AI code-review assistant.
- AI customer support dashboard.
- AI research assistant with tools and citations.
- AI resume/job matching tool.

Each capstone should include:

- Frontend.
- Backend API.
- Database.
- LangChain or LangGraph workflow.
- RAG or tool calling.
- Evaluation notes.
- Deployment instructions.

## Main Learning Path

Follow this order:

```text
Python for AI
  -> Full-stack fundamentals
  -> Raw LLM APIs
  -> LangChain core
  -> RAG
  -> Tools and agents
  -> LangGraph workflows
  -> Full-stack AI product
  -> Evaluation
  -> Deployment
  -> Capstone projects
```

## Weekly Practice Pattern

For each topic:

1. Read or watch the lesson.
2. Rebuild the example from scratch.
3. Change the example into a slightly different use case.
4. Add a README explaining what it does.
5. Write down one bug and how you fixed it.
6. Commit the work.

## Definition of Progress

You are making real progress when you can:

- Build without copying every line from a tutorial.
- Explain the data flow from frontend to backend to LLM.
- Debug failed model calls and bad retrieval results.
- Replace a fake local script with an API endpoint.
- Turn a CLI AI demo into a usable web feature.
- Add tests or evaluation checks before changing prompts.

## First Milestone

Build a full-stack document Q&A app:

- React chat UI.
- FastAPI backend.
- PDF upload.
- Qdrant vector database.
- LangChain ingestion pipeline.
- LangChain retrieval chain.
- Source citations.
- Docker Compose for local development.

This should be the first serious project after the smaller exercises.
