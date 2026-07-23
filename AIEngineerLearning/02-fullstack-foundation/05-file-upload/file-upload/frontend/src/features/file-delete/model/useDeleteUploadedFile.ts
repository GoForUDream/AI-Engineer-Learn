import {
  useMutation,
  useMutationState,
  useQueryClient,
} from "@tanstack/react-query";

import {
  deleteUploadedFile,
} from "../../../entities/uploaded-file/api/uploadedFilesApi";

import {
  type UploadedFile,
} from "../../../entities/uploaded-file/model/uploadedFile";

import {
  uploadedFileKeys,
} from "../../../entities/uploaded-file/model/uploadedFileKeys";


const deleteMutationKey = [
  "uploaded-files",
  "delete",
] as const;


interface DeleteContext {
  previousFiles:
    | UploadedFile[]
    | undefined;
}


export function useDeleteUploadedFile() {
  const queryClient = useQueryClient();

  const mutation = useMutation<
    void,
    Error,
    string,
    DeleteContext
  >({
    mutationKey: deleteMutationKey,

    mutationFn: deleteUploadedFile,

    onMutate: async (fileId) => {
      await queryClient.cancelQueries({
        queryKey: uploadedFileKeys.list(),
      });

      const previousFiles =
        queryClient.getQueryData<
          UploadedFile[]
        >(
          uploadedFileKeys.list(),
        );

      queryClient.setQueryData<
        UploadedFile[]
      >(
        uploadedFileKeys.list(),
        (currentFiles = []) =>
          currentFiles.filter(
            (file) =>
              file.id !== fileId,
          ),
      );

      return {
        previousFiles,
      };
    },

    onError: (
      _error,
      _fileId,
      context,
    ) => {
      if (context?.previousFiles) {
        queryClient.setQueryData(
          uploadedFileKeys.list(),
          context.previousFiles,
        );
      }
    },

    onSettled: async () => {
      await queryClient.invalidateQueries({
        queryKey:
          uploadedFileKeys.list(),
      });
    },
  });

  const pendingFileIds =
    useMutationState<string>({
      filters: {
        mutationKey: deleteMutationKey,
        status: "pending",
      },

      select: (pendingMutation) =>
        pendingMutation.state
          .variables as string,
    });

  return {
    deleteFile: mutation.mutateAsync,

    isDeleting: (fileId: string) =>
      pendingFileIds.includes(fileId),

    error: mutation.error,
    reset: mutation.reset,
  };
}