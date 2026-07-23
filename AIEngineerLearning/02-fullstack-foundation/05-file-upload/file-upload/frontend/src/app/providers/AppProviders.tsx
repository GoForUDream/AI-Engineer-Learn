import {
  type PropsWithChildren,
  useState,
} from "react";

import {
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query";

import { ApiError } from "../../shared/api/ApiError";


function shouldRetry(
  failureCount: number,
  error: Error,
): boolean {
  if (
    error instanceof ApiError &&
    error.status >= 400 &&
    error.status < 500
  ) {
    return false;
  }

  return failureCount < 2;
}


export function AppProviders({
  children,
}: PropsWithChildren) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            retry: shouldRetry,
            refetchOnWindowFocus: false,
            staleTime: 30_000,
          },

          mutations: {
            retry: false,
          },
        },
      }),
  );

  return (
    <QueryClientProvider
      client={queryClient}
    >
      {children}
    </QueryClientProvider>
  );
}