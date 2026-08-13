"""Gestiones y calificaciones: la parte real y persistente de la fase 1."""

import random
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Calificacion, Gestion
from ..schemas import (
    CalificacionCrear,
    CalificacionOut,
    GestionCerrar,
    GestionCrear,
    GestionObjecion,
    GestionOut,
)

router = APIRouter(prefix="/api/gestiones", tags=["gestiones"])


def _nuevo_id(db: Session) -> str:
    """Identificador legible tipo GES-77412, verificado contra la tabla."""
    for _ in range(20):
        candidato = f"GES-{random.randint(10000, 99999)}"
        if db.get(Gestion, candidato) is None:
            return candidato
    raise HTTPException(status_code=500, detail="No se pudo generar un id de gestión")


def _obtener(db: Session, id_gestion: str) -> Gestion:
    gestion = db.get(Gestion, id_gestion)
    if gestion is None:
        raise HTTPException(status_code=404, detail="Gestión no encontrada")
    return gestion


@router.post("", response_model=GestionOut, status_code=201, summary="Abre una gestión")
def crear_gestion(payload: GestionCrear, db: Session = Depends(get_db)) -> Gestion:
    gestion = Gestion(
        id_gestion=_nuevo_id(db),
        id_cliente=payload.id_cliente,
        oferta_recomendada=payload.oferta_recomendada,
        canal=payload.canal,
        id_asesor=payload.id_asesor,
        inicio=datetime.now(timezone.utc),
        prob_inicial=payload.prob_inicial,
        resultado="en_curso",
        objeciones_detectadas=[],
    )
    db.add(gestion)
    db.commit()
    db.refresh(gestion)
    return gestion


@router.patch(
    "/{id_gestion}/objecion", response_model=GestionOut, summary="Marca una objeción detectada"
)
def marcar_objecion(
    id_gestion: str, payload: GestionObjecion, db: Session = Depends(get_db)
) -> Gestion:
    gestion = _obtener(db, id_gestion)
    actuales = list(gestion.objeciones_detectadas or [])
    if payload.objecion not in actuales:
        actuales.append(payload.objecion)
        # Reasignar la lista completa: JSONB no rastrea mutaciones in place.
        gestion.objeciones_detectadas = actuales
        db.commit()
        db.refresh(gestion)
    return gestion


@router.post("/{id_gestion}/cerrar", response_model=GestionOut, summary="Cierra la gestión")
def cerrar_gestion(
    id_gestion: str, payload: GestionCerrar, db: Session = Depends(get_db)
) -> Gestion:
    gestion = _obtener(db, id_gestion)
    if gestion.resultado != "en_curso":
        raise HTTPException(status_code=409, detail="La gestión ya fue cerrada")

    gestion.resultado = payload.resultado
    gestion.motivo_real = payload.motivo_real
    gestion.prob_final = payload.prob_final
    gestion.medio_probatorio = payload.medio_probatorio
    gestion.fin = datetime.now(timezone.utc)
    db.commit()
    db.refresh(gestion)
    return gestion


@router.post(
    "/{id_gestion}/calificacion",
    response_model=CalificacionOut,
    status_code=201,
    summary="Califica la calidad del servicio",
)
def calificar(
    id_gestion: str, payload: CalificacionCrear, db: Session = Depends(get_db)
) -> Calificacion:
    _obtener(db, id_gestion)
    calificacion = Calificacion(id_gestion=id_gestion, **payload.model_dump())
    db.add(calificacion)
    db.commit()
    db.refresh(calificacion)
    return calificacion


@router.get("/{id_gestion}", response_model=GestionOut, summary="Consulta una gestión")
def obtener_gestion(id_gestion: str, db: Session = Depends(get_db)) -> Gestion:
    return _obtener(db, id_gestion)
