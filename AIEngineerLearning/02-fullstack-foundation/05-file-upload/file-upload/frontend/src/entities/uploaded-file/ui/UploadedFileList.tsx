import type {
  UploadedFile,
} from "../model/uploadedFile";

import {
  formatBytes,
} from "../../../shared/lib/formatBytes";


interface UploadedFileListProps {
  files: UploadedFile[];
  isDeleting: (
    fileId: string,
  ) => boolean;
  onDelete: (
    fileId: string,
  ) => Promise<void>;
}


export function UploadedFileList({
  files,
  isDeleting,
  onDelete,
}: UploadedFileListProps) {
  if (files.length === 0) {
    return (
      <p>
        No files have been uploaded.
      </p>
    );
  }

  return (
    <ul className="file-list">
      {files.map((file) => {
        const deleting =
          isDeleting(file.id);

        return (
          <li
            key={file.id}
            className="file-list-item"
          >
            <div>
              <strong>
                {file.originalName}
              </strong>

              <p className="file-metadata">
                {formatBytes(
                  file.sizeBytes
                )}
                {" · "}
                {file.contentType}
                {" · "}
                {file.uploadedAt.toLocaleString()}
              </p>
            </div>

            <button
              type="button"
              className="danger-button"
              disabled={deleting}
              onClick={() =>
                void onDelete(file.id)
              }
            >
              {deleting
                ? "Deleting…"
                : "Delete"}
            </button>
          </li>
        );
      })}
    </ul>
  );
}