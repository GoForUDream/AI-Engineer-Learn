# 05. File Uploads

Goal: Accept files without confusing file metadata, stored bytes, and extracted content.

## Why This Matters

Document upload is the entry point for many RAG systems. The upload endpoint must reject unsafe or unsupported input before later ingestion code sees it.

## Exercise

Add a text-file upload feature to FastAPI and React.

Accept only `.txt` and `.md` files for this lesson. Store file metadata in PostgreSQL and store file bytes in a local ignored upload directory.

## Build Steps

1. Add a multipart upload endpoint.
2. Validate extension, reported content type, and maximum byte size.
3. Generate the server-side storage name; never trust the client file path.
4. Save original name, stored name, content type, size, owner, and upload time.
5. Add list, metadata detail, and delete endpoints.
6. Build a frontend upload form with progress/pending feedback.
7. Show validation errors and the uploaded file list.
8. Test empty, oversized, unsupported, and valid uploads.

## Safety Rules

- Do not use the original filename as the storage path.
- Prevent path traversal.
- Do not load an unlimited file into memory.
- Keep uploaded files outside source-controlled directories.
- Deleting metadata and stored bytes should behave as one use case.

## Done When

- Valid text files can be uploaded and listed.
- Invalid files receive a clear `4xx` response.
- A filename cannot escape the upload directory.
- The frontend shows pending, success, and failure states.
- Tests verify both validation and cleanup behavior.

## Reflection

- Why is a file extension not enough to trust a file?
- What changes when files are stored in object storage instead of local disk?
- Why should ingestion be a separate step from upload?
