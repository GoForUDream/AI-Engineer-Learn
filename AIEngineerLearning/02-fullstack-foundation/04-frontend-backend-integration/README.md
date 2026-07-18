# 04. Frontend and Backend Integration

Goal: Connect the React interface to the FastAPI Todo API.

## Why This Matters

Most full-stack bugs happen at boundaries: wrong URLs, mismatched JSON fields, unexpected status codes, CORS settings, stale state, or network failures.

## Exercise

Replace the frontend's mock Todo storage with real API requests.

## Build Steps

1. Put the backend URL in `VITE_API_URL` and document it in `.env.example`.
2. Configure a narrow development CORS origin in FastAPI.
3. Create one typed API client module instead of scattering `fetch()` calls.
4. Load todos when the page opens.
5. Connect create, update, and delete actions.
6. Handle non-success HTTP responses before parsing success data.
7. Prevent accidental duplicate submissions.
8. Add frontend tests with mocked API responses.

## Required UI States

- Initial loading.
- Empty data.
- Loaded data.
- Submission in progress.
- Field validation failure.
- API failure with a retry action.
- Successful deletion without a full page refresh.

## Done When

- The browser UI performs full CRUD through FastAPI.
- A backend validation error is shown near the relevant form.
- A network failure does not erase the current UI unexpectedly.
- API request and response types are centralized.
- The browser console has no CORS or unhandled promise errors.

## Reflection

- What does CORS protect, and what does it not protect?
- Why is `response.ok` important when using `fetch()`?
- Which system owns validation: frontend, backend, or both?
