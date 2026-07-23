export const uploadedFileKeys = {
  all: ["uploaded-files"] as const,

  list: () => [
    ...uploadedFileKeys.all,
    "list",
  ] as const,

  detail: (fileId: string) => [
    ...uploadedFileKeys.all,
    "detail",
    fileId,
  ] as const,
};