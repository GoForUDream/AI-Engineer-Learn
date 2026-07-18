# Mini Project: Prompt Runner — Storage and Data Flow

## 1. Role of `storage.py`

`storage.py` is the persistence layer. It converts between validated Pydantic models and durable JSON text.

It creates storage, reads and validates JSON, generates IDs, adds and finds records, locks writes, performs atomic replacement, and translates low-level failures into application-specific exceptions. Terminal input and display formatting belong to `main.py`.

## 2. Data Shapes

### Input: `PromptRunCreate`

```json
{
  "prompt_name": "summarizer-test",
  "prompt_text": "Summarize this text in 3 bullets.",
  "response_text": "This is a sample model response.",
  "tags": ["summary", "test"]
}
```

The user does not provide `id` or `created_at`. Storage creates them.

### Stored Record: `PromptRun`

```json
{
  "id": "run_001",
  "created_at": "2026-07-18T05:14:25.315766Z",
  "prompt_name": "summarizer-test",
  "prompt_text": "Summarize this text in 3 bullets.",
  "response_text": "This is a sample model response.",
  "tags": ["summary", "test"]
}
```

### Root File: `PromptRunDocument`

```json
{
  "version": 1,
  "runs": [
    {
      "id": "run_001",
      "created_at": "2026-07-18T05:14:25.315766Z",
      "prompt_name": "summarizer-test",
      "prompt_text": "Summarize this text in 3 bullets.",
      "response_text": "This is a sample model response.",
      "tags": ["summary", "test"]
    }
  ]
}
```

`version` allows future schema migrations. `runs` preserves creation order.

## 3. Storage Class Setup

### `_ID_PATTERN`

```python
_ID_PATTERN = re.compile(r"^run_(\d+)$")
```

**Input:** An existing ID string.

**Logic:** Requires the complete value to start with `run_` and end with digits. The digits become capture group 1.

| Value | Match? | Captured Value |
| --- | --- | --- |
| `run_001` | Yes | `001` |
| `run_42` | Yes | `42` |
| `RUN_001` | No | — |
| `run_one` | No | — |

**Result when used:** A regex match object or `None`.

### `__init__()`

```python
def __init__(
    self,
    file_path: Path,
    *,
    lock_timeout_seconds: float = 10.0,
) -> None:
```

**Inputs:**

- `file_path`: JSON destination, such as `outputs/prompt_runs.json`.
- `lock_timeout_seconds`: Maximum wait for the lock. It is keyword-only because it follows `*`.

**Logic:**

1. Saves the JSON path.
2. Derives `outputs/prompt_runs.json.lock`.
3. Saves the timeout.

**Return:** `None`. It configures the object but does not access the file.

### `file_path` Property

**Input:** No explicit input.

**Logic:** Returns the private configured path through a read-only property.

**Return:** A `Path`.

## 4. `initialize()`

```python
def initialize(self) -> None:
```

**Input:** No explicit input.

**Logic:**

1. Creates the parent directory.
2. Returns if the JSON file already exists.
3. Acquires the lock.
4. Checks for the file again after locking.
5. Creates an empty `PromptRunDocument` if still missing.
6. Writes it with `_write_atomic()`.

The second existence check prevents two starting processes from both creating and overwriting the file.

**Return:** `None`.

**Raises:** `StorageLockError` if the lock times out.

## 5. Public Storage Functions

### `add()`

```python
def add(self, input_data: PromptRunCreate) -> PromptRun:
```

**Input:** A validated `PromptRunCreate`.

**Logic:**

1. Creates the output directory.
2. Acquires the storage lock.
3. Reads the document or creates an in-memory default.
4. Generates the next ID.
5. Generates the current UTC timestamp.
6. Builds a complete validated `PromptRun`.
7. Creates a new document with old runs plus the new run.
8. Writes the updated document atomically.
9. Releases the lock.

```python
runs=[*document.runs, prompt_run]
```

This creates a new list containing every old record followed by the new record.

