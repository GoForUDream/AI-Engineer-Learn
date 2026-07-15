# 07. Mini Project: Prompt Runner

Goal: Combine the whole block into one small AI-engineering style project.

## Product Idea

Build a CLI app for saving prompt experiments.

The app should let you:

- Add a prompt run.
- List previous prompt runs.
- View one prompt run by ID.
- Save all data as JSON.
- Validate input with Pydantic.

## Required Structure

```text
07-mini-project-prompt-runner/
  src/
    prompt_runner/
      __init__.py
      main.py
      models.py
      storage.py
      config.py
  outputs/
  .env.example
  README.md
  requirements.txt
```

## Commands To Support

```powershell
python -m prompt_runner.main add
python -m prompt_runner.main list
python -m prompt_runner.main view <id>
```

## Data Model

Each prompt run should include:

```json
{
  "id": "run_001",
  "created_at": "2026-07-15T10:00:00Z",
  "prompt_name": "summarizer-test",
  "prompt_text": "Summarize this text in 3 bullets.",
  "response_text": "Fake or real model response.",
  "tags": ["summary", "test"]
}
```

## Build Order

1. Create the project structure.
2. Create the Pydantic model.
3. Create JSON read/write helpers.
4. Add the `add` command.
5. Add the `list` command.
6. Add the `view` command.
7. Improve error messages.
8. Add a short README explaining how to run it.

## Done When

- You can add prompt runs.
- You can list prompt runs.
- You can view a specific prompt run.
- Data persists in `outputs/prompt_runs.json`.
- Invalid data fails with a clear error.

## Upgrade Ideas

After finishing the base version:

- Add a real LLM call.
- Add `.env` config for model provider.
- Add a `score` field for evaluation.
- Add search by tag.
- Export runs to Markdown.
