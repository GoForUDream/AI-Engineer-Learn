import { apiClient } from "../../../shared/api/apiClient";

import {
  parseUploadedFile,
  type UploadedFile,
} from "../../../entities/uploaded-file/model/uploadedFile";


export interface UploadFileOptions {
  file: File;
  signal?: AbortSignal;
  onProgress?: (percentage: number) => void;
}


export async function uploadFile({
  file,
  signal,
  onProgress,
}: UploadFileOptions): Promise<UploadedFile> {
  const body = new FormData();

  body.append("file", file);

  const response = await apiClient.post<unknown>(
    "/files",
    body,
    {
      signal,

      onUploadProgress: (event) => {
        if (!event.total) {
          return;
        }

        const percentage = Math.min(
          100,
          Math.round(
            (event.loaded / event.total) * 100,
          ),
        );

        onProgress?.(percentage);
      },
    },
  );

  return parseUploadedFile(response.data);
}