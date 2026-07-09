import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key
gemini_key = os.getenv("GEMINI_API_KEY")

if not gemini_key:
    raise ValueError("GEMINI_API_KEY is missing. Please check your .env file.")

# Initialize the OpenAI client pointing to the Gemini endpoint
client = OpenAI(
    api_key=gemini_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

try:
    # Send a basic chat completion request
    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful AI coding assistant. Only answer questions related to coding and programming. If the question is not related to coding, respond with 'I can only answer coding-related questions.'",
            },
            {"role": "user", "content": "Will Argentina win the 2022 FIFA World Cup?"},
        ],
        response_format={"type": "json_object"},
    )

    # Print the response from Gemini
    print("Gemini response:\n")
    print(response.choices[0].message.content)

except Exception as e:
    print(f"An error occurred while calling the API: {e}")
