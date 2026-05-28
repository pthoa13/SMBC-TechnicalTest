"""Translation-specific exceptions."""


class TranslationError(Exception):
    """Base exception for translation failures."""


class LLMRateLimitError(TranslationError):
    """Raised when the remote LLM reports rate limiting."""


class InvalidLLMResponseError(TranslationError):
    """Raised when the remote LLM response cannot be validated."""


class TranslationCacheError(TranslationError):
    """Raised when the translation cache cannot be read or written."""


class LLMConfigurationError(TranslationError):
    """Raised when translation credentials or provider settings are missing."""


class LLMTransientError(TranslationError):
    """Raised when the remote LLM reports a retryable failure."""


class LLMNonRetryableError(TranslationError):
    """Raised when the remote LLM reports a non-retryable failure."""
