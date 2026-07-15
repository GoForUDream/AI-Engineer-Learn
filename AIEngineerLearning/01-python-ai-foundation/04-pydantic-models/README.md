# 04. Pydantic Models

Goal: Learn how to validate external data and structured AI outputs.

## Why This Matters

LLM responses and API responses are not automatically trustworthy.

Pydantic helps you define the shape of data you expect.

## Exercise

Create models for weather data:

```text
WeatherRequest
WeatherCondition
WeatherReport
APIResult
```

## Build Steps

1. Install `pydantic`.
2. Create a request model with a `city` field.
3. Create a response model with city, temperature, condition, and wind speed.
4. Validate raw dictionaries.
5. Convert the model to JSON.
6. Try invalid data and read the validation error.

## Done When

- Valid data becomes a typed model.
- Invalid data fails clearly.
- You can serialize the model to JSON.

## Reflection

Write answers in your learning log:

- What problem does Pydantic solve?
- How is this useful for LLM structured outputs?
- What should happen when model output is missing a required field?
