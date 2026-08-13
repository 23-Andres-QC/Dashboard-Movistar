"""Run the local conversational core without APIs or an LLM."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from .composition import project_root
from .context import ContextBuilder
from .contract_dashboard_v01 import DashboardV01Formatter
from .contract_ml_v01 import MLV01Adapter
from .deterministic import (
    DeterministicContentGenerator,
    RuleBasedObjectionInterpreter,
)
from .domain import ConversationTurn
from .guardrails import ResponseValidator
from .knowledge import CsvDemoCatalog, JsonDemoPlaybook
from .mocks import InMemorySessionStore, MockRecommendationSource
from .ports import ContentGenerator
from .service import SalesCopilotService
from .state_machine import ConversationStateMachine
from .strategy import ConversationalStrategyPolicy


def _project_root() -> Path:
    return project_root()


def build_demo_service(
    root: Path | None = None,
    *,
    content_generator: ContentGenerator | None = None,
    fallback_content_generator: ContentGenerator | None = None,
) -> SalesCopilotService:
    project_root = root or _project_root()
    catalog = CsvDemoCatalog(project_root / "fixtures" / "demo_catalog_v01.csv")
    playbook = JsonDemoPlaybook(project_root / "fixtures" / "demo_playbook_v01.json")
    return SalesCopilotService(
        session_store=InMemorySessionStore(),
        context_builder=ContextBuilder(catalog),
        state_machine=ConversationStateMachine(),
        objection_interpreter=RuleBasedObjectionInterpreter(),
        strategy_policy=ConversationalStrategyPolicy(playbook),
        content_generator=content_generator or DeterministicContentGenerator(),
        response_validator=ResponseValidator(),
        fallback_content_generator=fallback_content_generator,
    )


def main() -> None:
    root = _project_root()
    raw_recommendation = MockRecommendationSource(
        root / "fixtures" / "ml_recommendation_v01.json"
    ).load()
    recommendation = MLV01Adapter.parse(raw_recommendation)

    service = build_demo_service(root)
    formatter = DashboardV01Formatter()

    initial_response = service.start_session(recommendation)
    print("=== SPEECH INICIAL GROUNDED ===")
    print(json.dumps(formatter.format(initial_response), indent=2, ensure_ascii=False))

    turn = ConversationTurn(
        request_id="req-demo-turn-001",
        conversation_id=initial_response.conversation_id,
        turn_id="turn-demo-001",
        speaker="customer",
        text="Me parece demasiado caro",
        timestamp=datetime.fromisoformat("2026-08-12T10:34:12-05:00"),
    )
    objection_response = service.handle_customer_turn(turn)
    print("\n=== REBATE DEMO GROUNDED ===")
    print(json.dumps(formatter.format(objection_response), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
