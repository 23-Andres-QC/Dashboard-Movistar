"""Offline-first evaluation harness for interchangeable content generators."""

from __future__ import annotations

import argparse
import copy
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any, Callable

from .configuration import OpenAISettings
from .contract_ml_v01 import MLV01Adapter
from .demo import _project_root, build_demo_service
from .deterministic import DeterministicContentGenerator
from .domain import ConversationTurn, CopilotResponse
from .llm import LlmContentGenerator
from .mocks import MockRecommendationSource
from .openai_responses import OpenAIResponsesProvider
from .service import SalesCopilotService


@dataclass(frozen=True)
class EvaluationCase:
    case_id: str
    customer_text: str | None
    expected_response_type: str
    expected_action: str
    expected_objection: str | None
    expected_recommendation_id: str
    expected_offer_id: str
    required_fact_ids: tuple[str, ...]
    forbidden_phrases: tuple[str, ...]
    expected_grounded: bool
    expected_error_code: str | None
    offer_override: dict[str, str] | None
    human_review_focus: tuple[str, ...]


@dataclass(frozen=True)
class EvaluationResult:
    case_id: str
    structural_compliance: bool
    grounding_compliance: bool
    identifiers_preserved: bool
    unauthorized_claims_absent: bool
    strategy_respected: bool
    response_type_respected: bool
    context_consistent: bool
    error_handling_compliance: bool
    degradation_behavior_respected: bool
    naturalness_proxy: float
    degraded_or_abstained: bool
    generator: str | None
    provider: str | None
    model: str | None
    provider_latency_ms: int | None
    end_to_end_latency_ms: int
    input_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None
    human_review_focus: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_evaluation_cases(path: Path) -> tuple[EvaluationCase, ...]:
    with path.open(encoding="utf-8") as stream:
        payload = json.load(stream)
    if not isinstance(payload, dict) or not isinstance(payload.get("cases"), list):
        raise ValueError("Evaluation fixture must contain a cases array")
    cases: list[EvaluationCase] = []
    for raw in payload["cases"]:
        if not isinstance(raw, dict):
            raise ValueError("Each evaluation case must be an object")
        cases.append(
            EvaluationCase(
                case_id=str(raw["case_id"]),
                customer_text=raw.get("customer_text"),
                expected_response_type=str(raw["expected_response_type"]),
                expected_action=str(raw["expected_action"]),
                expected_objection=raw.get("expected_objection"),
                expected_recommendation_id=str(raw["expected_recommendation_id"]),
                expected_offer_id=str(raw["expected_offer_id"]),
                required_fact_ids=tuple(raw.get("required_fact_ids", [])),
                forbidden_phrases=tuple(raw.get("forbidden_phrases", [])),
                expected_grounded=bool(raw.get("expected_grounded", True)),
                expected_error_code=raw.get("expected_error_code"),
                offer_override=raw.get("offer_override"),
                human_review_focus=tuple(raw.get("human_review_focus", [])),
            )
        )
    return tuple(cases)


