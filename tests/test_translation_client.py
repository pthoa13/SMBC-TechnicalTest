import httpx
import pytest

from brightlearn_site.translation.client import (
    LLMClientConfig,
    OpenAICompatibleTranslationClient,
)
from brightlearn_site.translation.exceptions import (
    InvalidLLMResponseError,
    LLMConfigurationError,
    LLMNonRetryableError,
    LLMRateLimitError,
    LLMTransientError,
)


def _config(api_key: str = "test-key") -> LLMClientConfig:
    return LLMClientConfig(
        provider="openai",
        api_key=api_key,
        model="test-model",
        base_url="https://example.test/v1",
        timeout_seconds=10,
        max_completion_tokens=1200,
    )


def test_client_rejects_missing_api_key() -> None:
    client = OpenAICompatibleTranslationClient(_config(api_key=""))

    with pytest.raises(LLMConfigurationError):
        client.translate_summary("Translate this")


def test_client_returns_message_content(monkeypatch) -> None:
    captured_payload = {}

    def fake_post(*args, **kwargs):
        captured_payload.update(kwargs["json"])
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": '{"translations":{}}'}}]},
        )

    monkeypatch.setattr(httpx, "post", fake_post)

    client = OpenAICompatibleTranslationClient(_config())

    assert client.translate_summary("Translate this") == '{"translations":{}}'
    assert captured_payload["response_format"] == {"type": "json_object"}
    assert captured_payload["max_completion_tokens"] == 1200


def test_client_maps_429_to_rate_limit(monkeypatch) -> None:
    monkeypatch.setattr(httpx, "post", lambda *args, **kwargs: httpx.Response(429))

    client = OpenAICompatibleTranslationClient(_config())

    with pytest.raises(LLMRateLimitError):
        client.translate_summary("Translate this")


def test_client_maps_5xx_to_transient(monkeypatch) -> None:
    monkeypatch.setattr(httpx, "post", lambda *args, **kwargs: httpx.Response(503))

    client = OpenAICompatibleTranslationClient(_config())

    with pytest.raises(LLMTransientError):
        client.translate_summary("Translate this")


def test_client_maps_timeout_to_transient(monkeypatch) -> None:
    def fake_post(*args, **kwargs):
        raise httpx.TimeoutException("timeout")

    monkeypatch.setattr(httpx, "post", fake_post)

    client = OpenAICompatibleTranslationClient(_config())

    with pytest.raises(LLMTransientError):
        client.translate_summary("Translate this")


def test_client_maps_remote_protocol_error_to_transient(monkeypatch) -> None:
    def fake_post(*args, **kwargs):
        raise httpx.RemoteProtocolError("server disconnected")

    monkeypatch.setattr(httpx, "post", fake_post)

    client = OpenAICompatibleTranslationClient(_config())

    with pytest.raises(LLMTransientError):
        client.translate_summary("Translate this")


def test_client_maps_4xx_to_non_retryable(monkeypatch) -> None:
    monkeypatch.setattr(httpx, "post", lambda *args, **kwargs: httpx.Response(400))

    client = OpenAICompatibleTranslationClient(_config())

    with pytest.raises(LLMNonRetryableError):
        client.translate_summary("Translate this")


def test_client_maps_length_finish_reason_to_invalid_response(monkeypatch) -> None:
    monkeypatch.setattr(
        httpx,
        "post",
        lambda *args, **kwargs: httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "finish_reason": "length",
                        "message": {"content": "{\"translations\":{\"es\":\"truncated"},
                    }
                ]
            },
        ),
    )

    client = OpenAICompatibleTranslationClient(_config())

    with pytest.raises(InvalidLLMResponseError, match="max_completion_tokens"):
        client.translate_summary("Translate this")


def test_client_maps_content_filter_finish_reason_to_non_retryable(monkeypatch) -> None:
    monkeypatch.setattr(
        httpx,
        "post",
        lambda *args, **kwargs: httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "finish_reason": "content_filter",
                        "message": {"content": ""},
                    }
                ]
            },
        ),
    )

    client = OpenAICompatibleTranslationClient(_config())

    with pytest.raises(LLMNonRetryableError, match="content filtering"):
        client.translate_summary("Translate this")


def test_client_maps_invalid_response_json_to_non_retryable(monkeypatch) -> None:
    monkeypatch.setattr(
        httpx,
        "post",
        lambda *args, **kwargs: httpx.Response(200, content=b"not-json"),
    )

    client = OpenAICompatibleTranslationClient(_config())

    with pytest.raises(LLMNonRetryableError):
        client.translate_summary("Translate this")
