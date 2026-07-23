import { useQuery } from "@tanstack/react-query";

import { getUploadedFiles } from "../api/uploadedFilesApi";
import { uploadedFileKeys } from "./uploadedFileKeys";


export function useUploadedFiles() {
  return useQuery({
    queryKey: uploadedFileKeys.list(),

    queryFn: ({ signal }) =>
      getUploadedFiles(signal),

    staleTime: 30_000,
  });
}