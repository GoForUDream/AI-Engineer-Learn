# Async Basics — Learning Log

## 1. What Is Concurrent I/O in Python?

**I/O (Input/Output)** refers to operations where code waits on something outside the CPU. Examples include downloading a webpage, reading a file, or waiting for a database query.

- **Sequential I/O:** Python starts one operation, waits for it to finish, and then starts the next operation.
- **Concurrent I/O:** Python uses idle waiting periods to make progress on other I/O tasks.

Concurrent I/O does not necessarily mean that code runs simultaneously across multiple CPU cores. It means the program manages waiting time more efficiently.

## 2. What Does `httpx` Do?

`httpx` is an HTTP client library for Python. Like `requests`, it can call APIs, download web content, and interact with web services.

Its key advantage for this exercise is that it supports both synchronous and asynchronous APIs. The `requests` library is synchronous, while `httpx` lets an application choose the appropriate model.

## 3. How Do `asyncio` and `httpx.AsyncClient` Work Together?

`asyncio` is Python's built-in framework for asynchronous operations. Its **event loop** tracks active tasks. When one task reaches an `await` point, the event loop can pause it and run another task.

`httpx.AsyncClient` is an asynchronous HTTP client designed to work with this event loop. Reusing one client also allows multiple requests to share connection resources.

```python
import asyncio

import httpx


async def fetch(client: httpx.AsyncClient, url: str) -> httpx.Response:
    return await client.get(url, timeout=5)


async def main() -> None:
    async with httpx.AsyncClient() as client:
        responses = await asyncio.gather(
            fetch(client, "https://example.com/one"),
            fetch(client, "https://example.com/two"),
        )
        print(responses)


asyncio.run(main())
```

## 4. What Is the Difference Between Sync and Async Code?

The main difference is whether execution remains blocked while waiting.

| Attribute | Synchronous (Sync) | Asynchronous (Async) |
| --- | --- | --- |
| Execution flow | Runs one operation at a time and blocks while waiting. | Can pause one operation and let another make progress. |
| Keywords | Uses `def` and normal function calls. | Uses `async def` and `await`. |
| Waiting behavior | Leaves the current thread blocked during the wait. | Lets the event loop switch between waiting tasks. |
| Analogy | A waiter stands at the kitchen until one order is ready. | A waiter takes another table's order while the first meal cooks. |

## 5. Why Is Async Useful for AI Apps?

AI applications often spend significant time waiting for external services such as LLM providers, search APIs, tool calls, and vector databases.

For example, an application might need to call three model APIs and then save a result:

```text
Sync:  API 1 (4s) → API 2 (3s) → API 3 (5s) → Database (1s) = about 13s
Async: Start independent API calls together → await results → save to database
```

Async can reduce total waiting time for independent operations and help a server handle more concurrent requests efficiently. Actual throughput still depends on service limits, connection pools, application design, and available resources.

## 6. What Kind of Work Does Async Not Speed Up?

Async is most useful for **I/O-bound** work. It does not inherently speed up **CPU-bound** work, where the processor is busy calculating rather than waiting.

Examples of CPU-bound work include:

- Heavy mathematical operations, such as matrix multiplication.
- Running a model locally on the CPU.
- Image processing or video encoding.
- Sorting very large collections or parsing large files in memory.

A CPU-heavy function can block the event loop and prevent other async tasks from progressing. CPU-bound workloads may require multiprocessing, native code that releases the Global Interpreter Lock (GIL), a worker system, or GPU acceleration.
