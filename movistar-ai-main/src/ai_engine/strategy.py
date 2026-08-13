"""State- and knowledge-aware conversational strategy policy."""

from __future__ import annotations

from .domain import (
    ConversationContext,
    ConversationState,
    ErrorCode,
    InterpretedObjection,
    ObjectionCategory,
    StrategyCode,
    StrategyDecision,
)
from .ports import SalesPlaybook


class ConversationalStrategyPolicy:
    """Select a permitted tactic without performing any ML ranking."""

    def __init__(
        self,
        playbook: SalesPlaybook,
        clarification_threshold: float = 0.75,
    ) -> None:
        self._playbook = playbook
        self._clarification_threshold = clarification_threshold

    @property
    def playbook_version(self) -> str:
        return self._playbook.version

    def decide(
        self,
        state: ConversationState,
        objection: InterpretedObjection,
        context: ConversationContext,
    ) -> StrategyDecision:
        if (
            objection.category is ObjectionCategory.OTRO
            or objection.confidence < self._clarification_threshold
        ):
            return StrategyDecision(
                code=StrategyCode.ASK_CLARIFYING_QUESTION,
                target_state=ConversationState.CLARIFICATION,
                rationale="La objeción es ambigua o tiene confianza insuficiente.",
            )

        tactic = next(
            (
                candidate
                for candidate in self._playbook.tactics_for(objection.category)
                if state in candidate.allowed_states
            ),
            None,
        )
        if tactic is None:
            return StrategyDecision(
                code=StrategyCode.ABSTAIN,
                target_state=ConversationState.ESCALATION,
                rationale="No existe una táctica disponible para este estado y objeción.",
                error_code=ErrorCode.KNOWLEDGE_UNAVAILABLE,
            )

        offer = context.offer_knowledge
        available_kinds = {fact.kind for fact in offer.facts} if offer else set()
        missing = set(tactic.required_fact_kinds) - available_kinds
        if missing:
            missing_values = ", ".join(sorted(kind.value for kind in missing))
            return StrategyDecision(
                code=StrategyCode.ABSTAIN,
                target_state=ConversationState.ESCALATION,
                rationale=f"Faltan hechos requeridos por la táctica: {missing_values}.",
                error_code=ErrorCode.KNOWLEDGE_UNAVAILABLE,
            )

        return StrategyDecision(
            code=tactic.strategy,
            target_state=tactic.target_state,
            rationale=f"Táctica demo aplicable: {tactic.tactic_id}.",
            tactic=tactic,
        )

