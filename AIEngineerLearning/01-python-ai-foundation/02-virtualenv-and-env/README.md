# 02. Virtual Environments and `.env`

Goal: Learn how to isolate dependencies and load secrets/config safely.

## Why This Matters

AI apps usually need API keys. Those keys should not be hardcoded and should never be committed to Git.

You should use:

- `.venv` for local dependencies.
- `.env` for local secret values.
- `.env.example` for documenting required config.

## Exercise

Create a config module that loads:

- `GEMINI_API_KEY`
- `APP_ENV`
- `LOG_LEVEL`

## Build Steps

1. Create a virtual environment.
2. Install `python-dotenv`.
3. Create `.env` from `.env.example`.
4. Create `config.py`.
5. Load values from environment variables.
6. Raise a clear error if `GEMINI_API_KEY` is missing.

Commands:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install python-dotenv
```

## Done When

- `.env.example` is committed.
- `.env` is not committed.
- Missing config gives a helpful error.
- You can print non-secret config like `APP_ENV`.

## Reflection

Write answers in your learning log:

- Why should API keys not be stored in code?
- What is the difference between `.env` and `.env.example`?
- Why do Python projects use virtual environments?