def evaluate_response(
    case: EvaluationCase,
    response: CopilotResponse,
    *,
    end_to_end_latency_ms: int,
) -> EvaluationResult:
    guidance = response.guidance
    customer_text = guidance.suggested_customer_response or ""
    normalized_text = customer_text.casefold()
    grounding_ids = set(guidance.grounding_fact_ids)
    claims_grounded = all(
        claim.fact_id in grounding_ids and claim.text in customer_text
        for claim in guidance.claims
    )
    objection_matches = (
        case.expected_objection is None
        and response.objection is None
        or response.objection is not None
        and response.objection.category.value == case.expected_objection
    )
    trace = guidance.generation
    structural = bool(
        guidance.summary.strip()
        and response.response_id
        and response.conversation_id
        and response.request_id
    )
    grounding = bool(
        response.grounded is case.expected_grounded
        and set(case.required_fact_ids).issubset(grounding_ids)
        and claims_grounded
    )
    identifiers = (
        response.recommendation_id == case.expected_recommendation_id
        and response.offer_id == case.expected_offer_id
        and guidance.source_recommendation_id == case.expected_recommendation_id
        and guidance.source_offer_id == case.expected_offer_id
    )
    unauthorized_absent = not any(
        phrase.casefold() in normalized_text for phrase in case.forbidden_phrases
    )
    strategy_respected = guidance.recommended_action.value == case.expected_action
    response_type_respected = response.response_type.value == case.expected_response_type
    actual_error_code = response.error.code if response.error else None
    error_handling_compliance = actual_error_code == case.expected_error_code
    degraded_or_abstained = bool(
        response.error is not None
        or not response.grounded
        or trace is not None
        and trace.fallback_used
    )
    degradation_expected = (
        not case.expected_grounded or case.expected_error_code is not None
    )
    context_consistent = bool(
        objection_matches
        and identifiers
        and set(case.required_fact_ids).issubset(grounding_ids)
        and error_handling_compliance
    )
    return EvaluationResult(
        case_id=case.case_id,
        structural_compliance=structural,
        grounding_compliance=grounding,
        identifiers_preserved=identifiers,
        unauthorized_claims_absent=unauthorized_absent,
        strategy_respected=strategy_respected,
        response_type_respected=response_type_respected,
        context_consistent=context_consistent,
        error_handling_compliance=error_handling_compliance,
        degradation_behavior_respected=(
            degraded_or_abstained is degradation_expected
        ),
        naturalness_proxy=_naturalness_proxy(customer_text, guidance.follow_up_question),
        degraded_or_abstained=degraded_or_abstained,
        generator=trace.generator if trace else None,
        provider=trace.provider if trace else None,
        model=trace.model if trace else None,
        provider_latency_ms=trace.latency_ms if trace else None,
        end_to_end_latency_ms=end_to_end_latency_ms,
        input_tokens=trace.input_tokens if trace else None,
        output_tokens=trace.output_tokens if trace else None,
        total_tokens=trace.total_tokens if trace else None,
        human_review_focus=case.human_review_focus,
    )


def run_evaluation(
    *,
    cases: tuple[EvaluationCase, ...],
    service_factory: Callable[[], SalesCopilotService],
    recommendation_payload: dict[str, Any],
) -> tuple[EvaluationResult, ...]:
    results: list[EvaluationResult] = []
    for case in cases:
        service = service_factory()
        started = perf_counter()
        case_payload = copy.deepcopy(recommendation_payload)
        if case.offer_override is not None:
            case_payload["primary_recommendation"]["offer_id"] = case.offer_override[
                "offer_id"
            ]
            case_payload["primary_recommendation"]["offer_name"] = case.offer_override[
                "offer_name"
            ]
        response = service.start_session(MLV01Adapter.parse(case_payload))
        if case.customer_text is not None:
            response = service.handle_customer_turn(
                ConversationTurn(
                    request_id=f"eval-request-{case.case_id}",
                    conversation_id=response.conversation_id,
                    turn_id=f"eval-turn-{case.case_id}",
                    speaker="customer",
                    text=case.customer_text,
                    timestamp=datetime.now(timezone.utc),
                )
            )
        elapsed_ms = round((perf_counter() - started) * 1000)
        results.append(
            evaluate_response(
                case,
                response,
                end_to_end_latency_ms=elapsed_ms,
            )
        )
    return tuple(results)


def _naturalness_proxy(customer_text: str, follow_up: str | None) -> float:
    combined = " ".join(part for part in (customer_text, follow_up or "") if part)
    if not combined:
        return 0.0
    checks = (
        20 <= len(combined) <= 600,
        "{" not in combined and "}" not in combined,
        "  " not in combined,
        combined[-1] in ".?!",
        len(combined.split()) >= 5,
    )
    return round(sum(checks) / len(checks), 2)


def _cli() -> None:
    parser = argparse.ArgumentParser(description="Run synthetic generator evaluation")
    parser.add_argument(
        "--generator",
        choices=("deterministic", "openai"),
        default="deterministic",
    )
    args = parser.parse_args()
    root = _project_root()
    cases = load_evaluation_cases(root / "fixtures" / "evaluation_cases_v01.json")
    recommendation_payload = dict(
        MockRecommendationSource(root / "fixtures" / "ml_recommendation_v01.json").load()
    )

    if args.generator == "openai":
        settings = OpenAISettings.from_env()
        generator = LlmContentGenerator(
            OpenAIResponsesProvider(
                model=settings.model,
                api_key=settings.api_key,
                timeout_seconds=settings.timeout_seconds,
            )
        )
        factory = lambda: build_demo_service(
            root,
            content_generator=generator,
            fallback_content_generator=DeterministicContentGenerator(),
        )
    else:
        factory = lambda: build_demo_service(root)

    results = run_evaluation(
        cases=cases,
        service_factory=factory,
        recommendation_payload=recommendation_payload,
    )
    print(json.dumps([result.to_dict() for result in results], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    _cli()
