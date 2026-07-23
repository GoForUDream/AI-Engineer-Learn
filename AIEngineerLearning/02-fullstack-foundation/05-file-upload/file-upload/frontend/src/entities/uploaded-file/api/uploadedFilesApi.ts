import { apiClient } from "../../../shared/api/apiClient";

import {
  parseUploadedFiles,
  type UploadedFile,
} from "../model/uploadedFile";


export async function getUploadedFiles(
  signal?: AbortSignal,
): Promise<UploadedFile[]> {
  const response = await apiClient.get<unknown>(
    "/files",
    {
      signal,
    },
  );

  return parseUploadedFiles(response.data);
}


export async function deleteUploadedFile(
  fileId: string,
): Promise<void> {
  await apiClient.delete(
    `/files/${encodeURIComponent(fileId)}`,
  );
}