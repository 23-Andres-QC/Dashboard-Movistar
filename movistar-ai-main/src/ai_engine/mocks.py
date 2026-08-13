"""Local replacements for external recommendation and persistence systems."""

from __future__ import annotations

import json
from collections import deque
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Mapping

from .domain import ConversationSession
from .generation import (
    StructuredGenerationRequest,
    StructuredGenerationResult,
)


class MockRecommendationSource:
    """Load a provisional ML payload from a local JSON fixture."""

    def __init__(self, fixture_path: Path) -> None:
        self.fixture_path = fixture_path

    def load(self) -> Mapping[str, Any]:
        with self.fixture_path.open(encoding="utf-8") as stream:
            payload = json.load(stream)
        if not isinstance(payload, dict):
            raise ValueError("The ML fixture must contain a JSON object")
        return payload


class InMemorySessionStore:
    """Process-local storage; replaceable without changing the core service."""

    def __init__(self) -> None:
        self._sessions: dict[str, ConversationSession] = {}

    def create(self, session: ConversationSession) -> None:
        if session.conversation_id in self._sessions:
            raise ValueError(f"Session already exists: {session.conversation_id}")
        self._sessions[session.conversation_id] = session

    def get(self, conversation_id: str) -> ConversationSession:
        try:
            return self._sessions[conversation_id]
        except KeyError as exc:
            raise KeyError(f"Unknown conversation: {conversation_id}") from exc

    def save(self, session: ConversationSession) -> None:
        if session.conversation_id not in self._sessions:
            raise KeyError(f"Unknown conversation: {session.conversation_id}")
        self._sessions[session.conversation_id] = session


class FakeStructuredGenerationProvider:
    """Queue provider results or failures for offline tests and demos."""

    def __init__(
        self,
        outcomes: Iterable[StructuredGenerationResult | Exception],
    ) -> None:
        self._outcomes = deque(outcomes)
        self.requests: list[StructuredGenerationRequest] = []

    def generate(
        self, request: StructuredGenerationRequest
    ) -> StructuredGenerationResult:
        self.requests.append(request)
        if not self._outcomes:
            raise AssertionError("Fake provider has no configured outcome")
        outcome = self._outcomes.popleft()
        if isinstance(outcome, Exception):
            raise outcome
        return outcome
