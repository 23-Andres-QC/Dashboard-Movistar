"""Adapter for the provisional ML contract 0.1.

Only this module knows the external field names from the draft contract.
"""

from __future__ import annotations

from datetime import datetime
from numbers import Real
from typing import Any, Mapping

from .domain import CustomerContext, OfferRecommendation, RecommendationContext


class MLContractError(ValueError):
    """Raised when a provisional ML 0.1 payload is not usable."""


def _mapping(value: Any, path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise MLContractError(f"{path} must be an object")
    return value


def _required_string(payload: Mapping[str, Any], field: str, path: str = "") -> str:
    value = payload.get(field)
    qualified = f"{path}.{field}" if path else field
    if not isinstance(value, str) or not value.strip():
        raise MLContractError(f"{qualified} is required and must be a non-empty string")
    return value.strip()


def _optional_probability(payload: Mapping[str, Any], field: str, path: str) -> float | None:
    value = payload.get(field)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, Real):
        raise MLContractError(f"{path}.{field} must be a number between 0 and 1")
    probability = float(value)
    if not 0.0 <= probability <= 1.0:
        raise MLContractError(f"{path}.{field} must be between 0 and 1")
    return probability


def _reason_codes(payload: Mapping[str, Any], path: str) -> tuple[str, ...]:
    value = payload.get("reason_codes", [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise MLContractError(f"{path}.reason_codes must be an array of strings")
    return tuple(item.strip() for item in value if item.strip())


def _offer(payload: Mapping[str, Any], path: str) -> OfferRecommendation:
    return OfferRecommendation(
        offer_id=_required_string(payload, "offer_id", path),
        offer_name=_required_string(payload, "offer_name", path),
        acceptance_probability=_optional_probability(
            payload, "acceptance_probability", path
        ),
        recommended_channel=(
            str(payload["recommended_channel"])
            if payload.get("recommended_channel") is not None
            else None
        ),
        recommended_moment=payload.get("recommended_moment"),
        reason_codes=_reason_codes(payload, path),
    )


class MLV01Adapter:
    """Validate a draft ML payload and map it to the stable internal model."""

    supported_version = "0.1"

    @classmethod
    def parse(cls, raw_payload: Mapping[str, Any]) -> RecommendationContext:
        payload = _mapping(raw_payload, "payload")
        version = payload.get("contract_version")
        if version is not None and version != cls.supported_version:
            raise MLContractError(
                f"Unsupported ML contract version: {version!r}; "
                f"expected {cls.supported_version!r}"
            )

        generated_at_text = _required_string(payload, "generated_at")
        try:
            generated_at = datetime.fromisoformat(generated_at_text.replace("Z", "+00:00"))
        except ValueError as exc:
            raise MLContractError("generated_at must be an ISO 8601 datetime") from exc

        customer_payload = _mapping(payload.get("customer"), "customer")
        profile = customer_payload.get("profile_summary", {})
        profile_mapping = _mapping(profile, "customer.profile_summary")

        primary_payload = _mapping(
            payload.get("primary_recommendation"), "primary_recommendation"
        )

        raw_alternatives = payload.get("alternatives", [])
        if not isinstance(raw_alternatives, list):
            raise MLContractError("alternatives must be an array")
        alternatives = tuple(
            _offer(_mapping(item, f"alternatives[{index}]"), f"alternatives[{index}]")
            for index, item in enumerate(raw_alternatives)
        )

        metadata = _mapping(payload.get("model_metadata"), "model_metadata")

        return RecommendationContext(
            source_request_id=_required_string(payload, "request_id"),
            recommendation_id=_required_string(payload, "recommendation_id"),
            generated_at=generated_at,
            customer=CustomerContext(
                customer_id=_required_string(customer_payload, "customer_id", "customer"),
                profile=dict(profile_mapping),
            ),
            primary_offer=_offer(primary_payload, "primary_recommendation"),
            alternatives=alternatives,
            model_version=_required_string(metadata, "model_version", "model_metadata"),
        )

