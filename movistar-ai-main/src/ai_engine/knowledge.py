"""Replaceable demo catalog and playbook implementations."""

from __future__ import annotations

import csv
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from .domain import (
    CommercialFact,
    ConversationState,
    FactKind,
    ObjectionCategory,
    OfferKnowledge,
    PlaybookTactic,
    ResponseType,
    StrategyCode,
)


class KnowledgeConfigurationError(ValueError):
    """Raised when demo knowledge cannot be parsed safely."""


class CsvDemoCatalog:
    """Read the synthetic challenge catalog as demo-only commercial facts."""

    def __init__(
        self,
        path: Path,
        version: str = "challenge-synthetic-catalog-2026",
    ) -> None:
        self._path = path
        self._version = version
        self._offers = self._load()

    @property
    def version(self) -> str:
        return self._version

    def get_offer(self, offer_id: str) -> OfferKnowledge | None:
        return self._offers.get(offer_id)

    def _load(self) -> dict[str, OfferKnowledge]:
        with self._path.open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))

        offers: dict[str, OfferKnowledge] = {}
        for row_number, row in enumerate(rows, start=2):
            offer_id = (row.get("oferta_id") or "").strip()
            offer_name = (row.get("nombre_oferta") or "").strip()
            if not offer_id or not offer_name:
                raise KnowledgeConfigurationError(
                    f"Missing offer id or name in catalog row {row_number}"
                )
            if offer_id in offers:
                raise KnowledgeConfigurationError(f"Duplicate offer id: {offer_id}")

            facts = [
                CommercialFact(
                    fact_id=f"demo_catalog:{offer_id}:name",
                    offer_id=offer_id,
                    kind=FactKind.OFFER_NAME,
                    value=offer_name,
                    display_value=offer_name,
                    source_version=self._version,
                    demo_only=True,
                )
            ]
            price_text = (row.get("precio_mensual") or "").strip()
            if price_text:
                try:
                    price = Decimal(price_text)
                except InvalidOperation as exc:
                    raise KnowledgeConfigurationError(
                        f"Invalid monthly price for {offer_id}: {price_text!r}"
                    ) from exc
                facts.append(
                    CommercialFact(
                        fact_id=f"demo_catalog:{offer_id}:monthly_price",
                        offer_id=offer_id,
                        kind=FactKind.MONTHLY_PRICE,
                        value=str(price),
                        display_value=f"S/ {price:.2f}",
                        source_version=self._version,
                        demo_only=True,
                    )
                )

            offers[offer_id] = OfferKnowledge(
                offer_id=offer_id,
                offer_name=offer_name,
                facts=tuple(facts),
                source_version=self._version,
                demo_only=True,
            )
        return offers


class JsonDemoPlaybook:
    """Read a synthetic, explicitly unapproved playbook for local execution."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._version, self._tactics = self._load()

    @property
    def version(self) -> str:
        return self._version

    def tactics_for(self, category: ObjectionCategory) -> tuple[PlaybookTactic, ...]:
        return tuple(
            tactic for tactic in self._tactics if tactic.objection_category is category
        )

    def _load(self) -> tuple[str, tuple[PlaybookTactic, ...]]:
        with self._path.open(encoding="utf-8") as stream:
            payload: Any = json.load(stream)
        if not isinstance(payload, dict):
            raise KnowledgeConfigurationError("Demo playbook must be a JSON object")
        metadata = payload.get("metadata")
        if not isinstance(metadata, dict):
            raise KnowledgeConfigurationError("Demo playbook metadata is required")
        if metadata.get("demo_only") is not True or metadata.get("approved") is not False:
            raise KnowledgeConfigurationError(
                "The bundled demo playbook must be marked demo_only=true and approved=false"
            )
        version = metadata.get("version")
        if not isinstance(version, str) or not version:
            raise KnowledgeConfigurationError("Demo playbook version is required")

        raw_tactics = payload.get("tactics")
        if not isinstance(raw_tactics, list):
            raise KnowledgeConfigurationError("Demo playbook tactics must be an array")

        tactics: list[PlaybookTactic] = []
        for index, raw in enumerate(raw_tactics):
            if not isinstance(raw, dict):
                raise KnowledgeConfigurationError(f"Tactic {index} must be an object")
            try:
                tactics.append(
                    PlaybookTactic(
                        tactic_id=str(raw["tactic_id"]),
                        objection_category=ObjectionCategory(raw["objection_category"]),
                        allowed_states=tuple(
                            ConversationState(value) for value in raw["allowed_states"]
                        ),
                        strategy=StrategyCode(raw["strategy"]),
                        target_state=ConversationState(raw["target_state"]),
                        response_type=ResponseType(raw["response_type"]),
                        required_fact_kinds=tuple(
                            FactKind(value) for value in raw["required_fact_kinds"]
                        ),
                        summary=str(raw["summary"]),
                        response_template=str(raw["response_template"]),
                        follow_up_template=(
                            str(raw["follow_up_template"])
                            if raw.get("follow_up_template") is not None
                            else None
                        ),
                        source_version=version,
                        demo_only=True,
                        approved=False,
                    )
                )
            except (KeyError, TypeError, ValueError) as exc:
                raise KnowledgeConfigurationError(
                    f"Invalid demo playbook tactic at index {index}"
                ) from exc
        return version, tuple(tactics)

