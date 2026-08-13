"""Deterministic implementations replaceable by an LLM in a later phase."""

from __future__ import annotations

import unicodedata

from .domain import (
    CommercialClaim,
    ConversationSession,
    ConversationTurn,
    FactKind,
    GenerationTrace,
    GuidanceDraft,
    InterpretedObjection,
    ObjectionCategory,
    ResponseType,
    StrategyCode,
    StrategyDecision,
)


def _normalized(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.casefold())
    return "".join(
        character for character in decomposed if not unicodedata.combining(character)
    )


class RuleBasedObjectionInterpreter:
    """Classify the documented demo taxonomy without using an LLM."""

    # El texto llega normalizado sin tildes y en minusculas. Las variantes
    # coloquiales peruanas se anaden a los patrones base; el orden importa
    # porque gana la primera categoria que coincide.
    _patterns: tuple[tuple[ObjectionCategory, tuple[str, ...]], ...] = (
        (
            ObjectionCategory.PRECIO,
            (
                "caro",
                "precio",
                "cuesta",
                "no me alcanza",
                "no tengo para pagar",
                "esta fuera de mi presupuesto",
                "muy elevado",
            ),
        ),
        # Va antes que NO_NECESITA: "ya tengo otra operadora, estoy conforme"
        # describe primero lo que el cliente ya tiene contratado.
        (
            ObjectionCategory.YA_TIENE_SIMILAR,
            (
                "ya tengo",
                "algo parecido",
                "otra operadora",
                "ya estoy con",
                "ya cuento con",
            ),
        ),
        (
            ObjectionCategory.NO_NECESITA,
            (
                "no necesito",
                "no me sirve",
                "para que me sirve",
                "no me interesa",
                "estoy conforme",
                "asi estoy bien",
            ),
        ),
        (
            ObjectionCategory.MAL_MOMENTO,
            (
                "ahora no",
                "despues",
                "otro momento",
                "lo voy a pensar",
                "lo pensare",
                "dejame consultarlo",
                "mas adelante",
                "ahorita no",
                "consultarlo en casa",
            ),
        ),
        (
            ObjectionCategory.NO_CONFIA,
            (
                "no confio",
                "no me da confianza",
                # Raiz, no forma conjugada: cubre amarrar/amarrarme/amarrarse.
                "amarrar",
                "atarme",
                "permanencia",
                "letra chica",
                "comprometerme",
            ),
        ),
    )

    def interpret(self, turn: ConversationTurn) -> InterpretedObjection:
        normalized = _normalized(turn.text)
        for category, patterns in self._patterns:
            if any(pattern in normalized for pattern in patterns):
                return InterpretedObjection(
                    category=category,
                    confidence=0.95,
                    customer_evidence=turn.text,
                )
        return InterpretedObjection(
            category=ObjectionCategory.OTRO,
            confidence=0.50,
            customer_evidence=turn.text,
        )


class DeterministicContentGenerator:
    """Render grounded content from structured facts and demo tactics."""

    def generate_initial(self, session: ConversationSession) -> GuidanceDraft:
        context = session.context
        offer = context.offer_knowledge
        if offer is None:
            raise ValueError("Initial speech requires offer knowledge")
        name_fact = offer.fact_by_kind(FactKind.OFFER_NAME)
        if name_fact is None:
            raise ValueError("Initial speech requires an offer name fact")
        recommendation = context.recommendation
        return GuidanceDraft(
            response_type=ResponseType.INITIAL_SPEECH,
            recommended_action=StrategyCode.PRESENT_INITIAL_SPEECH,
            summary="Presentar la oferta recomendada y abrir descubrimiento.",
            suggested_customer_response=(
                "Quisiera comentarle una opción que podría ajustarse a sus necesidades: "
                f"{name_fact.display_value}."
            ),
            follow_up_question="¿Qué aspecto de su servicio actual le gustaría mejorar?",
            grounding_fact_ids=(name_fact.fact_id,),
            claims=(
                CommercialClaim(
                    text=name_fact.display_value,
                    fact_id=name_fact.fact_id,
                ),
            ),
            source_recommendation_id=recommendation.recommendation_id,
            source_offer_id=recommendation.primary_offer.offer_id,
            generation=self._trace(),
        )

    def generate_for_strategy(
        self,
        session: ConversationSession,
        objection: InterpretedObjection,
        strategy: StrategyDecision,
    ) -> GuidanceDraft:
        del objection
        context = session.context
        recommendation = context.recommendation
        if strategy.code is StrategyCode.ASK_CLARIFYING_QUESTION:
            return GuidanceDraft(
                response_type=ResponseType.OBJECTION_RESPONSE,
                recommended_action=strategy.code,
                summary="Solicitar precisión antes de responder.",
                suggested_customer_response=(
                    "Para poder orientarle mejor, ¿podría contarme un poco más sobre su duda?"
                ),
                follow_up_question=None,
                grounding_fact_ids=(),
                claims=(),
                source_recommendation_id=recommendation.recommendation_id,
                source_offer_id=recommendation.primary_offer.offer_id,
                generation=self._trace(),
            )
        if strategy.code is StrategyCode.ABSTAIN or strategy.tactic is None:
            return GuidanceDraft(
                response_type=ResponseType.INSUFFICIENT_CONTEXT,
                recommended_action=StrategyCode.ABSTAIN,
                summary="No hay conocimiento autorizado suficiente para responder.",
                suggested_customer_response=None,
                follow_up_question=None,
                grounding_fact_ids=(),
                claims=(),
                source_recommendation_id=recommendation.recommendation_id,
                source_offer_id=recommendation.primary_offer.offer_id,
                generation=self._trace(),
            )

        offer = context.offer_knowledge
        if offer is None:
            raise ValueError("A playbook tactic requires offer knowledge")
        facts = {
            kind: offer.fact_by_kind(kind)
            for kind in strategy.tactic.required_fact_kinds
        }
        if any(fact is None for fact in facts.values()):
            raise ValueError("A required commercial fact is unavailable")
        resolved_facts = {kind: fact for kind, fact in facts.items() if fact is not None}
        template_values = {
            kind.value: fact.display_value for kind, fact in resolved_facts.items()
        }
        response_text = strategy.tactic.response_template.format_map(template_values)
        fact_ids = tuple(fact.fact_id for fact in resolved_facts.values())
        claims = tuple(
            CommercialClaim(text=fact.display_value, fact_id=fact.fact_id)
            for fact in resolved_facts.values()
        )
        return GuidanceDraft(
            response_type=strategy.tactic.response_type,
            recommended_action=strategy.code,
            summary=strategy.tactic.summary,
            suggested_customer_response=response_text,
            follow_up_question=strategy.tactic.follow_up_template,
            grounding_fact_ids=fact_ids,
            claims=claims,
            source_recommendation_id=recommendation.recommendation_id,
            source_offer_id=recommendation.primary_offer.offer_id,
            generation=self._trace(),
        )

    @staticmethod
    def _trace() -> GenerationTrace:
        return GenerationTrace(
            generator="deterministic",
            prompt_version="deterministic-core-v2",
        )
