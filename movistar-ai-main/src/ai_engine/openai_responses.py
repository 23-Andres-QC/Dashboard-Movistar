"""OpenAI Responses API adapter for provider-neutral structured generation."""

from __future__ import annotations

import json
from time import perf_counter
from typing import Any, Mapping

from .generation import (
    ProviderResponseError,
    ProviderUnavailableError,
    StructuredGenerationRequest,
    StructuredGenerationResult,
    TokenUsage,
)


class OpenAIResponsesProvider:
    """Call Responses API with a strict JSON Schema and no server-side storage."""

    provider_name = "openai"

    def __init__(
        self,
        *,
        model: str,
        api_key: str | None = None,
        timeout_seconds: float = 20.0,
        client: Any | None = None,
    ) -> None:
        if not model.strip():
            raise ValueError("An externally configured OpenAI model is required")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than zero")
        self.model = model
        self._api_key = api_key
        self._timeout_seconds = timeout_seconds
        self._client = client

    def generate(
        self, request: StructuredGenerationRequest
    ) -> StructuredGenerationResult:
        started = perf_counter()
        try:
            response = self._resolved_client().responses.create(
                model=self.model,
                instructions=request.instructions,
                input=json.dumps(
                    request.input_payload,
                    ensure_ascii=False,
                    separators=(",", ":"),
                ),
                text={
                    "format": {
                        "type": "json_schema",
                        "name": request.schema_name,
                        "strict": True,
                        "schema": dict(request.response_schema),
                    }
                },
                store=False,
            )
        except Exception as exc:
            latency_ms = round((perf_counter() - started) * 1000)
            raise ProviderUnavailableError(
                f"OpenAI Responses API call failed: {type(exc).__name__}",
                latency_ms=latency_ms,
            ) from exc

        latency_ms = round((perf_counter() - started) * 1000)
        refusal = self._refusal(response)
        if refusal is not None:
            raise ProviderResponseError(
                "OpenAI refused the structured generation request",
                latency_ms=latency_ms,
            )
        if self._value(response, "status") == "incomplete":
            raise ProviderResponseError(
                "OpenAI returned an incomplete response",
                latency_ms=latency_ms,
            )

        output_text = self._value(response, "output_text")
        if not isinstance(output_text, str) or not output_text.strip():
            raise ProviderResponseError(
                "OpenAI response did not include structured output text",
                latency_ms=latency_ms,
            )
        try:
            payload = json.loads(output_text)
        except json.JSONDecodeError as exc:
            raise ProviderResponseError(
                "OpenAI structured output was not valid JSON",
                latency_ms=latency_ms,
            ) from exc
        if not isinstance(payload, Mapping):
            raise ProviderResponseError(
                "OpenAI structured output must be a JSON object",
                latency_ms=latency_ms,
            )

        usage = self._value(response, "usage")
        return StructuredGenerationResult(
            payload=dict(payload),
            provider=self.provider_name,
            model=self.model,
            response_id=self._optional_string(self._value(response, "id")),
            latency_ms=latency_ms,
            usage=TokenUsage(
                input_tokens=self._optional_int(self._value(usage, "input_tokens")),
                output_tokens=self._optional_int(self._value(usage, "output_tokens")),
                total_tokens=self._optional_int(self._value(usage, "total_tokens")),
            ),
        )

    def _resolved_client(self) -> Any:
        if self._client is None:
            try:
                from openai import OpenAI
            except ImportError as exc:
                raise RuntimeError(
                    "Install the optional 'openai' dependency to use the real provider"
                ) from exc
            self._client = OpenAI(
                api_key=self._api_key,
                timeout=self._timeout_seconds,
            )
        return self._client

    @classmethod
    def _refusal(cls, response: Any) -> str | None:
        output = cls._value(response, "output")
        if not isinstance(output, list):
            return None
        for item in output:
            content = cls._value(item, "content")
            if not isinstance(content, list):
                continue
            for part in content:
                if cls._value(part, "type") == "refusal":
                    refusal = cls._value(part, "refusal")
                    return refusal if isinstance(refusal, str) else "refusal"
        return None

    @staticmethod
    def _value(container: Any, key: str) -> Any:
        if isinstance(container, Mapping):
            return container.get(key)
        return getattr(container, key, None)

    @staticmethod
    def _optional_int(value: Any) -> int | None:
        return value if isinstance(value, int) and not isinstance(value, bool) else None

    @staticmethod
    def _optional_string(value: Any) -> str | None:
        return value if isinstance(value, str) else None
