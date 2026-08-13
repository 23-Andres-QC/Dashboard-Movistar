"""Tests for the local conversational core and provisional adapters."""

from __future__ import annotations

import copy
import json
import unittest
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

from ai_engine.context import ContextBuilder
from ai_engine.contract_dashboard_v01 import DashboardV01Formatter
from ai_engine.contract_ml_v01 import MLContractError, MLV01Adapter
from ai_engine.deterministic import (
    DeterministicContentGenerator,
    RuleBasedObjectionInterpreter,
)
from ai_engine.domain import (
    ConversationEvent,
    ConversationSession,
    ConversationState,
    ConversationTurn,
    ErrorCode,
    GuidanceDraft,
    ObjectionCategory,
    RecommendationContext,
    ResponseType,
    StrategyCode,
)
from ai_engine.guardrails import ResponseValidator
from ai_engine.knowledge import CsvDemoCatalog, JsonDemoPlaybook
from ai_engine.mocks import InMemorySessionStore, MockRecommendationSource
from ai_engine.ports import ContentGenerator
from ai_engine.service import SalesCopilotService
from ai_engine.state_machine import ConversationStateMachine, InvalidTransitionError
from ai_engine.strategy import ConversationalStrategyPolicy


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ML_FIXTURE = PROJECT_ROOT / "fixtures" / "ml_recommendation_v01.json"
PLAYBOOK_FIXTURE = PROJECT_ROOT / "fixtures" / "demo_playbook_v01.json"
CATALOG_PATH = PROJECT_ROOT / "fixtures" / "demo_catalog_v01.csv"
FIXED_TIME = datetime(2026, 8, 12, 15, 35, tzinfo=timezone.utc)


def load_recommendation() -> RecommendationContext:
    return MLV01Adapter.parse(MockRecommendationSource(ML_FIXTURE).load())


def build_service(
    *,
    store: InMemorySessionStore | None = None,
    generator: ContentGenerator | None = None,
) -> tuple[SalesCopilotService, InMemorySessionStore]:
    resolved_store = store or InMemorySessionStore()
    catalog = CsvDemoCatalog(CATALOG_PATH)
    playbook = JsonDemoPlaybook(PLAYBOOK_FIXTURE)
    service = SalesCopilotService(
        session_store=resolved_store,
        context_builder=ContextBuilder(catalog),
        state_machine=ConversationStateMachine(),
        objection_interpreter=RuleBasedObjectionInterpreter(),
        strategy_policy=ConversationalStrategyPolicy(playbook),
        content_generator=generator or DeterministicContentGenerator(),
        response_validator=ResponseValidator(),
        clock=lambda: FIXED_TIME,
    )
    return service, resolved_store


def customer_turn(
    conversation_id: str,
    text: str,
    *,
    turn_id: str = "turn-001",
) -> ConversationTurn:
    return ConversationTurn(
        request_id=f"request-{turn_id}",
        conversation_id=conversation_id,
        turn_id=turn_id,
        speaker="customer",
        text=text,
        timestamp=FIXED_TIME,
    )


class UnauthorizedBenefitGenerator(DeterministicContentGenerator):
    """Test double that attempts to introduce an ungrounded discount."""

    def generate_initial(self, session: ConversationSession) -> GuidanceDraft:
        draft = super().generate_initial(session)
        return replace(
            draft,
            suggested_customer_response="Esta oferta incluye 50% de descuento.",
            grounding_fact_ids=(),
            claims=(),
        )


class RecommendationMutatingGenerator(DeterministicContentGenerator):
    """Test double that attempts to replace the ML-selected offer."""

    def generate_initial(self, session: ConversationSession) -> GuidanceDraft:
        draft = super().generate_initial(session)
        return replace(draft, source_offer_id="OF003")


