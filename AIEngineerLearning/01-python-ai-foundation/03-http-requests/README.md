# 03. HTTP Requests

Goal: Learn how Python talks to external APIs.

## Why This Matters

Most AI apps use external services:

- LLM APIs.
- Weather APIs.
- Search APIs.
- Vector databases.
- Internal backend APIs.

Before tools and agents, you need to understand normal HTTP calls.

## Exercise

Call this API:

```text
https://wttr.in/saigon?format=j1
```

Use `requests`.

## Build Steps

1. Install `requests`.
2. Create a function named `get_weather(city: str)`.
3. Add a timeout.
4. Handle non-200 responses.
5. Extract only useful fields from the response.
6. Print a clean summary.

## Done When

- The script handles success.
- The script handles timeout.
- The script handles invalid city names.
- The output is clean and readable.

## Reflection

Write answers in your learning log:

- What is an HTTP status code?
- Why do we use a timeout?
- What should an AI tool return when an API call fails?
