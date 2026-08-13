"""Opt-in real LLM demo; never used by the default test suite."""

from __future__ import annotations

import json
from datetime import datetime

from .configuration import OpenAISettings
from .contract_dashboard_v01 import DashboardV01Formatter
from .contract_ml_v01 import MLV01Adapter
from .demo import _project_root, build_demo_service
from .deterministic import DeterministicContentGenerator
from .domain import ConversationTurn
from .llm import LlmContentGenerator
from .mocks import MockRecommendationSource
from .openai_responses import OpenAIResponsesProvider


def main() -> None:
    settings = OpenAISettings.from_env()
    provider = OpenAIResponsesProvider(
        model=settings.model,
        api_key=settings.api_key,
        timeout_seconds=settings.timeout_seconds,
    )
    llm_generator = LlmContentGenerator(provider)
    deterministic_fallback = DeterministicContentGenerator()
    root = _project_root()
    service = build_demo_service(
        root,
        content_generator=llm_generator,
        fallback_content_generator=deterministic_fallback,
    )
    recommendation = MLV01Adapter.parse(
        MockRecommendationSource(root / "fixtures" / "ml_recommendation_v01.json").load()
    )
    formatter = DashboardV01Formatter()

    initial = service.start_session(recommendation)
    print("=== SPEECH INICIAL LLM (CON FALLBACK SEGURO) ===")
    print(json.dumps(formatter.format(initial), indent=2, ensure_ascii=False))

    turn = ConversationTurn(
        request_id="req-demo-llm-turn-001",
        conversation_id=initial.conversation_id,
        turn_id="turn-demo-llm-001",
        speaker="customer",
        text="Me parece demasiado caro",
        timestamp=datetime.fromisoformat("2026-08-12T10:34:12-05:00"),
    )
    response = service.handle_customer_turn(turn)
    print("\n=== RESPUESTA LLM GROUNDED O FALLBACK DETERMINISTA ===")
    print(json.dumps(formatter.format(response), indent=2, ensure_ascii=False))

    generation = response.guidance.generation
    if generation is not None:
        print("\n=== TRAZA INTERNA DE GENERACIÓN ===")
        print(
            json.dumps(
                {
                    "generator": generation.generator,
                    "provider": generation.provider,
                    "model": generation.model,
                    "latency_ms": generation.latency_ms,
                    "input_tokens": generation.input_tokens,
                    "output_tokens": generation.output_tokens,
                    "total_tokens": generation.total_tokens,
                    "fallback_used": generation.fallback_used,
                    "fallback_reason": generation.fallback_reason,
                },
                indent=2,
                ensure_ascii=False,
            )
        )


if __name__ == "__main__":
    main()
