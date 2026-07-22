import { env } from "../config/env";
import {
  ApiError,
  type ApiErrorBody,
} from "./errors";

type HttpMethod =
  | "GET"
  | "POST"
  | "PATCH"
  | "DELETE";

interface RequestOptions<TBody> {
  method?: HttpMethod;
  body?: TBody;
  signal?: AbortSignal;
}

function isApiErrorBody(
  value: unknown,
): value is ApiErrorBody {
  if (
    typeof value !== "object" ||
    value === null ||
    !("error" in value)
  ) {
    return false;
  }

  const error = value.error;

  return (
    typeof error === "object" &&
    error !== null &&
    "code" in error &&
    typeof error.code === "string" &&
    "message" in error &&
    typeof error.message === "string"
  );
}

async function parseJsonSafely(
  response: Response,
): Promise<unknown> {
  const contentType =
    response.headers.get("content-type");

  if (!contentType?.includes("application/json")) {
    return null;
  }

  try {
    return await response.json();
  } catch {
    return null;
  }
}

export async function request<
  TResponse,
  TBody = never,
>(
  path: string,
  options: RequestOptions<TBody> = {},
): Promise<TResponse> {
  const {
    method = "GET",
    body,
    signal,
  } = options;

  let response: Response;

  try {
    response = await fetch(
      `${env.apiUrl}${path}`,
      {
        method,
        signal,
        headers:
          body === undefined
            ? {
                Accept: "application/json",
              }
            : {
                Accept: "application/json",
                "Content-Type": "application/json",
              },
        body:
          body === undefined
            ? undefined
            : JSON.stringify(body),
      },
    );
  } catch (error) {
    if (
      error instanceof DOMException &&
      error.name === "AbortError"
    ) {
      throw error;
    }

    throw new ApiError({
      status: 0,
      code: "network_error",
      message:
        "The API could not be reached. Check your connection and try again.",
      cause: error,
    });
  }

  if (!response.ok) {
    const errorPayload =
      await parseJsonSafely(response);

    if (isApiErrorBody(errorPayload)) {
      throw new ApiError({
        status: response.status,
        code: errorPayload.error.code,
        message: errorPayload.error.message,
        fields: errorPayload.error.fields ?? [],
      });
    }

    throw new ApiError({
      status: response.status,
      code: "unexpected_api_error",
      message: `The request failed with status ${response.status}.`,
    });
  }

  if (response.status === 204) {
    return undefined as TResponse;
  }

  const payload = await parseJsonSafely(response);

  if (payload === null) {
    throw new ApiError({
      status: response.status,
      code: "invalid_api_response",
      message:
        "The API returned an unexpected response format.",
    });
  }

  return payload as TResponse;
}