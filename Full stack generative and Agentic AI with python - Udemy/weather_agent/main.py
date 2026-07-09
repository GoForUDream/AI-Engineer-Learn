import json
import os
from typing import Generic, TypeVar

import requests
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

# ==========================================================
# Configuration
# ==========================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY")

client = OpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

SYSTEM_PROMPT = (
    "You are a helpful AI assistant. Use the available tools whenever necessary."
)

# ==========================================================
# Pydantic Models
# ==========================================================

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    success: bool
    data: T | None = None
    error: str | None = None


class WeatherRequest(BaseModel):
    city: str


class WeatherData(BaseModel):
    city: str
    forecast: str


# ==========================================================
# Tool Implementation
# ==========================================================


def get_weather(request: WeatherRequest) -> APIResponse[WeatherData]:
    """Retrieve current weather information."""

    url = f"https://wttr.in/{request.city.lower()}?format=%C+%t+%w"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        return APIResponse(
            success=True,
            data=WeatherData(
                city=request.city,
                forecast=response.text.strip(),
            ),
        )

    except Exception as ex:
        return APIResponse(
            success=False,
            error=str(ex),
        )


# ==========================================================
# Tool Definitions
# ==========================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a city.",
            "parameters": WeatherRequest.model_json_schema(),
        },
    }
]

AVAILABLE_FUNCTIONS = {
    "get_weather": get_weather,
}


# ==========================================================
# Tool Executor
# ==========================================================


def execute_tool_call(tool_call):
    """Execute a function requested by the model."""

    function_name = tool_call.function.name

    if function_name not in AVAILABLE_FUNCTIONS:
        return {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": function_name,
            "content": json.dumps({"success": False, "error": "Unknown tool"}),
        }

    request = WeatherRequest.model_validate_json(tool_call.function.arguments)

    result = AVAILABLE_FUNCTIONS[function_name](request)

    return {
        "role": "tool",
        "tool_call_id": tool_call.id,
        "name": function_name,
        "content": result.model_dump_json(),
    }


# ==========================================================
# Chat Logic
# ==========================================================


def chat(messages: list):
    """Send conversation to Gemini."""

    return client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=messages,
        tools=TOOLS,
    )


# ==========================================================
# Main Loop
# ==========================================================


def main():

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]

    while True:
        user_input = input("\nYou: ")

        if user_input.lower() == "exit":
            break

        messages.append(
            {
                "role": "user",
                "content": user_input,
            }
        )

        try:
            response = chat(messages)

            assistant_message = response.choices[0].message

            messages.append(assistant_message)

            if assistant_message.tool_calls:
                for tool_call in assistant_message.tool_calls:
                    tool_response = execute_tool_call(tool_call)

                    messages.append(tool_response)

                final_response = client.chat.completions.create(
                    model="gemini-2.5-flash",
                    messages=messages,
                )

                final_message = final_response.choices[0].message

                messages.append(final_message)

                print(f"\nGemini: {final_message.content}")

            else:
                print(f"\nGemini: {assistant_message.content}")

        except Exception as ex:
            print(f"\nError: {ex}")


# ==========================================================
# Entry Point
# ==========================================================

if __name__ == "__main__":
    main()
