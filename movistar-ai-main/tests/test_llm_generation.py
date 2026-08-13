"""Offline tests for provider isolation, structured LLM output, and fallback."""

from __future__ import annotations

import json
import unittest
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from ai_engine.configuration import ConfigurationError, OpenAISettings
from ai_engine.context import ContextBuilder
from ai_engine.contract_dashboard_v01 import DashboardV01Formatter
from ai_engine.contract_ml_v01 import MLV01Adapter
from ai_engine.deterministic import (
    DeterministicContentGenerator,
    RuleBasedObjectionInterpreter,
)
from ai_engine.domain import (
    ConversationState,
    ConversationTurn,
    ErrorCode,
    StrategyCode,
)
from ai_engine.generation import (
    ProviderUnavailableError,
    StructuredGenerationRequest,
    StructuredGenerationResult,
    TokenUsage,
)
from ai_engine.guardrails import ResponseValidator
from ai_engine.knowledge import CsvDemoCatalog, JsonDemoPlaybook
from ai_engine.llm import LLM_PROMPT_VERSION, LlmContentGenerator
from ai_engine.mocks import (
    FakeStructuredGenerationProvider,
    InMemorySessionStore,
    MockRecommendationSource,
)
from ai_engine.openai_responses import OpenAIResponsesProvider
from ai_engine.ports import ContentGenerator
from ai_engine.service import SalesCopilotService
from ai_engine.state_machine import ConversationStateMachine
from ai_engine.strategy import ConversationalStrategyPolicy


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIXED_TIME = datetime(2026, 8, 12, 15, 35, tzinfo=timezone.utc)


def load_recommendation():
    return MLV01Adapter.parse(
        MockRecommendationSource(
            PROJECT_ROOT / "fixtures" / "ml_recommendation_v01.json"
        ).load()
    )


def build_service(
    generator: ContentGenerator,
    *,
    fallback: ContentGenerator | None = None,
) -> SalesCopilotService:
    catalog = CsvDemoCatalog(
        PROJECT_ROOT / "fixtures" / "demo_catalog_v01.csv"
    )
    playbook = JsonDemoPlaybook(
        PROJECT_ROOT / "fixtures" / "demo_playbook_v01.json"
    )
    return SalesCopilotService(
        session_store=InMemorySessionStore(),
        context_builder=ContextBuilder(catalog),
        state_machine=ConversationStateMachine(),
        objection_interpreter=RuleBasedObjectionInterpreter(),
        strategy_policy=ConversationalStrategyPolicy(playbook),
        content_generator=generator,
        fallback_content_generator=fallback,
        response_validator=ResponseValidator(),
        clock=lambda: FIXED_TIME,
    )


def customer_turn(conversation_id: str, text: str) -> ConversationTurn:
    return ConversationTurn(
        request_id="request-turn-llm",
        conversation_id=conversation_id,
        turn_id="turn-llm",
        speaker="customer",
        text=text,
        timestamp=FIXED_TIME,
    )


def result(payload: dict[str, Any]) -> StructuredGenerationResult:
    return StructuredGenerationResult(
        payload=payload,
        provider="fake-provider",
        model="fake-model",
        response_id="fake-response-id",
        latency_ms=37,
        usage=TokenUsage(input_tokens=101, output_tokens=42, total_tokens=143),
    )


def initial_payload() -> dict[str, Any]:
    return {
        "response_type": "initial_speech",
        "recommended_action": "PRESENT_INITIAL_SPEECH",
        "summary": "Presentar la oferta y abrir descubrimiento.",
        "suggested_customer_response": (
            "Quisiera comentarle una opción: Plan Movil Ilimitado."
        ),
        "follow_up_question": "¿Qué le gustaría mejorar de su servicio actual?",
        "grounding_fact_ids": ["demo_catalog:OF004:name"],
        "claims": [
            {
                "text": "Plan Movil Ilimitado",
                "fact_id": "demo_catalog:OF004:name",
            }
        ],
        "source_recommendation_id": "rec-demo-001",
        "source_offer_id": "OF004",
    }


def price_payload() -> dict[str, Any]:
    return {
        "response_type": "rebate",
        "recommended_action": "REFRAME_VALUE",
        "summary": "Reconocer la preocupación y aclarar el valor.",
        "suggested_customer_response": (
            "Entiendo su preocupación. Plan Movil Ilimitado tiene un precio mensual "
            "de S/ 99.90; revisemos si responde a lo que necesita."
        ),
        "follow_up_question": (
            "¿Le preocupa más el monto mensual o el valor que recibe?"
        ),
        "grounding_fact_ids": [
            "demo_catalog:OF004:name",
            "demo_catalog:OF004:monthly_price",
        ],
        "claims": [
            {
                "text": "Plan Movil Ilimitado",
                "fact_id": "demo_catalog:OF004:name",
            },
            {
                "text": "S/ 99.90",
                "fact_id": "demo_catalog:OF004:monthly_price",
            },
        ],
        "source_recommendation_id": "rec-demo-001",
        "source_offer_id": "OF004",
    }


