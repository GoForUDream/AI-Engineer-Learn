import axios from "axios";
import { z } from "zod";


const ApiErrorResponseSchema = z.object({
  code: z.string(),
  message: z.string(),
});


export class ApiError extends Error {
    public readonly status: number;
    public readonly code: string;

  constructor(
    status: number,
    code: string,
    message: string,
    options?: ErrorOptions,
  ) {
    super(message, options);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}


export function toApiError(
  error: unknown,
): ApiError {
  if (error instanceof ApiError) {
    return error;
  }

  if (axios.isCancel(error)) {
    return new ApiError(
      0,
      "request_cancelled",
      "The request was cancelled.",
      {
        cause: error,
      },
    );
  }

  if (axios.isAxiosError(error)) {
    const parsedBody =
      ApiErrorResponseSchema.safeParse(
        error.response?.data,
      );

    return new ApiError(
      error.response?.status ?? 0,
      parsedBody.success
        ? parsedBody.data.code
        : "request_failed",
      parsedBody.success
        ? parsedBody.data.message
        : error.response
          ? `Request failed with status ${error.response.status}.`
          : "Could not connect to the server.",
      {
        cause: error,
      },
    );
  }

  if (error instanceof Error) {
    return new ApiError(
      0,
      "unexpected_error",
      error.message,
      {
        cause: error,
      },
    );
  }

  return new ApiError(
    0,
    "unexpected_error",
    "An unexpected error occurred.",
  );
}