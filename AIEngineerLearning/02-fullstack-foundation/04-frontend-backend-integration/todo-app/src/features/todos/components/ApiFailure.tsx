import {
  isApiError,
} from "../../../api/errors";

interface ApiFailureProps {
  error: unknown;
  onRetry?: () => void;
}

export function ApiFailure({
  error,
  onRetry,
}: ApiFailureProps) {
  const message = isApiError(error)
    ? error.message
    : "An unexpected error occurred.";

  return (
    <section
      className="panel error-state"
      role="alert"
    >
      <h2>Something went wrong</h2>
      <p>{message}</p>

      {onRetry ? (
        <button
          type="button"
          onClick={onRetry}
        >
          Try again
        </button>
      ) : null}
    </section>
  );
}