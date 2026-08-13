"""Adapter for the provisional Dashboard contract 0.1.

Only this module knows the external response field names from the draft contract.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Mapping

from .domain import ConversationTurn, CopilotResponse


class DashboardContractError(ValueError):
    """Raised when a provisional Dashboard 0.1 turn is not usable."""


def _required_string(payload: Mapping[str, Any], field: str) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise DashboardContractError(
            f"{field} is required and must be a non-empty string"
        )
    return value.strip()


class DashboardV01TurnAdapter:
    """Validate a Dashboard 0.1 customer turn and map it to the domain."""

    supported_version = "0.1"

    @classmethod
    def parse(cls, raw_payload: Mapping[str, Any]) -> ConversationTurn:
        version = raw_payload.get("contract_version")
        if version is not None and version != cls.supported_version:
            raise DashboardContractError(
                f"Unsupported Dashboard contract version: {version!r}; "
                f"expected {cls.supported_version!r}"
            )
        speaker = _required_string(raw_payload, "speaker")
        if speaker != "customer":
            raise DashboardContractError(
                "The current MVP accepts only turns with speaker='customer'"
            )
        timestamp_text = _required_string(raw_payload, "timestamp")
        try:
            timestamp = datetime.fromisoformat(timestamp_text.replace("Z", "+00:00"))
        except ValueError as exc:
            raise DashboardContractError(
                "timestamp must be an ISO 8601 datetime"
            ) from exc
        return ConversationTurn(
            request_id=_required_string(raw_payload, "request_id"),
            conversation_id=_required_string(raw_payload, "conversation_id"),
            turn_id=_required_string(raw_payload, "turn_id"),
            speaker=speaker,
            text=_required_string(raw_payload, "text"),
            timestamp=timestamp,
        )


class DashboardV01Formatter:
    """Map an internal response to the provisional Dashboard 0.1 shape."""

    contract_version = "0.1"

    def format(self, response: CopilotResponse) -> dict[str, Any]:
        objection: dict[str, Any] | None = None
        if response.objection is not None:
            objection = {
                "category": response.objection.category.value,
                "secondary_categories": [],
                "confidence": response.objection.confidence,
                "customer_evidence": response.objection.customer_evidence,
            }

        payload: dict[str, Any] = {
            "contract_version": self.contract_version,
            "response_id": response.response_id,
            "request_id": response.request_id,
            "conversation_id": response.conversation_id,
            "in_reply_to_turn_id": response.in_reply_to_turn_id,
            "created_at": response.created_at.isoformat(),
            "response_type": response.response_type.value,
            "conversation_stage": response.conversation_stage.value,
            "advisor_guidance": {
                "recommended_action": response.guidance.recommended_action.value,
                "summary": response.guidance.summary,
                "suggested_customer_response": (
                    response.guidance.suggested_customer_response
                ),
                "follow_up_question": response.guidance.follow_up_question,
                "alternative_offer_id": None,
            },
            "grounding": {
                "offer_id": response.offer_id,
                "fact_ids": list(response.guidance.grounding_fact_ids),
            },
            "safety": {
                "grounded": response.grounded,
                "requires_human_review": response.requires_human_review,
                "flags": list(response.safety_flags),
            },
            "trace": {
                "recommendation_id": response.recommendation_id,
                "prompt_version": response.prompt_version,
                "knowledge_version": response.knowledge_version,
            },
        }
        if objection is not None:
            payload["objection"] = objection
        if response.error is not None:
            payload["error"] = {
                "code": response.error.code,
                "message": response.error.message,
            }
        return payload
