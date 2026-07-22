interface AppEnvironment {
  apiUrl: string;
}

function requireUrl(
  value: string | undefined,
  variableName: string,
): string {
  if (!value?.trim()) {
    throw new Error(
      `${variableName} is required. Check your frontend .env file.`,
    );
  }

  let parsedUrl: URL;

  try {
    parsedUrl = new URL(value);
  } catch {
    throw new Error(
      `${variableName} must be a valid absolute URL.`,
    );
  }

  if (!["http:", "https:"].includes(parsedUrl.protocol)) {
    throw new Error(
      `${variableName} must use HTTP or HTTPS.`,
    );
  }

  return parsedUrl.toString().replace(/\/$/, "");
}

export const env: AppEnvironment = Object.freeze({
  apiUrl: requireUrl(
    import.meta.env.VITE_API_URL,
    "VITE_API_URL",
  ),
});