class LlmContentGeneratorTests(unittest.TestCase):
    def test_valid_structured_generation_preserves_all_upstream_authorities(self) -> None:
        provider = FakeStructuredGenerationProvider(
            [result(initial_payload()), result(price_payload())]
        )
        service = build_service(
            LlmContentGenerator(provider),
            fallback=DeterministicContentGenerator(),
        )

        initial = service.start_session(load_recommendation())
        response = service.handle_customer_turn(
            customer_turn(initial.conversation_id, "Me parece demasiado caro")
        )

        self.assertEqual(response.conversation_stage, ConversationState.REBATE)
        self.assertEqual(response.recommendation_id, "rec-demo-001")
        self.assertEqual(response.offer_id, "OF004")
        self.assertEqual(response.guidance.recommended_action, StrategyCode.REFRAME_VALUE)
        self.assertNotIn("GENERATION_FALLBACK_USED", response.safety_flags)
        trace = response.guidance.generation
        self.assertIsNotNone(trace)
        assert trace is not None
        self.assertEqual(trace.generator, "llm")
        self.assertEqual(trace.provider, "fake-provider")
        self.assertEqual(trace.model, "fake-model")
        self.assertEqual(trace.total_tokens, 143)
        self.assertEqual(response.prompt_version, LLM_PROMPT_VERSION)

        serialized = DashboardV01Formatter().format(response)
        self.assertEqual(serialized["contract_version"], "0.1")
        self.assertEqual(serialized["trace"]["recommendation_id"], "rec-demo-001")
        self.assertNotIn("llm_provider", serialized["trace"])

    def test_context_sent_to_provider_is_minimal_and_authorized(self) -> None:
        provider = FakeStructuredGenerationProvider(
            [result(initial_payload()), result(price_payload())]
        )
        service = build_service(LlmContentGenerator(provider))

        initial = service.start_session(load_recommendation())
        service.handle_customer_turn(
            customer_turn(initial.conversation_id, "Me parece demasiado caro")
        )

        opening_context = provider.requests[0].input_payload
        self.assertEqual(
            opening_context["commercial_authority"]["allowed_catalog_facts"][0][
                "kind"
            ],
            "offer_name",
        )
        price_context = provider.requests[1].input_payload
        self.assertEqual(
            price_context["selected_strategy"]["code"], "REFRAME_VALUE"
        )
        self.assertEqual(price_context["objection"]["category"], "precio")
        self.assertEqual(
            price_context["recommendation_authority"],
            {"recommendation_id": "rec-demo-001", "offer_id": "OF004"},
        )
        self.assertEqual(
            {fact["kind"] for fact in price_context["commercial_authority"]["allowed_catalog_facts"]},
            {"offer_name", "monthly_price"},
        )
        self.assertEqual(
            price_context["conversation"]["recent_turns"],
            [{"speaker": "customer", "text": "Me parece demasiado caro"}],
        )
        serialized = json.dumps(price_context, ensure_ascii=False)
        for forbidden_field in (
            "profile_summary",
            "acceptance_probability",
            "alternatives",
            "model_version",
            "customer_id",
        ):
            self.assertNotIn(forbidden_field, serialized)

    def test_provider_unavailability_uses_deterministic_fallback(self) -> None:
        provider = FakeStructuredGenerationProvider(
            [ProviderUnavailableError("provider down", latency_ms=29)]
        )
        service = build_service(
            LlmContentGenerator(provider),
            fallback=DeterministicContentGenerator(),
        )

        response = service.start_session(load_recommendation())

        self.assertEqual(response.conversation_stage, ConversationState.OPENING)
        self.assertTrue(response.grounded)
        self.assertIn("GENERATION_FALLBACK_USED", response.safety_flags)
        trace = response.guidance.generation
        self.assertIsNotNone(trace)
        assert trace is not None
        self.assertTrue(trace.fallback_used)
        self.assertEqual(trace.generator, "deterministic_fallback")
        self.assertEqual(trace.latency_ms, 29)
        self.assertIn("ProviderUnavailableError", trace.fallback_reason or "")

    def test_invalid_structure_uses_deterministic_fallback(self) -> None:
        invalid = initial_payload()
        del invalid["claims"]
        provider = FakeStructuredGenerationProvider([result(invalid)])
        service = build_service(
            LlmContentGenerator(provider),
            fallback=DeterministicContentGenerator(),
        )

        response = service.start_session(load_recommendation())

        self.assertIn("GENERATION_FALLBACK_USED", response.safety_flags)
        self.assertEqual(response.guidance.generation.generator, "deterministic_fallback")
        self.assertIn(
            "Structured output contains",
            response.guidance.generation.fallback_reason or "",
        )

    def test_guardrail_violation_uses_fallback_instead_of_delivering_claim(self) -> None:
        invented = initial_payload()
        invented["suggested_customer_response"] = (
            "Plan Movil Ilimitado incluye 50% de descuento."
        )
        invented["grounding_fact_ids"] = ["fabricated:discount"]
        invented["claims"] = [
            {"text": "50% de descuento", "fact_id": "fabricated:discount"}
        ]
        provider = FakeStructuredGenerationProvider([result(invented)])
        service = build_service(
            LlmContentGenerator(provider),
            fallback=DeterministicContentGenerator(),
        )

        response = service.start_session(load_recommendation())

        self.assertIn("GENERATION_FALLBACK_USED", response.safety_flags)
        self.assertNotIn(
            "descuento",
            (response.guidance.suggested_customer_response or "").casefold(),
        )
        self.assertEqual(response.recommendation_id, "rec-demo-001")
        self.assertEqual(response.offer_id, "OF004")
        trace = response.guidance.generation
        self.assertIsNotNone(trace)
        assert trace is not None
        self.assertEqual(trace.provider, "fake-provider")
        self.assertEqual(trace.total_tokens, 143)
        self.assertIn("ResponseValidationError", trace.fallback_reason or "")

    def test_strategy_mutation_is_blocked_then_regenerated_by_baseline(self) -> None:
        mutated = price_payload()
        mutated["recommended_action"] = "ASK_CLARIFYING_QUESTION"
        provider = FakeStructuredGenerationProvider(
            [result(initial_payload()), result(mutated)]
        )
        service = build_service(
            LlmContentGenerator(provider),
            fallback=DeterministicContentGenerator(),
        )
        initial = service.start_session(load_recommendation())

        response = service.handle_customer_turn(
            customer_turn(initial.conversation_id, "Me parece demasiado caro")
        )

        self.assertEqual(response.guidance.recommended_action, StrategyCode.REFRAME_VALUE)
        self.assertIn("GENERATION_FALLBACK_USED", response.safety_flags)

    def test_provider_failure_without_fallback_abstains_safely(self) -> None:
        provider = FakeStructuredGenerationProvider(
            [ProviderUnavailableError("provider down")]
        )
        service = build_service(LlmContentGenerator(provider))

        response = service.start_session(load_recommendation())

        self.assertEqual(response.conversation_stage, ConversationState.ESCALATION)
        self.assertFalse(response.grounded)
        self.assertTrue(response.requires_human_review)
        self.assertIsNotNone(response.error)
        assert response.error is not None
        self.assertEqual(response.error.code, ErrorCode.GENERATION_UNAVAILABLE.value)


