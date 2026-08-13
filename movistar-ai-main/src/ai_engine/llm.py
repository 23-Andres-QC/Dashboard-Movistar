"""LLM-backed implementation of the existing ContentGenerator port."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .domain import (
    CommercialClaim,
    ConversationSession,
    ConversationState,
    FactKind,
    GenerationTrace,
    GuidanceDraft,
    InterpretedObjection,
    ResponseType,
    StrategyCode,
    StrategyDecision,
)
from .generation import (
    ProviderResponseError,
    StructuredGenerationProvider,
    StructuredGenerationRequest,
    StructuredGenerationResult,
)


LLM_PROMPT_VERSION = "llm-content-v1"


class AuthorizedPromptContextBuilder:
    """Expose only facts and conversation fragments needed for one generation."""

    def __init__(self, max_recent_turns: int = 4) -> None:
        if max_recent_turns < 0:
            raise ValueError("max_recent_turns cannot be negative")
        self._max_recent_turns = max_recent_turns

    def build_initial(self, session: ConversationSession) -> dict[str, Any]:
        name_fact = self._fact_for_kind(session, FactKind.OFFER_NAME)
        decision = StrategyDecision(
            code=StrategyCode.PRESENT_INITIAL_SPEECH,
            target_state=ConversationState.OPENING,
            rationale="La estrategia de apertura fue fijada por la orquestación.",
        )
        return self._build(
            session=session,
            decision=decision,
            objection=None,
            allowed_facts=(name_fact,),
            task="initial_speech",
        )

    def build_for_strategy(
        self,
        session: ConversationSession,
        objection: InterpretedObjection,
        decision: StrategyDecision,
    ) -> dict[str, Any]:
        required_facts = ()
        if decision.tactic is not None:
            required_facts = tuple(
                self._fact_for_kind(session, kind)
                for kind in decision.tactic.required_fact_kinds
            )
        return self._build(
            session=session,
            decision=decision,
            objection=objection,
            allowed_facts=required_facts,
            task="strategy_response",
        )

    def _build(
        self,
        *,
        session: ConversationSession,
        decision: StrategyDecision,
        objection: InterpretedObjection | None,
        allowed_facts: Sequence[Any],
        task: str,
    ) -> dict[str, Any]:
        recommendation = session.recommendation
        offer = session.context.offer_knowledge
        if offer is None:
            raise ProviderResponseError("Authorized offer knowledge is unavailable")

        tactic: dict[str, Any] | None = None
        if decision.tactic is not None:
            tactic = {
                "tactic_id": decision.tactic.tactic_id,
                "summary": decision.tactic.summary,
                "response_template": decision.tactic.response_template,
                "follow_up_template": decision.tactic.follow_up_template,
                "demo_only": decision.tactic.demo_only,
                "approved": decision.tactic.approved,
            }

        recent_turns = session.turns[-self._max_recent_turns :]
        return {
            "task": task,
            "recommendation_authority": {
                "recommendation_id": recommendation.recommendation_id,
                "offer_id": recommendation.primary_offer.offer_id,
            },
            "conversation": {
                "state": session.state.value,
                "recent_turns": [
                    {"speaker": turn.speaker, "text": turn.text}
                    for turn in recent_turns
                ],
            },
            "objection": (
                None
                if objection is None
                else {
                    "category": objection.category.value,
                    "confidence": objection.confidence,
                    "customer_evidence": objection.customer_evidence,
                }
            ),
            "selected_strategy": {
                "code": decision.code.value,
                "target_state": decision.target_state.value,
                "rationale": decision.rationale,
            },
            "commercial_authority": {
                "active_offer": {
                    "offer_id": offer.offer_id,
                    "offer_name": offer.offer_name,
                },
                "allowed_catalog_facts": [
                    {
                        "fact_id": fact.fact_id,
                        "kind": fact.kind.value,
                        "display_value": fact.display_value,
                        "source_version": fact.source_version,
                        "demo_only": fact.demo_only,
                    }
                    for fact in allowed_facts
                ],
                "selected_playbook_tactic": tactic,
            },
            "constraints": {
                "keep_recommendation_id": recommendation.recommendation_id,
                "keep_offer_id": recommendation.primary_offer.offer_id,
                "keep_strategy": decision.code.value,
                "commercial_claims_must_reference_allowed_fact_ids": True,
                "do_not_add_discounts_benefits_prices_or_conditions": True,
                "customer_facing_language": "es-PE",
            },
        }

    @staticmethod
    def _fact_for_kind(session: ConversationSession, kind: FactKind) -> Any:
        offer = session.context.offer_knowledge
        fact = offer.fact_by_kind(kind) if offer else None
        if fact is None:
            raise ProviderResponseError(
                f"Authorized fact required for generation is unavailable: {kind.value}"
            )
        return fact


class LlmContentGenerator:
    """Generate wording only; all upstream decisions remain immutable inputs."""

    _instructions = """Eres un redactor de asistencia comercial para un asesor.
