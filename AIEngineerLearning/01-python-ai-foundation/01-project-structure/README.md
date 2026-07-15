# 01. Project Structure

Goal: Learn how to organize Python code so your AI projects do not become one giant script.

## Why This Matters

AI apps quickly need many parts:

- Config loading.
- Model client setup.
- Prompt logic.
- Tool functions.
- File processing.
- API routes.
- Tests.

If everything lives in one file, the project becomes hard to debug and reuse.

## Exercise

Create this structure:

```text
01-project-structure/
  src/
    app/
      __init__.py
      main.py
      config.py
      services/
        __init__.py
        greeting_service.py
  tests/
    test_greeting_service.py
  README.md
  requirements.txt
```

## Build Steps

1. Create `greeting_service.py`.
2. Add a function named `build_greeting(name: str) -> str`.
3. Import that function in `main.py`.
4. Print a greeting from `main.py`.
5. Run the app from the project root.

Command:

```powershell
python -m app.main
```

## Done When

- The app runs from the command line.
- The business logic is not inside `main.py`.
- You can explain why `src/app/services/` exists.

## Reflection

Write answers in your learning log:

- What should go in `main.py`?
- What should go in a service file?
- Why is project structure important before learning LangChain?
