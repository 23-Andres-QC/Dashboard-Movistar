"""Ports for dependencies that have concrete replacement needs."""

from __future__ import annotations

from typing import Any, Mapping, Protocol

from .domain import (
    ConversationSession,
    ConversationTurn,
    GuidanceDraft,
    InterpretedObjection,
    ObjectionCategory,
    OfferKnowledge,
    PlaybookTactic,
    StrategyDecision,
)


class RecommendationSource(Protocol):
    def load(self) -> Mapping[str, Any]: ...


class SessionStore(Protocol):
    def create(self, session: ConversationSession) -> None: ...

    def get(self, conversation_id: str) -> ConversationSession: ...

    def save(self, session: ConversationSession) -> None: ...


class CommercialCatalog(Protocol):
    @property
    def version(self) -> str: ...

    def get_offer(self, offer_id: str) -> OfferKnowledge | None: ...


class SalesPlaybook(Protocol):
    @property
    def version(self) -> str: ...

    def tactics_for(self, category: ObjectionCategory) -> tuple[PlaybookTactic, ...]: ...


class ObjectionInterpreter(Protocol):
    def interpret(self, turn: ConversationTurn) -> InterpretedObjection: ...


class ContentGenerator(Protocol):
    def generate_initial(self, session: ConversationSession) -> GuidanceDraft: ...

    def generate_for_strategy(
        self,
        session: ConversationSession,
        objection: InterpretedObjection,
        strategy: StrategyDecision,
    ) -> GuidanceDraft: ...
