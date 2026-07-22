export interface ApiErrorField {
  location: string[];
  message: string;
  type: string;
}

export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
    fields: ApiErrorField[] | null;
  };
}

interface ApiErrorOptions {
  status: number;
  code: string;
  message: string;
  fields?: ApiErrorField[];
  cause?: unknown;
}

export class ApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly fields: ApiErrorField[];

  constructor({
    status,
    code,
    message,
    fields = [],
    cause,
  }: ApiErrorOptions) {
    super(message, { cause });

    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.fields = fields;
  }

  getFieldMessage(fieldName: string): string | undefined {
    return this.fields.find((field) =>
      field.location.includes(fieldName),
    )?.message;
  }
}

export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError;
}