import { z } from "zod";


export const MAX_UPLOAD_BYTES =
  5 * 1024 * 1024;


const ALLOWED_EXTENSIONS = [
  ".txt",
  ".md",
] as const;


function hasAllowedExtension(
  filename: string,
): boolean {
  const normalizedName = filename.toLowerCase();

  return ALLOWED_EXTENSIONS.some(
    (extension) =>
      normalizedName.endsWith(extension),
  );
}


export const FileUploadSchema = z.object({
  file: z
    .instanceof(File, {
      message: "Select a file.",
    })
    .refine(
      (file) => hasAllowedExtension(file.name),
      {
        message:
          "Only .txt and .md files are allowed.",
      },
    )
    .refine(
      (file) => file.size > 0,
      {
        message:
          "Empty files are not allowed.",
      },
    )
    .refine(
      (file) =>
        file.size <= MAX_UPLOAD_BYTES,
      {
        message:
          "The file must not exceed 5 MB.",
      },
    ),
});


export type FileUploadInput = z.infer<
  typeof FileUploadSchema
>;