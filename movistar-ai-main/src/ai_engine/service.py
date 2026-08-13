"""Application orchestration for the local conversational core."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from datetime import datetime, timezone

from .context import ContextBuilder
from .domain import (
    ConversationEvent,
    ConversationSession,
    ConversationState,
    ConversationTurn,
    CopilotResponse,
    ErrorCode,
    ErrorDetail,
    GenerationTrace,
    GuidanceDraft,
    InterpretedObjection,
    ObjectionCategory,
    RecommendationContext,
    ResponseType,
    StrategyCode,
    StrategyDecision,
)
from .generation import ContentGenerationError
from .guardrails import ResponseValidationError, ResponseValidator, ValidationResult
from .ports import ContentGenerator, ObjectionInterpreter, SessionStore
from .state_machine import ConversationStateMachine, InvalidTransitionError
from .strategy import ConversationalStrategyPolicy


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class SalesCopilotService:
    """Coordinate context, state, strategy, generation, and validation."""

    def __init__(
        self,
        session_store: SessionStore,
        context_builder: ContextBuilder,
        state_machine: ConversationStateMachine,
        objection_interpreter: ObjectionInterpreter,
        strategy_policy: ConversationalStrategyPolicy,
        content_generator: ContentGenerator,
        response_validator: ResponseValidator,
        fallback_content_generator: ContentGenerator | None = None,
        clock: Callable[[], datetime] = _utc_now,
    ) -> None:
        self._sessions = session_store
        self._context_builder = context_builder
        self._state_machine = state_machine
        self._objection_interpreter = objection_interpreter
        self._strategy_policy = strategy_policy
        self._content_generator = content_generator
        self._fallback_content_generator = fallback_content_generator
        self._response_validator = response_validator
        self._clock = clock

    def start_session(
        self,
        recommendation: RecommendationContext,
        conversation_id: str | None = None,
    ) -> CopilotResponse:
        now = self._clock()
        context = self._context_builder.build(recommendation)
        session = ConversationSession(
            conversation_id=(
                conversation_id or f"conv-{recommendation.recommendation_id}"
            ),
            context=context,
            state=ConversationState.CONTEXT_RECEIVED,
            state_updated_at=now,
        )
        self._sessions.create(session)

        if context.offer_knowledge is None:
            self._state_machine.transition(
                session, ConversationEvent.KNOWLEDGE_UNAVAILABLE, now
            )
            session.requires_human_review = True
            response = self._controlled_response(
                session=session,
                request_id=recommendation.source_request_id,
                in_reply_to_turn_id="session-start",
                code=ErrorCode.KNOWLEDGE_UNAVAILABLE,
                message=context.knowledge_issue or "Commercial knowledge is unavailable",
            )
            self._sessions.save(session)
            return response

        self._state_machine.transition(
            session, ConversationEvent.CONTEXT_VALIDATED, now
        )
        decision = StrategyDecision(
            code=StrategyCode.PRESENT_INITIAL_SPEECH,
            target_state=ConversationState.OPENING,
            rationale="La recomendación y el conocimiento de oferta fueron validados.",
        )
        try:
            draft, validation = self._generate_and_validate(
                session=session,
                decision=decision,
                generate=lambda generator: generator.generate_initial(session),
            )
        except ResponseValidationError as exc:
            response = self._guardrail_response(
                session,
                recommendation.source_request_id,
                "session-start",
                exc,
            )
            self._sessions.save(session)
            return response
        except ContentGenerationError as exc:
            response = self._generation_error_response(
                session,
                recommendation.source_request_id,
                "session-start",
                exc,
            )
            self._sessions.save(session)
            return response

        response = self._build_response(
            session=session,
            request_id=recommendation.source_request_id,
            in_reply_to_turn_id="session-start",
            draft=draft,
            objection=None,
            safety_flags=validation.safety_flags,
        )
        self._sessions.save(session)
        return response

    def handle_customer_turn(self, turn: ConversationTurn) -> CopilotResponse:
        if turn.speaker != "customer":
            raise ValueError("The current core accepts only customer turns")
        if not turn.text.strip():
            raise ValueError("Customer turn text cannot be empty")

        session = self._sessions.get(turn.conversation_id)
        if session.last_processed_turn_id == turn.turn_id:
            raise ValueError(f"Turn already processed: {turn.turn_id}")
        now = self._clock()
        self._prepare_for_customer_turn(session, now)

        objection = self._objection_interpreter.interpret(turn)
        session.turns.append(turn)
        session.detected_objections.append(objection)
        is_ambiguous = (
            objection.category is ObjectionCategory.OTRO
            or objection.confidence < 0.75
        )
        if not is_ambiguous and session.state is not ConversationState.OBJECTION_HANDLING:
            self._state_machine.transition(
                session, ConversationEvent.OBJECTION_DETECTED, now
            )

        decision = self._strategy_policy.decide(
            session.state, objection, session.context
        )
        self._apply_decision_transition(session, decision, now)
        session.used_strategies.append(decision.code)
        session.pending_clarification = (
            decision.target_state is ConversationState.CLARIFICATION
        )
        if decision.target_state is ConversationState.ESCALATION:
            session.requires_human_review = True

        try:
            draft, validation = self._generate_and_validate(
                session=session,
                decision=decision,
                generate=lambda generator: generator.generate_for_strategy(
                    session, objection, decision
                ),
            )
        except ResponseValidationError as exc:
            response = self._guardrail_response(
                session, turn.request_id, turn.turn_id, exc
            )
        except ContentGenerationError as exc:
            response = self._generation_error_response(
                session, turn.request_id, turn.turn_id, exc
            )
        else:
            error = None
            if decision.error_code is not None:
                error = ErrorDetail(
                    code=decision.error_code.value,
                    message=decision.rationale,
                )
            response = self._build_response(
                session=session,
                request_id=turn.request_id,
                in_reply_to_turn_id=turn.turn_id,
                draft=draft,
                objection=objection,
                safety_flags=validation.safety_flags,
                grounded=decision.code is not StrategyCode.ABSTAIN,
                error=error,
            )

        session.last_processed_turn_id = turn.turn_id
        self._sessions.save(session)
        return response

    def _prepare_for_customer_turn(
        self, session: ConversationSession, now: datetime
    ) -> None:
        if session.state is ConversationState.OPENING:
            self._state_machine.transition(
                session, ConversationEvent.CUSTOMER_TURN_RECEIVED, now
            )
        elif session.state is ConversationState.REBATE:
            self._state_machine.transition(
                session, ConversationEvent.CUSTOMER_TURN_RECEIVED, now
            )
        elif session.state not in {
            ConversationState.DISCOVERY,
            ConversationState.OFFER_PRESENTATION,
            ConversationState.OBJECTION_HANDLING,
            ConversationState.CLARIFICATION,
        }:
            raise InvalidTransitionError(
                session.state, ConversationEvent.CUSTOMER_TURN_RECEIVED
            )

    def _apply_decision_transition(
        self,
        session: ConversationSession,
        decision: StrategyDecision,
        now: datetime,
    ) -> None:
        event_by_target = {
            ConversationState.CLARIFICATION: ConversationEvent.CLARIFICATION_NEEDED,
            ConversationState.REBATE: ConversationEvent.AUTHORIZED_TACTIC_AVAILABLE,
            ConversationState.FOLLOW_UP: ConversationEvent.FOLLOW_UP_REQUESTED,
            ConversationState.ESCALATION: ConversationEvent.KNOWLEDGE_UNAVAILABLE,
        }
        event = event_by_target.get(decision.target_state)
        if event is None:
            raise ValueError(
                f"Unsupported strategy target state: {decision.target_state.value}"
            )
        self._state_machine.transition(session, event, now)

    def _build_response(
        self,
        session: ConversationSession,
        request_id: str,
        in_reply_to_turn_id: str,
        draft: GuidanceDraft,
        objection: InterpretedObjection | None,
        safety_flags: tuple[str, ...],
        grounded: bool = True,
        error: ErrorDetail | None = None,
    ) -> CopilotResponse:
        recommendation = session.recommendation
        return CopilotResponse(
            response_id=f"resp-{in_reply_to_turn_id}",
            request_id=request_id,
            conversation_id=session.conversation_id,
            in_reply_to_turn_id=in_reply_to_turn_id,
            created_at=self._clock(),
            response_type=draft.response_type,
            conversation_stage=session.state,
            recommendation_id=recommendation.recommendation_id,
            offer_id=recommendation.primary_offer.offer_id,
            guidance=draft,
            objection=objection,
            grounded=grounded,
            requires_human_review=session.requires_human_review,
            safety_flags=safety_flags,
            prompt_version=(
                draft.generation.prompt_version
                if draft.generation is not None
                else "deterministic-core-v2"
            ),
            knowledge_version=(
                f"{session.context.knowledge_version}+"
                f"{self._strategy_policy.playbook_version}"
            ),
            error=error,
        )

    def _controlled_response(
        self,
        session: ConversationSession,
        request_id: str,
        in_reply_to_turn_id: str,
        code: ErrorCode,
        message: str,
    ) -> CopilotResponse:
        recommendation = session.recommendation
        draft = GuidanceDraft(
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
                generator="controlled_response",
                prompt_version="deterministic-core-v2",
            ),
        )
        return self._build_response(
            session=session,
            request_id=request_id,
            in_reply_to_turn_id=in_reply_to_turn_id,
            draft=draft,
            objection=None,
            safety_flags=(code.value,),
            grounded=False,
            error=ErrorDetail(code=code.value, message=message),
        )

    def _guardrail_response(
        self,
        session: ConversationSession,
        request_id: str,
        in_reply_to_turn_id: str,
        error: ResponseValidationError,
    ) -> CopilotResponse:
        self._state_machine.transition(
            session, ConversationEvent.GUARDRAIL_BLOCKED, self._clock()
        )
        session.requires_human_review = True
        return self._controlled_response(
            session=session,
            request_id=request_id,
            in_reply_to_turn_id=in_reply_to_turn_id,
            code=error.code,
            message=str(error),
        )

    def _generate_and_validate(
        self,
        *,
        session: ConversationSession,
        decision: StrategyDecision,
        generate: Callable[[ContentGenerator], GuidanceDraft],
    ) -> tuple[GuidanceDraft, ValidationResult]:
        primary_draft: GuidanceDraft | None = None
        try:
            primary_draft = generate(self._content_generator)
            validation = self._response_validator.validate(
                session.context, decision, primary_draft
            )
            return primary_draft, validation
        except (ContentGenerationError, ResponseValidationError) as primary_error:
            if self._fallback_content_generator is None:
                raise
            failure = primary_error

        try:
            fallback_draft = generate(self._fallback_content_generator)
            fallback_draft = replace(
                fallback_draft,
                generation=self._fallback_trace(
                    fallback_draft=fallback_draft,
                    primary_draft=primary_draft,
                    primary_error=failure,
                ),
            )
            validation = self._response_validator.validate(
                session.context, decision, fallback_draft
            )
        except (ContentGenerationError, ResponseValidationError):
            raise

        return fallback_draft, replace(
            validation,
            safety_flags=validation.safety_flags + ("GENERATION_FALLBACK_USED",),
        )

    @staticmethod
    def _fallback_trace(
        *,
        fallback_draft: GuidanceDraft,
        primary_draft: GuidanceDraft | None,
        primary_error: ContentGenerationError | ResponseValidationError,
    ) -> GenerationTrace:
        fallback = fallback_draft.generation or GenerationTrace(
            generator="fallback",
            prompt_version="unknown",
        )
        primary = primary_draft.generation if primary_draft else None
        error_latency = (
            primary_error.latency_ms
            if isinstance(primary_error, ContentGenerationError)
            else None
        )
        return GenerationTrace(
            generator=f"{fallback.generator}_fallback",
            prompt_version=fallback.prompt_version,
            provider=primary.provider if primary else None,
            model=primary.model if primary else None,
            response_id=primary.response_id if primary else None,
            latency_ms=(primary.latency_ms if primary else error_latency),
            input_tokens=primary.input_tokens if primary else None,
            output_tokens=primary.output_tokens if primary else None,
            total_tokens=primary.total_tokens if primary else None,
            fallback_used=True,
            fallback_reason=f"{type(primary_error).__name__}: {primary_error}",
        )

    def _generation_error_response(
        self,
        session: ConversationSession,
        request_id: str,
        in_reply_to_turn_id: str,
        error: ContentGenerationError,
    ) -> CopilotResponse:
        self._state_machine.transition(
            session, ConversationEvent.GUARDRAIL_BLOCKED, self._clock()
        )
        session.requires_human_review = True
        return self._controlled_response(
            session=session,
            request_id=request_id,
            in_reply_to_turn_id=in_reply_to_turn_id,
            code=ErrorCode.GENERATION_UNAVAILABLE,
            message=str(error),
        )
