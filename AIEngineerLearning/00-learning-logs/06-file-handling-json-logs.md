# File Handling, JSON, and Structured Outputs — Learning Log

## 1. Exercise Goal

This exercise builds a small prompt-run storage application. Each prompt execution is represented as structured data, validated with Pydantic, and persisted in `outputs/prompt_runs.json`.

The implementation goes beyond simply calling `json.dump()`. It separates responsibilities into configuration, models, business logic, persistence, exceptions, and tests.

## 2. Project Structure

```text
06-file-handling-json/
├── README.md
├── src/
│   └── prompt_runs/
│       ├── __init__.py
│       ├── config.py
│       ├── exceptions.py
│       ├── main.py
│       ├── models.py
│       ├── repository.py
│       └── service.py
└── tests/
    ├── __init__.py
    └── test_repository.py
```

### Responsibility of Each File

| File | Responsibility |
| --- | --- |
| `config.py` | Defines where the JSON document is stored. |
| `models.py` | Defines and validates the shape of prompt-run data. |
| `repository.py` | Reads, validates, locks, and atomically writes the JSON document. |
| `service.py` | Implements application use cases without depending on JSON details. |
| `exceptions.py` | Defines application-specific storage errors. |
| `main.py` | Builds the dependencies and runs the demonstration workflow. |
| `test_repository.py` | Verifies persistence, JSON validity, directory creation, errors, and tag normalization. |

## 3. Architecture

The application uses a simple layered architecture:

```text
main.py
   │
   ▼
PromptRunService
   │
   ▼
PromptRunRepository protocol
   │
   ▼
JsonPromptRunRepository
   │
   ▼
outputs/prompt_runs.json
```

Each layer has one main purpose:

- **Entry point:** Coordinates the exercise and displays results.
- **Service layer:** Describes what the application can do.
- **Model layer:** Guarantees that application data has a valid shape.
- **Repository layer:** Handles the details of JSON persistence.
- **File system:** Stores the final serialized document.

This separation means the JSON repository could later be replaced with PostgreSQL or Redis without rewriting the service's use cases.

## 4. Main Data Models

### `PromptRun`

`PromptRun` represents one prompt execution:

```json
{
  "id": "generated UUID",
  "created_at": "timezone-aware UTC timestamp",
  "prompt": "The input sent to a model",
  "response": "The model response",
  "tags": ["python", "learning"]
}
```

Pydantic provides several guarantees:

- `id` is generated automatically with `uuid4()`.
- `created_at` is generated in UTC and must be timezone-aware.
- `prompt` and `response` cannot be empty.
- Unknown fields are rejected because `extra="forbid"` is enabled.
- The model is immutable because `frozen=True` is enabled.
- Leading and trailing string whitespace is removed.
- Tags are trimmed, converted to lowercase, deduplicated, and stripped of empty values.

### `PromptRunDocument`

The JSON file stores a document rather than a bare list:

```json
{
  "version": 1,
  "records": []
}
```

The `version` field creates a future migration path. If the JSON structure changes later, the application can identify which format it is reading.

## 5. Application Startup Flow

The startup sequence begins in `main()`:

```text
main()
  │
  ├── configure_logging()
  │
  ├── build_service()
  │     ├── create StorageSettings
  │     ├── calculate outputs/prompt_runs.json
  │     ├── create JsonPromptRunRepository
  │     └── inject repository into PromptRunService
  │
  └── run_exercise(service)
```

`build_service()` is the application's **composition root**. It creates the concrete dependencies and connects them together. The service receives its repository through constructor injection instead of creating the repository itself.

## 6. Write and Append Data Flow

When `service.record_run()` is called, the data follows this path:

```text
Raw prompt, response, and tags
              │
              ▼
Create and validate PromptRun
              │
              ▼
repository.append(prompt_run)
              │
              ▼
Create outputs/ directory if missing
              │
              ▼
Acquire prompt_runs.json.lock
              │
              ▼
Read existing document or create an empty one
              │
              ▼
Create a new records list containing old + new records
              │
              ▼
Validate the updated PromptRunDocument
              │
              ▼
Write safely to a temporary file
              │
              ▼
Flush and fsync the temporary file
              │
              ▼
Atomically replace prompt_runs.json
              │
              ▼
Release the file lock
```

The expression below creates a new list instead of mutating the existing Pydantic document:

