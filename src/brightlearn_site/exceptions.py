"""Shared application exceptions."""


class BrightLearnError(Exception):
    """Base exception for this project."""


class InputValidationError(BrightLearnError):
    """Raised when an input JSON file does not match the expected schema."""


class RenderError(BrightLearnError):
    """Raised when static page rendering fails."""


class BatchProcessingError(BrightLearnError):
    """Raised when a batch file cannot be processed."""
