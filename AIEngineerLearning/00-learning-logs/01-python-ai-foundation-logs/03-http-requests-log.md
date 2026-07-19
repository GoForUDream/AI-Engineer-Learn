# HTTP Requests — Learning Log

## 1. Why Do We Use a Timeout?

Without a timeout, a Python network request may wait indefinitely when the remote server is offline, overloaded, or affected by a silent network failure.

### The Domino Effect

In a larger application, such as a FastAPI backend or Discord bot, one hanging API call can block a processing thread. If many users trigger the same behavior, the server can exhaust its available workers or threads.

### The Solution

Setting `timeout=5` gives the request a limit. If the operation exceeds that limit, the client raises an exception so the application can handle the failure and continue running.

```python
response = requests.get(url, timeout=5)
```

## 2. What Should an AI Tool Return When an API Call Fails?

An AI tool should not only print an error and return `None`. The agent needs structured data that explains the failure so it can decide what to do next.

A useful tool response includes a clear status, error type, and actionable message:

```python
import requests


def get_weather_tool(city: str) -> dict:
    url = f"https://wttr.in/{city}?format=j1"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        return {
            "status": "success",
            "data": {
                "temperature_c": data["current_condition"][0]["temp_C"],
                "condition": data["current_condition"][0]["weatherDesc"][0]["value"],
            },
        }
    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "error_type": "TIMEOUT",
            "message": (
                "The weather service took too long to respond. "
                f"The request for '{city}' was aborted."
            ),
        }
    except requests.exceptions.HTTPError:
        return {
            "status": "error",
            "error_type": f"HTTP_{response.status_code}",
            "message": (
                f"Could not find weather data for '{city}'. "
                "Please verify the city name spelling."
            ),
        }
```

### Why This Structure Matters to an AI Agent

- **Clear status:** A value such as `"status": "error"` immediately tells the agent that the tool failed.
- **Actionable message:** A user-friendly `message` helps the agent explain the problem clearly.
- **Self-correction:** An `error_type` such as `HTTP_404` can help an agent identify invalid input, correct it, and retry when appropriate.
