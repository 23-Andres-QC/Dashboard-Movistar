"""Copiloto conversacional: la consola habla con el AI Engine a través de aquí.

El dashboard no conoce al proveedor generativo. Manda lo que dijo el cliente y
recibe qué decirle, con los flags de seguridad intactos.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import ai_client, demo_data
from ..db import get_db
from ..models import Gestion
from ..schemas import CopilotoIniciar, CopilotoTurno, GuiaCopiloto

router = APIRouter(prefix="/api/gestiones", tags=["copiloto"])


def _obtener(db: Session, id_gestion: str) -> Gestion:
    gestion = db.get(Gestion, id_gestion)
    if gestion is None:
        raise HTTPException(status_code=404, detail="Gestión no encontrada")
    return gestion


def _a_guia(respuesta: dict) -> GuiaCopiloto:
    guia = respuesta.get("advisor_guidance") or {}
    objecion = respuesta.get("objection") or {}
    seguridad = respuesta.get("safety") or {}
    return GuiaCopiloto(
        conversation_id=respuesta.get("conversation_id", ""),
        response_type=respuesta.get("response_type", ""),
        conversation_stage=respuesta.get("conversation_stage", ""),
        recommended_action=guia.get("recommended_action", ""),
        resumen=guia.get("summary"),
        que_decir=guia.get("suggested_customer_response", ""),
        pregunta_seguimiento=guia.get("follow_up_question"),
        oferta_alternativa=guia.get("alternative_offer_id"),
        objecion_categoria=objecion.get("category"),
        objecion_confianza=objecion.get("confidence"),
        grounded=seguridad.get("grounded", True),
        requiere_revision=seguridad.get("requires_human_review", False),
        flags=seguridad.get("flags", []),
    )


@router.post(
    "/{id_gestion}/copiloto/iniciar",
    response_model=GuiaCopiloto,
    summary="Abre la conversación y devuelve el speech inicial",
)
def iniciar(
    id_gestion: str, payload: CopilotoIniciar, db: Session = Depends(get_db)
) -> GuiaCopiloto:
    gestion = _obtener(db, id_gestion)

    recomendaciones = demo_data.recomendaciones(gestion.id_cliente)
    cliente = demo_data.buscar_por_id(gestion.id_cliente)
    if not recomendaciones or cliente is None:
        raise HTTPException(status_code=404, detail="Cliente sin recomendaciones")

    principal = next(
        (r for r in recomendaciones if r["oferta_id"] == gestion.oferta_id),
        recomendaciones[0],
    )
    alternativas = [r for r in recomendaciones if r is not principal and not r.get("descartada")]

    try:
        respuesta = ai_client.iniciar_conversacion(
            id_gestion=gestion.id_gestion,
            cliente=cliente,
            principal=principal,
            alternativas=alternativas[:3],
            canal=payload.canal or gestion.canal,
        )
    except ai_client.ErrorCopiloto as e:
        raise HTTPException(status_code=e.status, detail=e.mensaje) from e

    return _a_guia(respuesta)


@router.post(
    "/{id_gestion}/copiloto/turno",
    response_model=GuiaCopiloto,
    summary="Procesa lo que dijo el cliente y devuelve qué responder",
)
def turno(id_gestion: str, payload: CopilotoTurno, db: Session = Depends(get_db)) -> GuiaCopiloto:
    _obtener(db, id_gestion)
    try:
        respuesta = ai_client.enviar_turno(
            conversation_id=payload.conversation_id, texto=payload.texto
        )
    except ai_client.ErrorCopiloto as e:
        raise HTTPException(status_code=e.status, detail=e.mensaje) from e
    return _a_guia(respuesta)