```python
records=[*document.records, prompt_run]
```

This preserves every existing record and appends the new record at the end.

## 7. Why the File Lock Matters

The repository uses `portalocker` to prevent two processes from updating the document at the same time.

Without a lock, this race condition could happen:

```text
Process A reads 5 records
Process B reads 5 records
Process A writes record 6A
Process B writes record 6B
Result: record 6A is lost
```

With a lock, only one process can perform the read-modify-write sequence at a time. The second process waits until the first process releases the lock.

## 8. Why Atomic Writes Matter

The repository does not overwrite `prompt_runs.json` directly. It follows an atomic-write strategy:

1. Serialize the validated document.
2. Write it to a temporary file in the same directory.
3. Flush Python's buffer.
4. Call `os.fsync()` to ask the operating system to persist the bytes.
5. Replace the destination with `os.replace()`.

If the program crashes while writing the temporary file, the previous JSON document remains intact. This reduces the chance of leaving the main file half-written or corrupted.

## 9. Read Data Flow

When `service.list_runs()` is called:

```text
service.list_runs()
        │
        ▼
repository.read_all()
        │
        ▼
Initialize the file if it does not exist
        │
        ▼
Read UTF-8 text from disk
        │
        ▼
Reject an empty document
        │
        ▼
Parse JSON with json.loads()
        │
        ▼
Validate the parsed object as PromptRunDocument
        │
        ▼
Return typed Python models
```

There are two validation boundaries:

1. `json.loads()` verifies that the text is valid JSON syntax.
2. `PromptRunDocument.model_validate()` verifies that the JSON has the expected application structure.

Valid JSON is not necessarily valid application data. For example, `{"hello": "world"}` is valid JSON but not a valid `PromptRunDocument`.

## 10. Error Flow

The project translates low-level errors into application-specific exceptions:

```text
OSError
  └── PromptRunStorageError

JSONDecodeError
  └── InvalidPromptRunDocumentError

Pydantic ValidationError
  └── InvalidPromptRunDocumentError

Portalocker LockException
  └── PromptRunStorageError
```

`main()` catches the base `PromptRunError`, logs the full exception, and exits with status code `1`. This gives callers and automation a clear failure signal.

## 11. Exercise Workflow

`run_exercise()` demonstrates the required behavior in this order:

1. Create and store the first prompt run.
2. Read the document back and log its record count.
3. Create and append a second prompt run.
4. Read the final document.
5. Pretty-print the validated document as JSON.

This proves the complete cycle:

```text
create → validate → serialize → write → read → parse → validate → display
```

## 12. What the Tests Verify

The repository tests are designed to verify that:

- Appending a record does not delete existing records.
- Missing parent directories are created automatically.
- The stored file remains valid JSON.
- Corrupted JSON raises a domain-specific exception.
- Tags are normalized and deduplicated.

The tests use pytest's `tmp_path`, so they work with isolated temporary files instead of modifying the real `outputs/prompt_runs.json` document.

## 13. Current Verified Execution Issue

The imports currently mix two execution styles:

- Source files use direct imports such as `from models import PromptRun`.
- Tests use package imports such as `from src.prompt_runs.repository import JsonPromptRunRepository`.

Because of this mismatch, package imports and test collection currently fail with:

```text
ModuleNotFoundError: No module named 'models'
```

For package-style execution, imports inside `prompt_runs` should be relative:

```python
from .models import PromptRun, PromptRunDocument
from .exceptions import PromptRunStorageError
```

The same rule should be applied consistently in `main.py`, `repository.py`, and `service.py`. After that, the package can be executed and tested through one predictable import path.

## 14. Key Takeaways

- **Structured outputs** make data predictable, machine-readable, and validatable.
- **Pydantic models** protect the application from invalid in-memory and persisted data.
- **JSON** is appropriate when data must preserve fields, types, lists, and nesting.
- **A repository** keeps persistence details out of business logic.
- **File locks** protect concurrent read-modify-write operations.
- **Atomic replacement** protects the main document from partial writes.
- **Custom exceptions** prevent low-level implementation details from spreading through the application.
- **Tests with temporary paths** verify file behavior without damaging real data.
- **Consistent package imports** are required for reliable execution and testing.

## 15. Python and Pydantic Questions

### 15.1 What Does `from __future__ import annotations` Do?

