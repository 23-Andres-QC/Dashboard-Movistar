"""Explicit conversational state transitions."""

from __future__ import annotations

from datetime import datetime

from .domain import (
    ConversationEvent,
    ConversationSession,
    ConversationState,
    StateChange,
)


class InvalidTransitionError(ValueError):
    """Raised before state mutation when a transition is not allowed."""

    def __init__(self, state: ConversationState, event: ConversationEvent) -> None:
        self.state = state
        self.event = event
        super().__init__(f"Event {event.value!r} is invalid from state {state.value!r}")


class ConversationStateMachine:
    """Apply the transition graph documented for the Sales Copilot."""

    _transitions: dict[
        tuple[ConversationState, ConversationEvent], ConversationState
    ] = {
        (ConversationState.CONTEXT_RECEIVED, ConversationEvent.CONTEXT_VALIDATED): ConversationState.OPENING,
        (ConversationState.CONTEXT_RECEIVED, ConversationEvent.KNOWLEDGE_UNAVAILABLE): ConversationState.ESCALATION,
        (ConversationState.OPENING, ConversationEvent.CUSTOMER_TURN_RECEIVED): ConversationState.DISCOVERY,
        (ConversationState.OPENING, ConversationEvent.OFFER_PRESENTED): ConversationState.OFFER_PRESENTATION,
        (ConversationState.DISCOVERY, ConversationEvent.OFFER_PRESENTED): ConversationState.OFFER_PRESENTATION,
        (ConversationState.DISCOVERY, ConversationEvent.OBJECTION_DETECTED): ConversationState.OBJECTION_HANDLING,
        (ConversationState.DISCOVERY, ConversationEvent.CLARIFICATION_NEEDED): ConversationState.CLARIFICATION,
        (ConversationState.OFFER_PRESENTATION, ConversationEvent.OBJECTION_DETECTED): ConversationState.OBJECTION_HANDLING,
        (ConversationState.OFFER_PRESENTATION, ConversationEvent.CUSTOMER_INTEREST_SIGNAL): ConversationState.CLOSING_GUIDANCE,
        (ConversationState.OBJECTION_HANDLING, ConversationEvent.CLARIFICATION_NEEDED): ConversationState.CLARIFICATION,
        (ConversationState.OBJECTION_HANDLING, ConversationEvent.AUTHORIZED_TACTIC_AVAILABLE): ConversationState.REBATE,
        (ConversationState.OBJECTION_HANDLING, ConversationEvent.FOLLOW_UP_REQUESTED): ConversationState.FOLLOW_UP,
        (ConversationState.OBJECTION_HANDLING, ConversationEvent.KNOWLEDGE_UNAVAILABLE): ConversationState.ESCALATION,
        (ConversationState.CLARIFICATION, ConversationEvent.OBJECTION_DETECTED): ConversationState.OBJECTION_HANDLING,
        (ConversationState.CLARIFICATION, ConversationEvent.CLARIFICATION_NEEDED): ConversationState.CLARIFICATION,
        (ConversationState.REBATE, ConversationEvent.CUSTOMER_TURN_RECEIVED): ConversationState.OBJECTION_HANDLING,
        (ConversationState.REBATE, ConversationEvent.CUSTOMER_INTEREST_SIGNAL): ConversationState.CLOSING_GUIDANCE,
        (ConversationState.REBATE, ConversationEvent.NO_PROGRESS): ConversationState.FOLLOW_UP,
        (ConversationState.CLOSING_GUIDANCE, ConversationEvent.ACTION_PROPOSED): ConversationState.COMPLETED,
        (ConversationState.FOLLOW_UP, ConversationEvent.ACTION_PROPOSED): ConversationState.COMPLETED,
        (ConversationState.ESCALATION, ConversationEvent.ACTION_PROPOSED): ConversationState.COMPLETED,
    }

    _active_states = frozenset(
        state
        for state in ConversationState
        if state not in {ConversationState.COMPLETED, ConversationState.ERROR}
    )

    def target(
        self, state: ConversationState, event: ConversationEvent
    ) -> ConversationState:
        if event is ConversationEvent.ERROR_OCCURRED and state in self._active_states:
            return ConversationState.ERROR
        if event is ConversationEvent.GUARDRAIL_BLOCKED and state in self._active_states:
            return ConversationState.ESCALATION
        try:
            return self._transitions[(state, event)]
        except KeyError as exc:
            raise InvalidTransitionError(state, event) from exc

    def transition(
        self,
        session: ConversationSession,
        event: ConversationEvent,
        occurred_at: datetime,
    ) -> ConversationState:
        previous = session.state
        current = self.target(previous, event)
        session.state = current
        session.state_updated_at = occurred_at
        session.transitions.append(
            StateChange(
                previous=previous,
                current=current,
                event=event,
                occurred_at=occurred_at,
            )
        )
        return current

