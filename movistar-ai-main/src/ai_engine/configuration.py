"""External configuration for optional provider integrations."""

from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum
from typing import Mapping


class ConfigurationError(ValueError):
    """Required external configuration is absent or invalid."""


class GeneratorMode(str, Enum):
    """Generation implementations available at the composition boundary."""

    DETERMINISTIC = "deterministic"
    OPENAI = "openai"


@dataclass(frozen=True)
class RuntimeSettings:
    """Provider selection for the AI Engine process."""

    generator_mode: GeneratorMode = GeneratorMode.DETERMINISTIC

    @classmethod
    def from_env(
        cls, environment: Mapping[str, str] | None = None
    ) -> RuntimeSettings:
        values = environment if environment is not None else os.environ
        raw_mode = values.get("AI_ENGINE_GENERATOR", "deterministic").strip().casefold()
        try:
            mode = GeneratorMode(raw_mode)
        except ValueError as exc:
            allowed = ", ".join(mode.value for mode in GeneratorMode)
            raise ConfigurationError(
                f"AI_ENGINE_GENERATOR must be one of: {allowed}"
            ) from exc
        return cls(generator_mode=mode)


@dataclass(frozen=True)
class ApiServerSettings:
    """Local HTTP transport settings."""

    host: str = "127.0.0.1"
    port: int = 8000
    cors_origins: tuple[str, ...] = ("*",)

    @classmethod
    def from_env(
        cls, environment: Mapping[str, str] | None = None
    ) -> ApiServerSettings:
        values = environment if environment is not None else os.environ
        host = values.get("AI_ENGINE_HOST", "127.0.0.1").strip()
        if not host:
            raise ConfigurationError("AI_ENGINE_HOST cannot be empty")
        raw_port = values.get("AI_ENGINE_PORT", "8000").strip()
        try:
            port = int(raw_port)
        except ValueError as exc:
            raise ConfigurationError("AI_ENGINE_PORT must be an integer") from exc
        if not 1 <= port <= 65535:
            raise ConfigurationError("AI_ENGINE_PORT must be between 1 and 65535")
        raw_origins = values.get("AI_ENGINE_CORS_ORIGINS", "*")
        origins = tuple(
            origin.strip() for origin in raw_origins.split(",") if origin.strip()
        )
        return cls(host=host, port=port, cors_origins=origins)


@dataclass(frozen=True)
class OpenAISettings:
    """Settings used only by the OpenAI adapter and its composition root."""

    api_key: str
    model: str
    timeout_seconds: float = 20.0

    @classmethod
    def from_env(
        cls, environment: Mapping[str, str] | None = None
    ) -> OpenAISettings:
        values = environment if environment is not None else os.environ
        api_key = values.get("OPENAI_API_KEY", "").strip()
        model = values.get("OPENAI_MODEL", "").strip()
        if not api_key:
            raise ConfigurationError("OPENAI_API_KEY is required for the real LLM demo")
        if not model:
            raise ConfigurationError(
                "OPENAI_MODEL is required; the model is not hardcoded by the AI Engine"
            )
        raw_timeout = values.get("AI_ENGINE_LLM_TIMEOUT_SECONDS", "20").strip()
        try:
            timeout_seconds = float(raw_timeout)
        except ValueError as exc:
            raise ConfigurationError(
                "AI_ENGINE_LLM_TIMEOUT_SECONDS must be numeric"
            ) from exc
        if timeout_seconds <= 0:
            raise ConfigurationError(
                "AI_ENGINE_LLM_TIMEOUT_SECONDS must be greater than zero"
            )
        return cls(
            api_key=api_key,
            model=model,
            timeout_seconds=timeout_seconds,
        )