Type annotations normally refer to Python objects such as `datetime`, `Path`, or a custom class. This future import postpones how those annotations are evaluated.

With the future import enabled, Python can store an annotation in a deferred form instead of requiring every referenced type to be fully available when the function or class is first defined. In this project's Python 3.14 environment, the future behavior stores the annotations as strings:

```python
from __future__ import annotations


class Node:
    parent: Node | None


print(Node.__annotations__)
# {'parent': 'Node | None'}
```

Without postponed annotations, referring to `Node` inside the class body could be a problem on Python versions that immediately evaluate annotations because `Node` has not finished being created yet.

The import is useful for:

- **Forward references:** A class can refer to itself or to a class defined later.
- **Fewer runtime import problems:** Types used only for type checking do not always need to be resolved immediately.
- **Cleaner type syntax:** You often do not need quotes around forward references.
- **Compatibility:** The source keeps consistent annotation behavior across supported Python versions.

In this exercise, the import is not essential for basic annotations such as `Path` or `str`. It is mainly a defensive, forward-compatible convention. It must appear near the top of the file because future imports affect how Python compiles that module.

### 15.2 What Is `Sequence`?

```python
from collections.abc import Sequence
```

`Sequence` is an abstract interface for ordered collections. A sequence supports iteration, stable ordering, `len(value)`, and access by numeric index.

Common sequence types include `list[str]`, `tuple[str, ...]`, and `str`.

The service declares:

```python
def record_run(
    self,
    *,
    prompt: str,
    response: str,
    tags: Sequence[str] = (),
) -> PromptRun:
```

Using `Sequence[str]` instead of `list[str]` makes the input contract more flexible. Callers can provide a list or tuple:

```python
service.record_run(prompt="...", response="...", tags=["python", "json"])
service.record_run(prompt="...", response="...", tags=("python", "json"))
```

The service then creates its own list:

```python
tags=list(tags)
```

This conversion gives the Pydantic model the concrete `list[str]` it expects and prevents the model from retaining a caller-owned list. The default is an empty tuple, `()`, rather than an empty list. Tuples are immutable, so this also avoids the mutable-default-argument problem.

One subtle detail is that `str` itself is a sequence of characters. A stricter public API might reject a plain string explicitly if passing `"python"` instead of `["python"]` would be a likely caller mistake.

### 15.3 What Does `ConfigDict(...)` Configure?

```python
model_config = ConfigDict(
    extra="forbid",
    frozen=True,
    str_strip_whitespace=True,
)
```

This line configures how the Pydantic model validates and behaves.

#### `extra="forbid"`

Reject fields that are not declared by the model:

```python
PromptRun(
    prompt="Hello",
    response="Hi",
    unknown_field="unexpected",
)
```

Instead of silently ignoring `unknown_field`, Pydantic raises a `ValidationError`. This catches misspelled keys and unexpected changes in external data.

#### `frozen=True`

Prevent field assignment after the model has been created:

```python
prompt_run.prompt = "Changed prompt"  # ValidationError
```

This provides *faux immutability*: the model's fields cannot be reassigned normally. It makes a stored prompt run behave like a historical record rather than an object that changes unexpectedly.

It is shallow immutability. A mutable value stored inside the model may still require additional protection.

#### `str_strip_whitespace=True`

Remove leading and trailing whitespace from strings during validation:

```python
PromptRun(prompt="  Explain JSON  ", response="  JSON stores data.  ")
```

The validated values become:

```text
prompt   = "Explain JSON"
response = "JSON stores data."
```

This improves consistency and ensures that a value containing only spaces fails a `min_length=1` requirement after normalization.

### 15.4 What Does `default_factory` Mean?

```python
created_at: datetime = Field(default_factory=utc_now)
```

A default factory is a callable that Pydantic invokes whenever it needs to create a default value for a new model instance.

The function is passed without parentheses:

```python
default_factory=utc_now
```

This gives Pydantic the function itself. Pydantic calls it later for every new `PromptRun`.

If the timestamp were calculated once while defining the class, later objects could receive the same stale timestamp. A factory produces a fresh value for each instance.

The behavior is conceptually similar to:

```python
first_run = PromptRun(created_at=utc_now(), ...)
second_run = PromptRun(created_at=utc_now(), ...)
```

Default factories are also useful for dynamic or mutable defaults:

```python
id: UUID = Field(default_factory=uuid4)
tags: list[str] = Field(default_factory=list)
```

Each model receives a new UUID and its own list.

### 15.5 What Is the Difference Between `json.load()` and `json.loads()`?

Both functions parse JSON, but they accept different inputs.

#### `json.load()` Reads from a File-Like Object

```python
import json


with open("prompt_runs.json", encoding="utf-8") as file:
    data = json.load(file)
```

The argument is an open file or another object with a `.read()` method.

#### `json.loads()` Reads from In-Memory JSON

```python
raw_content = '{"version": 1, "records": []}'
data = json.loads(raw_content)
```

The `s` can be remembered as **string**. More precisely, `json.loads()` accepts a `str`, `bytes`, or `bytearray` containing JSON.

This repository uses:

```python
raw_content = self._file_path.read_text(encoding="utf-8")
raw_document = json.loads(raw_content)
```

This is appropriate because `Path.read_text()` has already read the file and returned an in-memory string.

| Function | Input | Typical Use |
| --- | --- | --- |
| `json.load(file)` | Open file-like object | Read and parse from a file handle. |
| `json.loads(text)` | JSON string, bytes, or bytearray | Parse JSON already loaded into memory. |

Neither function validates the application's business schema. They only verify JSON syntax and convert JSON values into normal Python values.

### 15.6 What Does `model_dump_json(indent=2)` Do?

```python
serialized_document = document.model_dump_json(indent=2)
```

`model_dump_json()` is a Pydantic method that serializes a validated model into a JSON string.

It performs two main operations:

1. Converts the model and nested models into JSON-compatible data.
2. Encodes that data as JSON text.

Pydantic knows how to serialize types the standard JSON encoder cannot handle directly, including `UUID` values, `datetime` values, and nested Pydantic models.

```python
document = PromptRunDocument(records=[prompt_run])
serialized_document = document.model_dump_json(indent=2)
```

The result is a string similar to:

```json
{
  "version": 1,
  "records": [
    {
      "id": "c76d84a1-8305-4e30-a194-25f5d2d65e08",
      "created_at": "2026-07-17T10:30:00Z",
      "prompt": "Explain JSON",
      "response": "JSON is a structured text format.",
      "tags": [
        "python",
        "json"
      ]
    }
  ]
}
```

The `indent=2` argument makes the output human-readable by adding line breaks and two spaces for each nesting level. Without indentation, the JSON is more compact.

This method only returns a string. It does not write to disk. `_write_atomic()` writes the returned string into the temporary file afterward.

| Method | Result |
| --- | --- |
| `model_dump()` | Python dictionary. |
| `model_dump_json()` | JSON string. |
| `model_validate(data)` | Validated model created from Python data. |
| `model_validate_json(text)` | Validated model created directly from JSON text. |

### 15.7 What Does `@dataclass(frozen=True, slots=True)` Mean?

```python
@dataclass(frozen=True, slots=True)
class StorageSettings:
    output_directory: Path = Path("outputs")
    file_name: str = "prompt_runs.json"
```

`@dataclass` asks Python to generate common class methods from the declared fields. Python generates behavior such as an `__init__()` method, readable `__repr__()`, and `__eq__()` for value comparison.

This makes the class convenient for holding configuration data without repetitive boilerplate.

#### `frozen=True`

Prevent normal field reassignment after construction:

```python
settings = StorageSettings()
settings.file_name = "other.json"  # FrozenInstanceError
```

This is useful because configuration should remain stable after the application has been assembled.

Dataclass freezing is shallow. It prevents assigning another value to a field but does not automatically make every object stored inside its fields deeply immutable.

#### `slots=True`

Generate `__slots__` for the declared fields instead of giving each instance a normal `__dict__`.

The practical effects are:

- Instances usually use less memory.
- Attribute access may be slightly more efficient.
- New undeclared attributes cannot be added accidentally.

```python
settings.unexpected = "value"  # AttributeError
```

For this small exercise, memory savings are not important. The main benefit is a stricter configuration object that allows only its declared fields.

#### Why a Dataclass Instead of a Pydantic Model?

`StorageSettings` contains trusted values created by the application itself. It mainly needs a compact immutable container, so a standard dataclass is sufficient.

`PromptRun` represents data that may come from users, files, or external systems. It needs parsing and validation, so Pydantic is the better choice.