Tu única autoridad es el objeto de contexto autorizado recibido como entrada.
La recomendación, oferta, estado, objeción y estrategia ya fueron decididos por otros componentes y no puedes cambiarlos.
No calcules probabilidades, no recomiendes otra oferta y no inventes precios, descuentos, beneficios o condiciones.
Cada afirmación comercial debe aparecer en claims y referenciar un fact_id permitido.
Devuelve solo el objeto estructurado solicitado. El texto es una sugerencia para el asesor, no una confirmación de venta."""

    def __init__(
        self,
        provider: StructuredGenerationProvider,
        context_builder: AuthorizedPromptContextBuilder | None = None,
    ) -> None:
        self._provider = provider
        self._context_builder = context_builder or AuthorizedPromptContextBuilder()

    def generate_initial(self, session: ConversationSession) -> GuidanceDraft:
        decision = StrategyDecision(
            code=StrategyCode.PRESENT_INITIAL_SPEECH,
            target_state=ConversationState.OPENING,
            rationale="La estrategia de apertura fue fijada por la orquestación.",
        )
        context = self._context_builder.build_initial(session)
        return self._generate(
            context=context,
            expected_response_type=ResponseType.INITIAL_SPEECH,
            decision=decision,
            session=session,
        )

    def generate_for_strategy(
        self,
        session: ConversationSession,
        objection: InterpretedObjection,
        strategy: StrategyDecision,
    ) -> GuidanceDraft:
        if strategy.code is StrategyCode.ABSTAIN:
            return self._abstention_draft(session)
        if strategy.tactic is not None:
            expected_response_type = strategy.tactic.response_type
        elif strategy.code is StrategyCode.ASK_CLARIFYING_QUESTION:
            expected_response_type = ResponseType.OBJECTION_RESPONSE
        else:
            raise ProviderResponseError(
                f"Unsupported strategy for LLM generation: {strategy.code.value}"
            )
        context = self._context_builder.build_for_strategy(
            session, objection, strategy
        )
        return self._generate(
            context=context,
            expected_response_type=expected_response_type,
            decision=strategy,
            session=session,
        )

    def _generate(
        self,
        *,
        context: Mapping[str, Any],
        expected_response_type: ResponseType,
        decision: StrategyDecision,
        session: ConversationSession,
    ) -> GuidanceDraft:
        request = StructuredGenerationRequest(
            instructions=self._instructions,
            input_payload=context,
            schema_name="sales_copilot_guidance",
            response_schema=self._response_schema(
                session=session,
                expected_response_type=expected_response_type,
                expected_strategy=decision.code,
            ),
        )
        result = self._provider.generate(request)
        return self._to_draft(result)

    @staticmethod
    def _response_schema(
        *,
        session: ConversationSession,
        expected_response_type: ResponseType,
        expected_strategy: StrategyCode,
    ) -> dict[str, Any]:
        recommendation = session.recommendation
        nullable_string = {"anyOf": [{"type": "string"}, {"type": "null"}]}
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "response_type": {
                    "type": "string",
                    "enum": [expected_response_type.value],
                },
                "recommended_action": {
                    "type": "string",
                    "enum": [expected_strategy.value],
                },
                "summary": {"type": "string"},
                "suggested_customer_response": nullable_string,
                "follow_up_question": nullable_string,
                "grounding_fact_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "claims": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "text": {"type": "string"},
                            "fact_id": {"type": "string"},
                        },
                        "required": ["text", "fact_id"],
                    },
                },
                "source_recommendation_id": {
                    "type": "string",
                    "enum": [recommendation.recommendation_id],
                },
                "source_offer_id": {
                    "type": "string",
                    "enum": [recommendation.primary_offer.offer_id],
                },
            },
            "required": [
                "response_type",
                "recommended_action",
                "summary",
                "suggested_customer_response",
                "follow_up_question",
                "grounding_fact_ids",
                "claims",
                "source_recommendation_id",
                "source_offer_id",
            ],
        }

    @classmethod
    def _to_draft(cls, result: StructuredGenerationResult) -> GuidanceDraft:
        payload = result.payload
        required = {
            "response_type",
            "recommended_action",
            "summary",
            "suggested_customer_response",
            "follow_up_question",
            "grounding_fact_ids",
            "claims",
            "source_recommendation_id",
            "source_offer_id",
        }
        if set(payload) != required:
            raise ProviderResponseError(
                "Structured output contains missing or unexpected fields",
                latency_ms=result.latency_ms,
            )
        try:
            response_type = ResponseType(cls._required_string(payload, "response_type"))
            action = StrategyCode(cls._required_string(payload, "recommended_action"))
            summary = cls._required_string(payload, "summary")
            source_recommendation_id = cls._required_string(
                payload, "source_recommendation_id"
            )
            source_offer_id = cls._required_string(payload, "source_offer_id")
            customer_response = cls._nullable_string(
                payload, "suggested_customer_response"
            )
            follow_up = cls._nullable_string(payload, "follow_up_question")
            grounding_fact_ids = cls._string_tuple(payload, "grounding_fact_ids")
            claims = cls._claims(payload.get("claims"))
        except (TypeError, ValueError) as exc:
            raise ProviderResponseError(
                f"Structured output failed local validation: {exc}",
                latency_ms=result.latency_ms,
            ) from exc

        usage = result.usage
        return GuidanceDraft(
            response_type=response_type,
            recommended_action=action,
            summary=summary,
            suggested_customer_response=customer_response,
            follow_up_question=follow_up,
            grounding_fact_ids=grounding_fact_ids,
            claims=claims,
            source_recommendation_id=source_recommendation_id,
            source_offer_id=source_offer_id,
            generation=GenerationTrace(
                generator="llm",
                prompt_version=LLM_PROMPT_VERSION,
                provider=result.provider,
                model=result.model,
                response_id=result.response_id,
                latency_ms=result.latency_ms,
                input_tokens=usage.input_tokens,
                output_tokens=usage.output_tokens,
                total_tokens=usage.total_tokens,
            ),
        )

    @staticmethod
    def _required_string(payload: Mapping[str, Any], field: str) -> str:
        value = payload.get(field)
        if not isinstance(value, str) or not value.strip():
            raise TypeError(f"{field} must be a non-empty string")
        return value

    @staticmethod
    def _nullable_string(payload: Mapping[str, Any], field: str) -> str | None:
        value = payload.get(field)
        if value is not None and not isinstance(value, str):
            raise TypeError(f"{field} must be a string or null")
        return value

    @staticmethod
    def _string_tuple(payload: Mapping[str, Any], field: str) -> tuple[str, ...]:
        value = payload.get(field)
        if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
            raise TypeError(f"{field} must be an array of strings")
        return tuple(value)

    @staticmethod
    def _claims(value: Any) -> tuple[CommercialClaim, ...]:
        if not isinstance(value, list):
            raise TypeError("claims must be an array")
        claims: list[CommercialClaim] = []
        for item in value:
            if not isinstance(item, Mapping) or set(item) != {"text", "fact_id"}:
                raise TypeError("each claim must contain only text and fact_id")
            text = item.get("text")
            fact_id = item.get("fact_id")
            if not isinstance(text, str) or not text.strip():
                raise TypeError("claim text must be a non-empty string")
            if not isinstance(fact_id, str) or not fact_id.strip():
                raise TypeError("claim fact_id must be a non-empty string")
            claims.append(CommercialClaim(text=text, fact_id=fact_id))
        return tuple(claims)

    @staticmethod
    def _abstention_draft(session: ConversationSession) -> GuidanceDraft:
        recommendation = session.recommendation
        return GuidanceDraft(
            response_type=ResponseType.INSUFFICIENT_CONTEXT,
            recommended_action=StrategyCode.ABSTAIN,
            summary="No hay conocimiento autorizado suficiente para responder.",
            suggested_customer_response=None,
            follow_up_question=None,
            grounding_fact_ids=(),
            claims=(),
            source_recommendation_id=recommendation.recommendation_id,
            source_offer_id=recommendation.primary_offer.offer_id,
            generation=GenerationTrace(
                generator="deterministic_abstention",
                prompt_version=LLM_PROMPT_VERSION,
            ),
        )
