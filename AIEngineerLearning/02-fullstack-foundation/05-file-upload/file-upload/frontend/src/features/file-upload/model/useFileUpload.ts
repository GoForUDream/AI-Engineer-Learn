import {
  useCallback,
  useRef,
  useState,
} from "react";

import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import { uploadedFileKeys } from "../../../entities/uploaded-file/model/uploadedFileKeys";
import { uploadFile } from "../api/uploadFile";


export function useFileUpload() {
  const queryClient = useQueryClient();

  const abortControllerRef =
    useRef<AbortController | null>(null);

  const [progress, setProgress] =
    useState(0);

  const mutation = useMutation({
    mutationKey: [
      "uploaded-files",
      "upload",
    ],

    mutationFn: async (file: File) => {
      const abortController =
        new AbortController();

      abortControllerRef.current =
        abortController;

      return uploadFile({
        file,
        signal: abortController.signal,
        onProgress: setProgress,
      });
    },

    onMutate: () => {
      setProgress(0);
    },

    onSuccess: async () => {
      setProgress(100);

      await queryClient.invalidateQueries({
        queryKey: uploadedFileKeys.list(),
      });
    },

    onSettled: () => {
      abortControllerRef.current = null;
    },
  });

  const cancel = useCallback(() => {
    abortControllerRef.current?.abort();
  }, []);

  const reset = useCallback(() => {
    mutation.reset();
    setProgress(0);
  }, [mutation]);

  return {
    upload: mutation.mutateAsync,
    cancel,
    reset,

    progress,

    isUploading: mutation.isPending,
    isSuccess: mutation.isSuccess,
    error: mutation.error,
    uploadedFile: mutation.data,
  };
}