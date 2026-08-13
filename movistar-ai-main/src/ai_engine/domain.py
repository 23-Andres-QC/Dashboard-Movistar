"""Stable internal domain models, independent from provisional contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Mapping


class ConversationState(str, Enum):
    CONTEXT_RECEIVED = "context_received"
    OPENING = "opening"
    DISCOVERY = "discovery"
    OFFER_PRESENTATION = "offer_presentation"
    OBJECTION_HANDLING = "objection_handling"
    CLARIFICATION = "clarification"
    REBATE = "rebate"
    CLOSING_GUIDANCE = "closing_guidance"
    FOLLOW_UP = "follow_up"
    ESCALATION = "escalation"
    COMPLETED = "completed"
    ERROR = "error"


class ConversationEvent(str, Enum):
    CONTEXT_VALIDATED = "context_validated"
    CUSTOMER_TURN_RECEIVED = "customer_turn_received"
    OFFER_PRESENTED = "offer_presented"
    OBJECTION_DETECTED = "objection_detected"
    CLARIFICATION_NEEDED = "clarification_needed"
    AUTHORIZED_TACTIC_AVAILABLE = "authorized_tactic_available"
    FOLLOW_UP_REQUESTED = "follow_up_requested"
    CUSTOMER_INTEREST_SIGNAL = "customer_interest_signal"
    ACTION_PROPOSED = "action_proposed"
    NO_PROGRESS = "no_progress"
    KNOWLEDGE_UNAVAILABLE = "knowledge_unavailable"
    GUARDRAIL_BLOCKED = "guardrail_blocked"
    ERROR_OCCURRED = "error_occurred"


class ObjectionCategory(str, Enum):
    PRECIO = "precio"
    NO_NECESITA = "no_necesita"
    YA_TIENE_SIMILAR = "ya_tiene_similar"
    MAL_MOMENTO = "mal_momento"
    NO_CONFIA = "no_confia"
    OTRO = "otro"


class StrategyCode(str, Enum):
    PRESENT_INITIAL_SPEECH = "PRESENT_INITIAL_SPEECH"
    ASK_DISCOVERY_QUESTION = "ASK_DISCOVERY_QUESTION"
    ASK_CLARIFYING_QUESTION = "ASK_CLARIFYING_QUESTION"
    REFRAME_VALUE = "REFRAME_VALUE"
    PROPOSE_FOLLOW_UP = "PROPOSE_FOLLOW_UP"
    ESCALATE_TO_HUMAN = "ESCALATE_TO_HUMAN"
    ABSTAIN = "ABSTAIN"


class ResponseType(str, Enum):
    INITIAL_SPEECH = "initial_speech"
    OBJECTION_RESPONSE = "objection_response"
    REBATE = "rebate"
    SCHEDULE_FOLLOWUP = "schedule_followup"
    ESCALATION = "escalation"
    INSUFFICIENT_CONTEXT = "insufficient_context"
    ERROR = "error"


class FactKind(str, Enum):
    OFFER_NAME = "offer_name"
    MONTHLY_PRICE = "monthly_price"
    DATA_ALLOWANCE = "data_allowance"
    DISCOUNT = "discount"
    CONDITION = "condition"


class ErrorCode(str, Enum):
    KNOWLEDGE_UNAVAILABLE = "KNOWLEDGE_UNAVAILABLE"
    GENERATION_UNAVAILABLE = "GENERATION_UNAVAILABLE"
    UNAUTHORIZED_COMMERCIAL_CLAIM = "UNAUTHORIZED_COMMERCIAL_CLAIM"
    GROUNDING_VALIDATION_FAILED = "GROUNDING_VALIDATION_FAILED"
    RECOMMENDATION_MUTATION_ATTEMPT = "RECOMMENDATION_MUTATION_ATTEMPT"


@dataclass(frozen=True)
class CustomerContext:
    customer_id: str
    profile: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class OfferRecommendation:
    offer_id: str
    offer_name: str
    acceptance_probability: float | None = None
    recommended_channel: str | None = None
    recommended_moment: Any | None = None
    reason_codes: tuple[str, ...] = ()


@dataclass(frozen=True)
class RecommendationContext:
    source_request_id: str
    recommendation_id: str
    generated_at: datetime
    customer: CustomerContext
    primary_offer: OfferRecommendation
    alternatives: tuple[OfferRecommendation, ...]
    model_version: str


@dataclass(frozen=True)
class CommercialFact:
    fact_id: str
    offer_id: str
    kind: FactKind
    value: str
    display_value: str
    source_version: str
    demo_only: bool


@dataclass(frozen=True)
class OfferKnowledge:
    offer_id: str
    offer_name: str
    facts: tuple[CommercialFact, ...]
    source_version: str
    demo_only: bool

    def fact_by_kind(self, kind: FactKind) -> CommercialFact | None:
        return next((fact for fact in self.facts if fact.kind is kind), None)


@dataclass(frozen=True)
class PlaybookTactic:
    tactic_id: str
    objection_category: ObjectionCategory
    allowed_states: tuple[ConversationState, ...]
    strategy: StrategyCode
    target_state: ConversationState
    response_type: ResponseType
    required_fact_kinds: tuple[FactKind, ...]
    summary: str
    response_template: str
    follow_up_template: str | None
    source_version: str
    demo_only: bool
    approved: bool


@dataclass(frozen=True)
class ConversationContext:
    recommendation: RecommendationContext
    offer_knowledge: OfferKnowledge | None
    knowledge_version: str
    knowledge_issue: str | None = None

    @property
    def facts_by_id(self) -> Mapping[str, CommercialFact]:
        if self.offer_knowledge is None:
            return {}
        return {fact.fact_id: fact for fact in self.offer_knowledge.facts}


@dataclass(frozen=True)
class ConversationTurn:
    request_id: str
    conversation_id: str
    turn_id: str
    speaker: str
    text: str
    timestamp: datetime


@dataclass(frozen=True)
class InterpretedObjection:
    category: ObjectionCategory
    confidence: float
    customer_evidence: str


@dataclass(frozen=True)
class StrategyDecision:
    code: StrategyCode
    target_state: ConversationState
    rationale: str
    tactic: PlaybookTactic | None = None
    error_code: ErrorCode | None = None


@dataclass(frozen=True)
class CommercialClaim:
    text: str
    fact_id: str


@dataclass(frozen=True)
class GenerationTrace:
    """Provider-neutral metadata for generation and evaluation."""

    generator: str
    prompt_version: str
    provider: str | None = None
    model: str | None = None
    response_id: str | None = None
    latency_ms: int | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    fallback_used: bool = False
    fallback_reason: str | None = None


@dataclass(frozen=True)
class GuidanceDraft:
    response_type: ResponseType
    recommended_action: StrategyCode
    summary: str
    suggested_customer_response: str | None
    follow_up_question: str | None
    grounding_fact_ids: tuple[str, ...]
    claims: tuple[CommercialClaim, ...]
    source_recommendation_id: str
    source_offer_id: str
    generation: GenerationTrace | None = None


@dataclass(frozen=True)
class ErrorDetail:
    code: str
    message: str


@dataclass(frozen=True)
class CopilotResponse:
    response_id: str
    request_id: str
    conversation_id: str
    in_reply_to_turn_id: str
    created_at: datetime
    response_type: ResponseType
    conversation_stage: ConversationState
    recommendation_id: str
    offer_id: str
    guidance: GuidanceDraft
    objection: InterpretedObjection | None = None
    grounded: bool = True
    requires_human_review: bool = False
    safety_flags: tuple[str, ...] = ()
    prompt_version: str = "deterministic-core-v2"
    knowledge_version: str = "unknown"
    error: ErrorDetail | None = None


@dataclass(frozen=True)
class StateChange:
    previous: ConversationState
    current: ConversationState
    event: ConversationEvent
    occurred_at: datetime


@dataclass
class ConversationSession:
    conversation_id: str
    context: ConversationContext
    state: ConversationState
    state_updated_at: datetime
    last_processed_turn_id: str | None = None
    detected_objections: list[InterpretedObjection] = field(default_factory=list)
    turns: list[ConversationTurn] = field(default_factory=list)
    used_strategies: list[StrategyCode] = field(default_factory=list)
    pending_clarification: bool = False
    presented_alternative_ids: list[str] = field(default_factory=list)
    requires_human_review: bool = False
    transitions: list[StateChange] = field(default_factory=list)

    @property
    def recommendation(self) -> RecommendationContext:
        return self.context.recommendation
