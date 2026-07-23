import {
  type ChangeEvent,
  useState,
} from "react";

import { zodResolver } from "@hookform/resolvers/zod";

import {
  Controller,
  useForm,
} from "react-hook-form";

import { ApiError } from "../../../shared/api/ApiError";
import { Alert } from "../../../shared/ui/Alert";

import {
  FileUploadSchema,
  type FileUploadInput,
} from "../model/fileUploadSchema";

import { useFileUpload } from "../model/useFileUpload";


export function FileUploadForm() {
  const [inputVersion, setInputVersion] =
    useState(0);

  const {
    upload,
    cancel,
    reset: resetUpload,
    progress,
    isUploading,
    isSuccess,
    error,
    uploadedFile,
  } = useFileUpload();

  const {
    control,
    handleSubmit,
    reset: resetForm,
    formState: {
      errors,
      isSubmitting,
    },
  } = useForm<FileUploadInput>({
    resolver: zodResolver(
      FileUploadSchema
    ),
  });

  async function submit(
    input: FileUploadInput,
  ) {
    await upload(input.file);

    resetForm();
    setInputVersion(
      (current) => current + 1
    );
  }

  function handleNewSelection() {
    resetUpload();
  }

  const errorMessage =
    error instanceof ApiError
      ? error.message
      : error instanceof Error
        ? error.message
        : null;

  return (
    <section className="panel">
      <h2>Upload a text file</h2>

      <p className="help-text">
        Accepted formats: .txt and .md.
        Maximum size: 5 MB.
      </p>

      <form
        className="upload-form"
        onSubmit={handleSubmit(submit)}
        noValidate
      >
        <Controller
          key={inputVersion}
          name="file"
          control={control}
          render={({ field }) => {
            function handleChange(
              event: ChangeEvent<HTMLInputElement>,
            ) {
              handleNewSelection();

              field.onChange(
                event.target.files?.[0],
              );
            }

            return (
              <input
                ref={field.ref}
                name={field.name}
                type="file"
                accept=".txt,.md,text/plain,text/markdown"
                disabled={isUploading}
                onBlur={field.onBlur}
                onChange={handleChange}
                aria-invalid={
                  errors.file
                    ? "true"
                    : "false"
                }
                aria-describedby={
                  errors.file
                    ? "file-error"
                    : undefined
                }
              />
            );
          }}
        />

        {errors.file && (
          <p
            id="file-error"
            className="field-error"
            role="alert"
          >
            {errors.file.message}
          </p>
        )}

        <div className="button-row">
          <button
            type="submit"
            disabled={
              isUploading ||
              isSubmitting
            }
          >
            {isUploading
              ? "Uploading…"
              : "Upload"}
          </button>

          {isUploading && (
            <button
              type="button"
              className="secondary-button"
              onClick={cancel}
            >
              Cancel
            </button>
          )}
        </div>
      </form>

      {isUploading && (
        <div
          className="upload-progress"
          aria-live="polite"
        >
          <progress
            value={progress}
            max={100}
          />

          <span>{progress}%</span>
        </div>
      )}

      {errorMessage && (
        <Alert variant="error">
          {errorMessage}
        </Alert>
      )}

      {isSuccess && uploadedFile && (
        <Alert variant="success">
          Uploaded{" "}
          {uploadedFile.originalName}.
        </Alert>
      )}
    </section>
  );
}