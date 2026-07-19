# Pydantic Models — Learning Log

## 1. What Problem Does Pydantic Solve?

Pydantic helps applications handle **untrusted and unpredictable data**.

Python is dynamically typed. Data from an external API, database, or user may arrive as a raw dictionary or string, with no guarantee that fields are present, correctly spelled, or using the expected types.

Without Pydantic, validation can require many defensive checks:

```python
if "weather" in data and "temperature_c" in data["weather"]:
    if isinstance(data["weather"]["temperature_c"], (int, float)):
        # Use the validated value.
        pass
```

Pydantic acts as a parsing and validation layer. You define the expected data shape with a model, pass raw data through it, and receive validated, typed data or a clear validation error.

## 2. How Is Pydantic Useful for LLM Structured Outputs?

LLMs naturally generate text, but application code often needs predictable JSON. With structured-output features, a Pydantic model can define the schema expected from the model.

This is useful for three main reasons:

- **Schema generation:** An SDK can derive a JSON Schema from the Pydantic model and use it to request a matching response shape.
- **Type conversion:** Pydantic can convert compatible input values into the declared Python types before application logic uses them.
- **Editor support:** Typed response objects provide autocomplete and reduce mistakes caused by manually typing dictionary keys.

## 3. What If Model Output Is Missing a Required Field?

If output is missing a required field, Pydantic raises a `ValidationError`. An AI workflow should catch that error instead of allowing the entire application to crash.

### Retry and Self-Correction Flow

```text
LLM generates a response
          │
          ▼
Pydantic validates the response
          │
     ┌────┴────┐
     │         │
   Valid    ValidationError
     │         │
     ▼         ▼
 Continue   Inspect the error
                 │
                 ▼
          Request a corrected response
                 │
                 └──► Retry validation
```

### Implementation Strategy

1. **Catch the error:** Wrap validation in a `try`/`except ValidationError` block.
2. **Inspect the details:** Use `ValidationError.errors()` to identify missing or invalid fields.
3. **Request a correction:** Include a concise description of the validation problem in a retry prompt.
4. **Limit retries:** Stop after a small, defined number of attempts and return a controlled error if validation still fails.