class OpenAIProviderAdapterTests(unittest.TestCase):
    def test_adapter_calls_responses_with_strict_schema_and_maps_usage(self) -> None:
        payload = initial_payload()

        class FakeResponses:
            def __init__(self) -> None:
                self.kwargs: dict[str, Any] | None = None

            def create(self, **kwargs: Any) -> Any:
                self.kwargs = kwargs
                return SimpleNamespace(
                    id="resp-openai-fake",
                    status="completed",
                    output_text=json.dumps(payload),
                    output=[],
                    usage=SimpleNamespace(
                        input_tokens=88,
                        output_tokens=31,
                        total_tokens=119,
                    ),
                )

        responses = FakeResponses()
        provider = OpenAIResponsesProvider(
            model="externally-configured-model",
            client=SimpleNamespace(responses=responses),
        )
        request = StructuredGenerationRequest(
            instructions="authorized instructions",
            input_payload={"minimum": "context"},
            schema_name="test_schema",
            response_schema={"type": "object"},
        )

        generated = provider.generate(request)

        self.assertEqual(generated.payload, payload)
        self.assertEqual(generated.model, "externally-configured-model")
        self.assertEqual(generated.usage.total_tokens, 119)
        assert responses.kwargs is not None
        self.assertFalse(responses.kwargs["store"])
        self.assertEqual(responses.kwargs["instructions"], "authorized instructions")
        self.assertEqual(
            responses.kwargs["text"]["format"],
            {
                "type": "json_schema",
                "name": "test_schema",
                "strict": True,
                "schema": {"type": "object"},
            },
        )

    def test_settings_require_external_key_and_model(self) -> None:
        with self.assertRaisesRegex(ConfigurationError, "OPENAI_API_KEY"):
            OpenAISettings.from_env({})
        with self.assertRaisesRegex(ConfigurationError, "OPENAI_MODEL"):
            OpenAISettings.from_env({"OPENAI_API_KEY": "test-only-not-a-key"})

        settings = OpenAISettings.from_env(
            {
                "OPENAI_API_KEY": "test-only-not-a-key",
                "OPENAI_MODEL": "configured-model",
                "AI_ENGINE_LLM_TIMEOUT_SECONDS": "7.5",
            }
        )
        self.assertEqual(settings.model, "configured-model")
        self.assertEqual(settings.timeout_seconds, 7.5)


if __name__ == "__main__":
    unittest.main()