Read, ID generation, and write occur under one lock. Two processes cannot generate the same next ID.

**Return:** The newly created `PromptRun`.

**Possible errors:** `StorageLockError`, `StorageReadError`, `InvalidStorageDocumentError`, and `StorageWriteError`.

### `list_all()`

```python
def list_all(self) -> list[PromptRun]:
```

**Input:** No explicit input.

**Logic:**

1. Initializes storage if needed.
2. Reads and validates the document.
3. Copies `document.runs`.

**Return:** A new `list[PromptRun]` in creation order. Empty storage returns `[]`.

### `get_by_id()`

```python
def get_by_id(self, prompt_run_id: str) -> PromptRun:
```

**Input:** An ID such as `"run_001"`.

**Logic:**

1. Strips whitespace.
2. Converts the ID to lowercase.
3. Calls `list_all()`.
4. Searches each run.
5. Returns the first match.
6. Raises `PromptRunNotFoundError` if absent.

`" RUN_001 "` becomes `"run_001"`.

**Return:** One `PromptRun`.

**Complexity:** O(n), because all records are loaded and searched.

## 6. Private Read Functions

### `_read_document_or_default()`

**Input:** No explicit input.

**Logic:** Returns a new empty `PromptRunDocument` if the file is missing; otherwise calls `_read_document()`.

**Return:** A validated `PromptRunDocument`.

This lets `add()` create the first record before a file exists.

### `_read_document()`

**Input:** No explicit input; reads `self._file_path`.

**Logic:**

1. Reads UTF-8 text.
2. Rejects empty content.
3. Parses JSON using `json.loads()`.
4. Validates data using `PromptRunDocument.model_validate()`.
5. Converts nested dictionaries into `PromptRun` objects.

```text
Disk bytes
   ↓ UTF-8 decoding
JSON string
   ↓ json.loads()
Python dictionary and lists
   ↓ Pydantic model_validate()
PromptRunDocument containing PromptRun objects
```

**Return:** A `PromptRunDocument`.

| Failure | Storage Error |
| --- | --- |
| File cannot be read | `StorageReadError` |
| Empty file | `InvalidStorageDocumentError` |
| Invalid JSON syntax | `InvalidStorageDocumentError` with line and column |
| Invalid schema | `InvalidStorageDocumentError` with Pydantic details |

## 7. `_write_atomic()`

```python
def _write_atomic(self, document: PromptRunDocument) -> None:
```

**Input:** A validated `PromptRunDocument`.

**Logic:**

1. Creates the parent directory.
2. Serializes with `model_dump_json(indent=2)`.
3. Creates a temporary file beside the destination.
4. Writes JSON and a newline.
5. Flushes Python's buffer.
6. Calls `os.fsync()`.
7. Calls `os.replace()` for atomic replacement.
8. Deletes the temporary file after an `OSError`.

```text
Validated document
        ↓
Pretty JSON string
        ↓
.prompt_runs.json.<random>.tmp
        ↓ write + flush + fsync
os.replace(temp, prompt_runs.json)
        ↓
Complete destination file
```

**Return:** `None`.

**Raises:** `StorageWriteError` with the original `OSError` retained as its cause.

Atomic replacement prevents partially written destination files.

## 8. `_generate_next_id()`

```python
def _generate_next_id(
    self,
    prompt_runs: list[PromptRun],
) -> str:
```

**Input:** Existing runs.

**Logic:**

1. Starts the highest number at zero.
2. Matches every ID.
3. Rejects invalid existing IDs.
4. Converts suffixes to integers.
5. Finds the highest value.
6. Adds one.
7. Formats at least three digits.

```text
[run_001, run_004, run_012]
              ↓
[1, 4, 12]
              ↓
highest = 12
              ↓
"run_013"
```

**Return:** A string such as `"run_001"` or `"run_013"`.

Using the highest ID instead of list length avoids reusing deleted IDs.

## 9. Exception Hierarchy

