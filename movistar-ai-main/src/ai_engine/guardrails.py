"""Basic grounding, recommendation-integrity, and claim guardrails."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .domain import (
    ConversationContext,
    ErrorCode,
    FactKind,
    GuidanceDraft,
    StrategyDecision,
    StrategyCode,
)


class ResponseValidationError(ValueError):
    """A generated draft cannot be safely delivered."""

    def __init__(self, code: ErrorCode, message: str) -> None:
        self.code = code
        super().__init__(message)


@dataclass(frozen=True)
class ValidationResult:
    safety_flags: tuple[str, ...]


class ResponseValidator:
    """Validate structured generation before it crosses the dashboard boundary."""

    _percentage = re.compile(r"\b\d+(?:[.,]\d+)?\s*%")
    _discount_terms = ("descuento", "gratis", "sin costo", "promoción")

    def validate(
        self,
        context: ConversationContext,
        strategy: StrategyDecision,
        draft: GuidanceDraft,
    ) -> ValidationResult:
        recommendation = context.recommendation
        if (
            draft.source_recommendation_id != recommendation.recommendation_id
            or draft.source_offer_id != recommendation.primary_offer.offer_id
        ):
            raise ResponseValidationError(
                ErrorCode.RECOMMENDATION_MUTATION_ATTEMPT,
                "Generated content changed the original recommendation identity",
            )
        if draft.recommended_action is not strategy.code:
            raise ResponseValidationError(
                ErrorCode.GROUNDING_VALIDATION_FAILED,
                "Generated action does not match the selected strategy",
            )
        if not draft.summary.strip():
            raise ResponseValidationError(
                ErrorCode.GROUNDING_VALIDATION_FAILED,
                "Generated guidance summary cannot be empty",
            )
        if (
            strategy.code is not StrategyCode.ABSTAIN
            and not (draft.suggested_customer_response or "").strip()
        ):
            raise ResponseValidationError(
                ErrorCode.GROUNDING_VALIDATION_FAILED,
                "A deliverable strategy requires customer-facing content",
            )
        if strategy.tactic and draft.response_type is not strategy.tactic.response_type:
            raise ResponseValidationError(
                ErrorCode.GROUNDING_VALIDATION_FAILED,
                "Generated response type does not match the selected tactic",
            )

        known_facts = context.facts_by_id
        grounded_ids = set(draft.grounding_fact_ids)
        unknown_grounding = grounded_ids - set(known_facts)
        if unknown_grounding:
            raise ResponseValidationError(
                ErrorCode.GROUNDING_VALIDATION_FAILED,
                f"Unknown grounding facts: {sorted(unknown_grounding)}",
            )
        claim_fact_ids = {claim.fact_id for claim in draft.claims}
        if claim_fact_ids != grounded_ids:
            raise ResponseValidationError(
                ErrorCode.GROUNDING_VALIDATION_FAILED,
                "Grounding facts and declared commercial claims do not match",
            )
        rendered_text = " ".join(
            part
            for part in (
                draft.summary,
                draft.suggested_customer_response or "",
                draft.follow_up_question or "",
            )
            if part
        )
        for claim in draft.claims:
            if claim.fact_id not in grounded_ids or claim.fact_id not in known_facts:
                raise ResponseValidationError(
                    ErrorCode.GROUNDING_VALIDATION_FAILED,
                    f"Commercial claim is not grounded: {claim.fact_id}",
                )
            if claim.text != known_facts[claim.fact_id].display_value:
                raise ResponseValidationError(
                    ErrorCode.GROUNDING_VALIDATION_FAILED,
                    f"Commercial claim does not match its authorized fact: {claim.fact_id}",
                )
            if claim.text not in rendered_text:
                raise ResponseValidationError(
                    ErrorCode.GROUNDING_VALIDATION_FAILED,
                    f"Declared claim is absent from generated content: {claim.fact_id}",
                )

        if strategy.tactic is not None:
            grounded_kinds = {known_facts[fact_id].kind for fact_id in grounded_ids}
            missing = set(strategy.tactic.required_fact_kinds) - grounded_kinds
            if missing:
                raise ResponseValidationError(
                    ErrorCode.GROUNDING_VALIDATION_FAILED,
                    "Generated content omitted required tactic facts",
                )

        customer_text = " ".join(
            part
            for part in (
                draft.suggested_customer_response or "",
                draft.follow_up_question or "",
            )
            if part
        ).casefold()
        all_generated_text = rendered_text.casefold()
        fact_kinds = {known_facts[fact_id].kind for fact_id in grounded_ids}
        if "s/" in all_generated_text and FactKind.MONTHLY_PRICE not in fact_kinds:
            raise ResponseValidationError(
                ErrorCode.UNAUTHORIZED_COMMERCIAL_CLAIM,
                "A price was used without a grounded monthly-price fact",
            )
        if (
            self._percentage.search(all_generated_text)
            or any(term in customer_text for term in self._discount_terms)
        ) and FactKind.DISCOUNT not in fact_kinds:
            raise ResponseValidationError(
                ErrorCode.UNAUTHORIZED_COMMERCIAL_CLAIM,
                "A discount or promotion was used without an authorized fact",
            )

        flags: list[str] = []
        if context.offer_knowledge and context.offer_knowledge.demo_only:
            flags.append("DEMO_CATALOG_NOT_OFFICIAL")
        if strategy.tactic and strategy.tactic.demo_only and not strategy.tactic.approved:
            flags.append("DEMO_PLAYBOOK_NOT_APPROVED")
        return ValidationResult(safety_flags=tuple(flags))
