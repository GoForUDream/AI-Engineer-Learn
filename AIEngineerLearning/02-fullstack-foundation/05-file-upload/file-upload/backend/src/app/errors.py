class ApplicationError(Exception):
    status_code = 500
    code = "internal_error"

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class InvalidUploadError(ApplicationError):
    status_code = 422
    code = "invalid_upload"


class UploadTooLargeError(ApplicationError):
    status_code = 413
    code = "upload_too_large"


class UploadedFileNotFoundError(ApplicationError):
    status_code = 404
    code = "uploaded_file_not_found"

    def __init__(self) -> None:
        super().__init__("Uploaded file was not found.")


class StorageConsistencyError(ApplicationError):
    status_code = 500
    code = "storage_consistency_error"
