# 06. File Handling, JSON, and Structured Outputs

Goal: Learn how to save and load structured data.

## Why This Matters

AI apps often need local files for:

- Uploaded documents.
- Prompt experiments.
- Evaluation datasets.
- Logs.
- Cached responses.
- RAG ingestion inputs.

JSON is one of the most common formats for structured AI output.

## Exercise

Create a script that saves prompt runs to a JSON file.

Each record should include:

- `id`
- `created_at`
- `prompt`
- `response`
- `tags`

## Build Steps

1. Create an `outputs/` folder from Python if missing.
2. Write one record to `outputs/prompt_runs.json`.
3. Read the file back.
4. Append another record.
5. Pretty-print the JSON.

## Done When

- The script can create the JSON file.
- The script can append without deleting old records.
- The file remains valid JSON.
- The data shape is predictable.

## Reflection

Write answers in your learning log:

- Why are structured outputs useful in AI apps?
- When would you use JSON instead of plain text?
- What can go wrong when appending to files?