class ConversationalCoreTests(unittest.TestCase):
    def test_opening_builds_context_and_grounds_initial_speech(self) -> None:
        service, store = build_service()
        initial = service.start_session(load_recommendation())

        self.assertEqual(initial.conversation_stage, ConversationState.OPENING)
        self.assertEqual(
            initial.guidance.recommended_action,
            StrategyCode.PRESENT_INITIAL_SPEECH,
        )
        self.assertEqual(initial.offer_id, "OF004")
        self.assertEqual(
            initial.guidance.grounding_fact_ids,
            ("demo_catalog:OF004:name",),
        )
        self.assertIn("DEMO_CATALOG_NOT_OFFICIAL", initial.safety_flags)
        self.assertTrue(initial.grounded)

        session = store.get(initial.conversation_id)
        self.assertEqual(session.state, ConversationState.OPENING)
        self.assertEqual(len(session.transitions), 1)
        self.assertEqual(
            session.transitions[0].event, ConversationEvent.CONTEXT_VALIDATED
        )

    def test_price_objection_uses_grounded_demo_tactic(self) -> None:
        service, store = build_service()
        initial = service.start_session(load_recommendation())
        response = service.handle_customer_turn(
            customer_turn(initial.conversation_id, "Me parece demasiado caro")
        )

        self.assertEqual(response.conversation_stage, ConversationState.REBATE)
        self.assertEqual(response.response_type, ResponseType.REBATE)
        self.assertIsNotNone(response.objection)
        assert response.objection is not None
        self.assertEqual(response.objection.category, ObjectionCategory.PRECIO)
        self.assertEqual(
            response.guidance.recommended_action, StrategyCode.REFRAME_VALUE
        )
        self.assertIn("S/ 99.90", response.guidance.suggested_customer_response or "")
        self.assertEqual(
            set(response.guidance.grounding_fact_ids),
            {
                "demo_catalog:OF004:name",
                "demo_catalog:OF004:monthly_price",
            },
        )
        self.assertIn("DEMO_PLAYBOOK_NOT_APPROVED", response.safety_flags)
        self.assertEqual(store.get(initial.conversation_id).state, ConversationState.REBATE)

    def test_bad_moment_objection_moves_to_follow_up(self) -> None:
        service, _ = build_service()
        initial = service.start_session(load_recommendation())
        response = service.handle_customer_turn(
            customer_turn(initial.conversation_id, "Ahora no puedo, mejor después")
        )

        self.assertEqual(response.conversation_stage, ConversationState.FOLLOW_UP)
        self.assertEqual(response.response_type, ResponseType.SCHEDULE_FOLLOWUP)
        self.assertEqual(
            response.guidance.recommended_action, StrategyCode.PROPOSE_FOLLOW_UP
        )
        assert response.objection is not None
        self.assertEqual(response.objection.category, ObjectionCategory.MAL_MOMENTO)

    def test_ambiguous_objection_requests_clarification(self) -> None:
        service, store = build_service()
        initial = service.start_session(load_recommendation())
        response = service.handle_customer_turn(
            customer_turn(initial.conversation_id, "No sé, tendría que verlo")
        )

        self.assertEqual(response.conversation_stage, ConversationState.CLARIFICATION)
        self.assertEqual(
            response.guidance.recommended_action,
            StrategyCode.ASK_CLARIFYING_QUESTION,
        )
        self.assertTrue(store.get(initial.conversation_id).pending_clarification)

    def test_state_machine_accepts_valid_and_rejects_invalid_transition(self) -> None:
        service, store = build_service()
        initial = service.start_session(load_recommendation())
        session = store.get(initial.conversation_id)
        machine = ConversationStateMachine()

        machine.transition(session, ConversationEvent.OFFER_PRESENTED, FIXED_TIME)
        self.assertEqual(session.state, ConversationState.OFFER_PRESENTATION)

        with self.assertRaises(InvalidTransitionError):
            machine.transition(session, ConversationEvent.CONTEXT_VALIDATED, FIXED_TIME)
        self.assertEqual(session.state, ConversationState.OFFER_PRESENTATION)

    def test_missing_offer_knowledge_returns_controlled_abstention(self) -> None:
        recommendation = load_recommendation()
        unknown_offer = replace(
            recommendation.primary_offer,
            offer_id="OF999",
            offer_name="Oferta inexistente",
        )
        recommendation = replace(recommendation, primary_offer=unknown_offer)
        service, store = build_service()

        response = service.start_session(recommendation)

        self.assertEqual(response.conversation_stage, ConversationState.ESCALATION)
        self.assertEqual(response.response_type, ResponseType.INSUFFICIENT_CONTEXT)
        self.assertEqual(response.guidance.recommended_action, StrategyCode.ABSTAIN)
        self.assertFalse(response.grounded)
        self.assertTrue(response.requires_human_review)
        self.assertIsNotNone(response.error)
        assert response.error is not None
        self.assertEqual(response.error.code, ErrorCode.KNOWLEDGE_UNAVAILABLE.value)
        self.assertEqual(store.get(response.conversation_id).recommendation.primary_offer.offer_id, "OF999")
        serialized = DashboardV01Formatter().format(response)
        self.assertEqual(serialized["error"]["code"], "KNOWLEDGE_UNAVAILABLE")

    def test_missing_playbook_tactic_abstains_instead_of_inventing(self) -> None:
        service, _ = build_service()
        initial = service.start_session(load_recommendation())

        response = service.handle_customer_turn(
            customer_turn(initial.conversation_id, "No confío en esa propuesta")
        )

        self.assertEqual(response.conversation_stage, ConversationState.ESCALATION)
        self.assertEqual(response.guidance.recommended_action, StrategyCode.ABSTAIN)
        self.assertIsNotNone(response.error)
        assert response.error is not None
        self.assertEqual(response.error.code, ErrorCode.KNOWLEDGE_UNAVAILABLE.value)

    def test_unauthorized_discount_is_blocked_by_guardrail(self) -> None:
        service, store = build_service(generator=UnauthorizedBenefitGenerator())

        response = service.start_session(load_recommendation())

        self.assertEqual(response.conversation_stage, ConversationState.ESCALATION)
        self.assertEqual(response.guidance.recommended_action, StrategyCode.ABSTAIN)
        self.assertIsNone(response.guidance.suggested_customer_response)
        self.assertIsNotNone(response.error)
        assert response.error is not None
        self.assertEqual(
            response.error.code,
            ErrorCode.UNAUTHORIZED_COMMERCIAL_CLAIM.value,
        )
        self.assertEqual(store.get(response.conversation_id).state, ConversationState.ESCALATION)

    def test_attempt_to_change_ml_offer_is_blocked(self) -> None:
        service, _ = build_service(generator=RecommendationMutatingGenerator())

        response = service.start_session(load_recommendation())

        self.assertEqual(response.offer_id, "OF004")
        self.assertEqual(response.recommendation_id, "rec-demo-001")
        self.assertEqual(response.conversation_stage, ConversationState.ESCALATION)
        self.assertIsNotNone(response.error)
        assert response.error is not None
        self.assertEqual(
            response.error.code,
            ErrorCode.RECOMMENDATION_MUTATION_ATTEMPT.value,
        )

    def test_original_recommendation_and_offer_are_preserved(self) -> None:
        recommendation = load_recommendation()
        service, store = build_service()
        initial = service.start_session(recommendation)
        response = service.handle_customer_turn(
            customer_turn(initial.conversation_id, "Me parece demasiado caro")
        )

        session = store.get(initial.conversation_id)
        self.assertEqual(response.recommendation_id, "rec-demo-001")
        self.assertEqual(response.offer_id, "OF004")
        self.assertEqual(session.recommendation, recommendation)

    def test_core_is_deterministic_and_dashboard_v01_serializes_it(self) -> None:
        def run_once() -> dict[str, object]:
            service, _ = build_service()
            initial = service.start_session(load_recommendation())
            response = service.handle_customer_turn(
                customer_turn(initial.conversation_id, "Me parece demasiado caro")
            )
            return DashboardV01Formatter().format(response)

        first = run_once()
        second = run_once()

        self.assertEqual(first, second)
        self.assertEqual(first["contract_version"], "0.1")
        self.assertEqual(first["conversation_stage"], "rebate")
        self.assertEqual(first["objection"]["category"], "precio")
        self.assertEqual(
            first["advisor_guidance"]["recommended_action"], "REFRAME_VALUE"
        )
        self.assertEqual(first["grounding"]["offer_id"], "OF004")
        self.assertEqual(first["trace"]["recommendation_id"], "rec-demo-001")
        json.dumps(first, ensure_ascii=False)

    def test_invalid_ml_payload_is_rejected_at_external_adapter(self) -> None:
        payload = copy.deepcopy(MockRecommendationSource(ML_FIXTURE).load())
        del payload["request_id"]

        with self.assertRaisesRegex(MLContractError, "request_id is required"):
            MLV01Adapter.parse(payload)


if __name__ == "__main__":
    unittest.main()
