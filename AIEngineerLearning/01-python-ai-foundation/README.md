# 01. Python AI Foundation

This block builds the Python base you need before deeper LangChain, RAG, and agent work.

The goal is not to learn every Python feature. The goal is to become comfortable writing clean Python scripts and small modules that can call APIs, read config, validate data, process files, and return structured outputs.

## What You Will Learn

- Python project structure.
- Virtual environments.
- Environment variables with `.env`.
- HTTP requests.
- Pydantic models.
- Async basics.
- File handling.
- JSON and structured outputs.

## Study Flow

Follow these folders in order:

```text
01-python-ai-foundation/
  01-project-structure/
  02-virtualenv-and-env/
  03-http-requests/
  04-pydantic-models/
  05-async-basics/
  06-file-handling-json/
  07-mini-project-prompt-runner/
```

## How To Study Each Topic

For every folder:

1. Read the topic README.
2. Build the smallest working version.
3. Break it on purpose once.
4. Fix it.
5. Write what you learned in `../00-learning-logs/`.
6. Commit the working result.

## Required Outcome

By the end of this block, you should be able to build this without a tutorial:

```text
A Python CLI app that:
  - loads config from .env
  - accepts user input
  - calls an HTTP API
  - validates the response with Pydantic
  - saves input and output to JSON
  - handles errors clearly
  - optionally runs multiple requests asynchronously
```

## Suggested Setup

Use one virtual environment for this block:

```powershell
cd C:\Users\VNGkh\repository\AI-Engineer-Learn\AIEngineerLearning\01-python-ai-foundation
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install requests python-dotenv pydantic httpx
```

Create `.env` locally when needed. Do not commit `.env`.

Use `.env.example` to document required variables:

```text
GEMINI_API_KEY=your_key_here
WEATHER_API_BASE_URL=https://wttr.in
```

## Main Exercises

### Exercise 1: Project Structure

Create a small Python project with:

```text
src/
  app/
    __init__.py
    main.py
    config.py
tests/
README.md
requirements.txt
```

Done when:

- You can run `python -m app.main` from the project root.
- Imports work without copy-pasting code between files.

### Exercise 2: Virtual Environment and `.env`

Create a config loader that reads:

- `GEMINI_API_KEY`
- `APP_ENV`
- `LOG_LEVEL`

Done when:

- Missing required values produce a clear error.
- `.env.example` shows what the app needs.
- `.env` remains ignored by Git.

### Exercise 3: HTTP Requests

Call a simple public API with `requests`.

Recommended API:

```text
https://wttr.in/saigon?format=j1
```

Done when:

- You handle success.
- You handle timeout.
- You handle non-200 responses.
- You print only useful data, not the full raw response.

### Exercise 4: Pydantic Models

Use Pydantic to model the response data you care about.

Done when:

- Raw JSON becomes a typed Python object.
- Bad data returns a validation error you can understand.
- You can convert the model back to JSON.

### Exercise 5: Async Basics

Use `httpx.AsyncClient` to call multiple URLs concurrently.

Done when:

- You can fetch weather for 3 cities at the same time.
- You understand the difference between sequential and concurrent requests.
- Errors from one city do not crash the whole program.

### Exercise 6: File Handling and JSON

Save structured results to disk.

Done when:

- You can write a JSON file.
- You can read it back.
- You can append a new record to a list.
- Your script creates the output folder if it does not exist.

### Exercise 7: Mini Project - Prompt Runner

Build a small CLI app that stores prompt experiments.

Input:

- Prompt name.
- Prompt text.
- Model response or fake response.
- Tags.

Output:

- `outputs/prompt_runs.json`

Each record should include:

- `id`
- `created_at`
- `prompt_name`
- `prompt_text`
- `response_text`
- `tags`

Done when:

- You can add a new prompt run from the CLI.
- The record is validated with Pydantic.
- The record is saved to JSON.
- You can list previous prompt runs.

## Block Completion Checklist

- [ ] I can explain a basic Python project structure.
- [ ] I can create and use a virtual environment.
- [ ] I can load environment variables safely.
- [ ] I can call an HTTP API and handle errors.
- [ ] I can validate data with Pydantic.
- [ ] I can write a simple async program.
- [ ] I can read and write JSON files.
- [ ] I can build the prompt runner mini project.

## Notes For AI Engineering

These skills map directly into later AI work:

- Project structure becomes LangChain app structure.
- `.env` becomes model/provider configuration.
- HTTP requests become external tools.
- Pydantic becomes structured model output validation.
- Async becomes streaming and concurrent agent/tool calls.
- File handling becomes document ingestion.
- JSON becomes evaluation data, logs, and model output contracts.
