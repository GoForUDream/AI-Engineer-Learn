class PromptRunError(Exception):
    """Base exception for the prompt-run application."""


class PromptRunStorageError(PromptRunError):
    """Raised when prompt-run data cannot be persisted or loaded."""


class InvalidPromptRunDocumentError(PromptRunStorageError):
    """Raised when the stored JSON document is invalid or corrupted."""
