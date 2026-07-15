# 05. Async Basics

Goal: Learn the basics of concurrent IO in Python.

## Why This Matters

AI apps often wait on slow external systems:

- LLM responses.
- Embedding requests.
- Search APIs.
- Database calls.
- Tool calls.

Async helps when your app needs to wait on many IO operations.

## Exercise

Fetch weather for multiple cities concurrently.

Use:

- `asyncio`
- `httpx.AsyncClient`

Cities:

- Saigon
- Hanoi
- Tokyo

## Build Steps

1. Install `httpx`.
2. Write an async function named `fetch_weather(city: str)`.
3. Use `asyncio.gather`.
4. Add error handling per city.
5. Print results in a clean list.

## Done When

- Three cities are fetched in one async run.
- One failed city does not crash the full script.
- You can explain when async helps and when it does not.

## Reflection

Write answers in your learning log:

- What is the difference between sync and async code?
- Why is async useful for AI apps?
- What kind of work does async not speed up?
