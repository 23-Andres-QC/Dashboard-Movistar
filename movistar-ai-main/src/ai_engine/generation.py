"""Provider-neutral contracts and errors for structured content generation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol


class ContentGenerationError(RuntimeError):
    """A content generator could not produce a usable structured draft."""

    def __init__(self, message: str, *, latency_ms: int | None = None) -> None:
        self.latency_ms = latency_ms
        super().__init__(message)


class ProviderUnavailableError(ContentGenerationError):
    """The configured provider could not complete the request."""


class ProviderResponseError(ContentGenerationError):
    """The provider completed but did not return usable structured output."""


@dataclass(frozen=True)
class TokenUsage:
    """Usage reported by a provider; values may be unavailable."""

    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None


@dataclass(frozen=True)
class StructuredGenerationRequest:
    """Minimal authorized input plus its required output schema."""

    instructions: str
    input_payload: Mapping[str, Any]
    schema_name: str
    response_schema: Mapping[str, Any]


@dataclass(frozen=True)
class StructuredGenerationResult:
    """Provider-neutral structured result and operational metadata."""

    payload: Mapping[str, Any]
    provider: str
    model: str
    response_id: str | None = None
    latency_ms: int | None = None
    usage: TokenUsage = TokenUsage()


class StructuredGenerationProvider(Protocol):
    """Generate one schema-constrained object without domain authority."""

    def generate(
        self, request: StructuredGenerationRequest
    ) -> StructuredGenerationResult: ...
