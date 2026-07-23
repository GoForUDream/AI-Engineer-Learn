import {
  UploadedFileList,
} from "../../entities/uploaded-file/ui/UploadedFileList";

import {
  useUploadedFiles,
} from "../../entities/uploaded-file/model/useUploadedFile";

import {
  FileUploadForm,
} from "../../features/file-upload/ui/FileUploadForm";

import {
  useDeleteUploadedFile,
} from "../../features/file-delete/model/useDeleteUploadedFile";

import {
  ApiError,
} from "../../shared/api/ApiError";

import {
  Alert,
} from "../../shared/ui/Alert";

import {
  LoadingIndicator,
} from "../../shared/ui/LoadingIndicator";


function getErrorMessage(
  error: unknown,
): string {
  if (error instanceof ApiError) {
    return error.message;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "An unexpected error occurred.";
}


export function FilesPage() {
  const filesQuery =
    useUploadedFiles();

  const deleteFile =
    useDeleteUploadedFile();

  return (
    <main className="page-container">
      <header className="page-header">
        <h1>Text file uploads</h1>

        <p>
          Upload and manage Markdown
          or plain-text files.
        </p>
      </header>

      <FileUploadForm />

      <section className="panel">
        <div className="section-header">
          <h2>Uploaded files</h2>

          <button
            type="button"
            className="secondary-button"
            disabled={
              filesQuery.isFetching
            }
            onClick={() =>
              void filesQuery.refetch()
            }
          >
            {filesQuery.isFetching
              ? "Refreshing…"
              : "Refresh"}
          </button>
        </div>

        {filesQuery.isPending && (
          <LoadingIndicator />
        )}

        {filesQuery.error && (
          <Alert variant="error">
            {getErrorMessage(
              filesQuery.error
            )}
          </Alert>
        )}

        {deleteFile.error && (
          <Alert variant="error">
            {getErrorMessage(
              deleteFile.error
            )}
          </Alert>
        )}

        {filesQuery.data && (
          <UploadedFileList
            files={filesQuery.data}
            isDeleting={
              deleteFile.isDeleting
            }
            onDelete={
              deleteFile.deleteFile
            }
          />
        )}
      </section>
    </main>
  );
}