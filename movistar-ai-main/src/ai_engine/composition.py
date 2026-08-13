"""Composition root for local demos and the HTTP transport."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .configuration import GeneratorMode, OpenAISettings, RuntimeSettings
from .context import ContextBuilder
from .deterministic import (
    DeterministicContentGenerator,
    RuleBasedObjectionInterpreter,
)
from .guardrails import ResponseValidator
from .knowledge import CsvDemoCatalog, JsonDemoPlaybook
from .llm import LlmContentGenerator
from .mocks import InMemorySessionStore
from .openai_responses import OpenAIResponsesProvider
from .ports import ContentGenerator
from .service import SalesCopilotService
from .state_machine import ConversationStateMachine
from .strategy import ConversationalStrategyPolicy


@dataclass(frozen=True)
class EngineRuntime:
    """Process-local service plus the generation mode exposed by health checks."""

    service: SalesCopilotService
    generator_mode: GeneratorMode


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def build_runtime(
    settings: RuntimeSettings | None = None,
    *,
    root: Path | None = None,
) -> EngineRuntime:
    resolved_settings = settings or RuntimeSettings.from_env()
    resolved_root = root or project_root()
    deterministic = DeterministicContentGenerator()
    generator: ContentGenerator = deterministic
    fallback: ContentGenerator | None = None

    if resolved_settings.generator_mode is GeneratorMode.OPENAI:
        openai = OpenAISettings.from_env()
        generator = LlmContentGenerator(
            OpenAIResponsesProvider(
                model=openai.model,
                api_key=openai.api_key,
                timeout_seconds=openai.timeout_seconds,
            )
        )
        fallback = deterministic

    catalog = CsvDemoCatalog(resolved_root / "fixtures" / "demo_catalog_v01.csv")
    playbook = JsonDemoPlaybook(
        resolved_root / "fixtures" / "demo_playbook_v01.json"
    )
    service = SalesCopilotService(
        session_store=InMemorySessionStore(),
        context_builder=ContextBuilder(catalog),
        state_machine=ConversationStateMachine(),
        objection_interpreter=RuleBasedObjectionInterpreter(),
        strategy_policy=ConversationalStrategyPolicy(playbook),
        content_generator=generator,
        fallback_content_generator=fallback,
        response_validator=ResponseValidator(),
    )
    return EngineRuntime(
        service=service,
        generator_mode=resolved_settings.generator_mode,
    )