```text
PromptRunnerStorageError
├── StorageReadError
├── StorageWriteError
├── InvalidStorageDocumentError
├── PromptRunNotFoundError
└── StorageLockError
```

The CLI catches the base storage error, prints a clear message, and returns exit code `1`.

## 10. `add` Flow

```powershell
python -m prompt_runner.main add --name summarizer-test --prompt "Summarize this text." --response "Sample response." --tags "summary,test"
```

```text
CLI strings
   ↓ argparse
Namespace
   ↓
request_required_value() + parse_tags()
   ↓
PromptRunCreate
   ↓ Pydantic validation
storage.add()
   ↓ acquire lock
Read document or use empty default
   ↓
Generate ID + UTC timestamp
   ↓
Create PromptRun
   ↓
Append to PromptRunDocument
   ↓
Atomic JSON write
   ↓
Return PromptRun
   ↓
Print success and JSON
   ↓
Exit code 0
```

Tag transformation:

```text
" Summary, test, summary "
   ↓ parse_tags()
["Summary", "test", "summary"]
   ↓ Pydantic validator
["summary", "test"]
```

Failures:

- Invalid input model → exit code `2`.
- Empty required input → exit code `2`.
- Storage failure → exit code `1`.
- Ctrl+C → exit code `130`.

## 11. `list` Flow

```powershell
python -m prompt_runner.main list
```

```text
"list"
  ↓ argparse
build_storage()
  ↓
handle_list()
  ↓
storage.list_all()
  ↓ initialize if missing
Read JSON text
  ↓ json.loads()
Python data
  ↓ Pydantic validation
PromptRunDocument
  ↓ copy runs
list[PromptRun]
  ↓
Empty? Print "No prompt runs..."
Otherwise calculate widths
  ↓
Format timestamps and tags
  ↓
Print summary table
  ↓
Exit code 0
```

Example:

```text
ID       PROMPT NAME      CREATED AT               TAGS
-------------------------------------------------------
run_001  summarizer-test  2026-07-18 05:14:25 UTC  summary, test
```

`list` omits full prompt and response text; `view` shows them.

## 12. `view` Flow

```powershell
python -m prompt_runner.main view run_001
```

```text
"view" + "run_001"
   ↓ argparse
handle_view()
   ↓
storage.get_by_id("run_001")
   ↓ normalize ID
storage.list_all()
   ↓
Read, parse, validate document
   ↓
Linear search
   ↓
Return matching PromptRun
   ↓
model_dump_json(indent=2)
   ↓
Print complete JSON
   ↓
Exit code 0
```

A missing ID raises `PromptRunNotFoundError` and produces exit code `1`.

## 13. Configuration Flow

```text
.env and process environment
        ↓
PROMPT_RUNNER_OUTPUT_DIRECTORY
PROMPT_RUNNER_STORAGE_FILE
PROMPT_RUNNER_LOCK_TIMEOUT_SECONDS
        ↓ validation
AppConfig
        ↓ storage_file_path
JsonPromptRunStorage(path, timeout)
```

Configuration changes the storage path and timeout without editing source.

## 14. Current Verified Path Mismatch

The CLI currently resolves:

```text
outputs/prompt_runs.json
```

relative to the project root. The existing record is at:

```text
src/outputs/prompt_runs.json
```

These are different files. Verified behavior:

```text
list          → No prompt runs have been saved yet.
view run_001  → Storage error: Prompt run "run_001" was not found.
```

The `src/outputs/` JSON contains `run_001`, but the current CLI does not read that location. Prefer one canonical project-root `outputs/` directory and align the configuration and existing data.

## 15. End-to-End Model

```text
CLI input
  ↓
argparse routing
  ↓
input normalization
  ↓
Pydantic validation
  ↓
storage operation
  ↓
file lock for writes
  ↓
JSON parsing
  ↓
document validation
  ↓
add, list, or find
  ↓
atomic write when changed
  ↓
typed model returned
  ↓
table or JSON output
  ↓
exit code
```

The CLI works with validated Python models. `storage.py` owns conversion between those models and durable JSON text.
