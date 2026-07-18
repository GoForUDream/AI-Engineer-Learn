# 07. Streaming Responses and Chat UI

Goal: Display a response incrementally while the backend is still producing it.

## Why This Matters

LLM responses may take seconds to finish. Streaming gives immediate feedback, allows cancellation, and makes long operations feel understandable.

## Exercise

Build a chat-shaped UI backed by a fake streaming endpoint. The backend should split a fixed response into small chunks with a short delay. Do not call an LLM yet.

## Build Steps

1. Create a validated `POST /api/chat/stream` endpoint.
2. Stream plain text or newline-delimited JSON chunks.
3. Include a final completion event and a controlled error event.
4. Read the response body incrementally with `fetch()` in React.
5. Append chunks to one assistant message without duplicating text.
6. Add a Stop button using `AbortController`.
7. Disable duplicate submission while a request is active.
8. Test completion, cancellation, and mid-stream failure.

## Required UI States

- Empty conversation.
- User message submitted.
- Assistant is streaming.
- Stream completed.
- Stream cancelled with partial text retained.
- Stream failed with a retry action.

## Done When

- Text appears before the full backend response finishes.
- The user can cancel an active stream.
- Partial output remains readable after cancellation or failure.
- A second message can be sent after completion.
- No chunk is duplicated when React re-renders.

## Reflection

- How is a streaming response different from a normal JSON response?
- Why is cancellation important for AI applications?
- When would you choose WebSockets instead of HTTP response streaming?
