"""Build the minimum trusted context required by the conversational core."""

from __future__ import annotations

import unicodedata

from .domain import ConversationContext, RecommendationContext
from .ports import CommercialCatalog


def _normalized(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value.casefold())
    return "".join(char for char in decomposed if not unicodedata.combining(char))


class ContextBuilder:
    """Join an immutable ML recommendation with replaceable catalog knowledge."""

    def __init__(self, catalog: CommercialCatalog) -> None:
        self._catalog = catalog

    def build(self, recommendation: RecommendationContext) -> ConversationContext:
        offer = self._catalog.get_offer(recommendation.primary_offer.offer_id)
        if offer is None:
            return ConversationContext(
                recommendation=recommendation,
                offer_knowledge=None,
                knowledge_version=self._catalog.version,
                knowledge_issue=(
                    f"Offer {recommendation.primary_offer.offer_id!r} is absent from catalog"
                ),
            )
        if _normalized(offer.offer_name) != _normalized(
            recommendation.primary_offer.offer_name
        ):
            return ConversationContext(
                recommendation=recommendation,
                offer_knowledge=None,
                knowledge_version=self._catalog.version,
                knowledge_issue=(
                    "ML offer name does not match the catalog for "
                    f"{recommendation.primary_offer.offer_id}"
                ),
            )
        return ConversationContext(
            recommendation=recommendation,
            offer_knowledge=offer,
            knowledge_version=self._catalog.version,
        )

