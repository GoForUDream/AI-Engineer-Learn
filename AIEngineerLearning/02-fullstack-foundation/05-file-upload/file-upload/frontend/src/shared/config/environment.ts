import { z } from "zod";


const EnvironmentSchema = z.object({
  VITE_API_URL: z
    .url("VITE_API_URL must be a valid URL."),
});


const parsedEnvironment =
  EnvironmentSchema.safeParse(import.meta.env);


if (!parsedEnvironment.success) {
  console.error(
    "Invalid frontend environment:",
    parsedEnvironment.error.flatten(),
  );

  throw new Error(
    "Frontend environment configuration is invalid.",
  );
}


export const environment = {
  apiUrl: parsedEnvironment.data.VITE_API_URL,
} as const;