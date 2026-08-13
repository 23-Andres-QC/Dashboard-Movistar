"""Explicit HTTP schemas for provisional ML and Dashboard contracts 0.1."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class MLCustomerV01(BaseModel):
    model_config = ConfigDict(extra="allow")

    customer_id: str = Field(min_length=1)
    profile_summary: dict[str, Any] = Field(default_factory=dict)


class MLOfferV01(BaseModel):
    model_config = ConfigDict(extra="allow")

    offer_id: str = Field(min_length=1)
    offer_name: str = Field(min_length=1)
    acceptance_probability: float | None = Field(default=None, ge=0, le=1)
    recommended_channel: str | None = None
    recommended_moment: Any | None = None
    reason_codes: list[str] = Field(default_factory=list)


class MLModelMetadataV01(BaseModel):
    model_config = ConfigDict(extra="allow")

    model_version: str = Field(min_length=1)


class MLRecommendationV01(BaseModel):
    """Provisional ML 0.1 payload used to start one conversation."""

    model_config = ConfigDict(
        extra="allow",
        json_schema_extra={
            "example": {
                "contract_version": "0.1",
                "request_id": "req-demo-001",
                "recommendation_id": "rec-demo-001",
                "generated_at": "2026-08-11T10:30:00-05:00",
                "customer": {
                    "customer_id": "CLI000001",
                    "profile_summary": {"customer_type": "postpago"},
                },
                "primary_recommendation": {
                    "offer_id": "OF004",
                    "offer_name": "Plan Movil Ilimitado",
                    "acceptance_probability": 0.71,
                    "recommended_channel": "Call In",
                    "reason_codes": ["HIGH_DATA_USAGE"],
                },
                "alternatives": [],
                "model_metadata": {"model_version": "nbo-mock-v1"},
            }
        },
    )

    contract_version: Literal["0.1"] = "0.1"
    request_id: str = Field(min_length=1)
    recommendation_id: str = Field(min_length=1)
    generated_at: datetime
    customer: MLCustomerV01
    primary_recommendation: MLOfferV01
    alternatives: list[MLOfferV01] = Field(default_factory=list)
    model_metadata: MLModelMetadataV01


class DashboardTurnV01(BaseModel):
    """Customer turn accepted by the current Dashboard 0.1 adapter."""

    model_config = ConfigDict(
        extra="allow",
        json_schema_extra={
            "example": {
                "contract_version": "0.1",
                "request_id": "req-turn-001",
                "conversation_id": "conv-rec-demo-001",
                "turn_id": "turn-001",
                "speaker": "customer",
                "text": "Me parece demasiado caro",
                "timestamp": "2026-08-12T10:34:12-05:00",
                "channel": "Call In",
                "language": "es-PE",
            }
        },
    )

    contract_version: Literal["0.1"] = "0.1"
    request_id: str = Field(min_length=1)
    conversation_id: str = Field(min_length=1)
    turn_id: str = Field(min_length=1)
    speaker: Literal["customer"]
    text: str = Field(min_length=1)
    timestamp: datetime
    advisor_id: str | None = None
    channel: str | None = None
    language: str | None = None
    ui_context: dict[str, Any] | None = None
    selected_suggestion_id: str | None = None
    event_type: str | None = None
    sequence_number: int | None = None
    metadata: dict[str, Any] | None = None


class AdvisorGuidanceV01(BaseModel):
    recommended_action: str
    summary: str
    suggested_customer_response: str | None
    follow_up_question: str | None
    alternative_offer_id: str | None


class ObjectionV01(BaseModel):
    category: str
    secondary_categories: list[str]
    confidence: float
    customer_evidence: str


class GroundingV01(BaseModel):
    offer_id: str
    fact_ids: list[str]


class SafetyV01(BaseModel):
    grounded: bool
    requires_human_review: bool
    flags: list[str]


class TraceV01(BaseModel):
    recommendation_id: str
    prompt_version: str
    knowledge_version: str


class EngineErrorDetail(BaseModel):
    code: str
    message: str


class DashboardResponseV01(BaseModel):
    """Response already formatted for the provisional Dashboard contract 0.1."""

    contract_version: Literal["0.1"]
    response_id: str
    request_id: str
    conversation_id: str
    in_reply_to_turn_id: str
    created_at: datetime
    response_type: str
    conversation_stage: str
    advisor_guidance: AdvisorGuidanceV01
    grounding: GroundingV01
    safety: SafetyV01
    trace: TraceV01
    objection: ObjectionV01 | None = None
    error: EngineErrorDetail | None = None


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: Literal["ai-engine-sales-copilot"]
    version: str
    generator_mode: Literal["deterministic", "openai"]
    ml_contract_version: Literal["0.1"]
    dashboard_contract_version: Literal["0.1"]


class TransportErrorDetail(BaseModel):
    field: str | None = None
    message: str


class TransportErrorBody(BaseModel):
    code: str
    message: str
    details: list[TransportErrorDetail] = Field(default_factory=list)


class TransportErrorResponse(BaseModel):
    error: TransportErrorBody
