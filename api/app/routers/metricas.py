"""Metricas calculadas con SQL sobre lo realmente guardado."""

from fastapi import APIRouter, Depends
from sqlalchemy import Integer, cast, func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Calificacion, Gestion
from ..schemas import MetricasResumen, ParticipacionMT

router = APIRouter(prefix="/api/metricas", tags=["metricas"])

RESULTADOS = ("en_curso", "vendido", "rechazado", "sin_contacto")


def _pct(parte: int, total: int) -> float:
    return round(parte / total * 100, 1) if total else 0.0


def _participacion_mt(db: Session) -> ParticipacionMT:
    """Objetivo del reto: >50% de la venta hogar y >10% de la movil con MT.

    Se cuenta sobre ventas cerradas, partiendo el denominador por el segmento
    al que apunta la oferta. Las ofertas convergentes (`ambos`) cuentan en los
    dos denominadores, porque una venta de MT es a la vez venta hogar y movil.
    """
    filas = db.execute(
        select(Gestion.segmento_objetivo, Gestion.oferta_es_mt, func.count())
        .where(Gestion.resultado == "vendido")
        .group_by(Gestion.segmento_objetivo, Gestion.oferta_es_mt)
    ).all()

    hogar = hogar_mt = movil = movil_mt = total = total_mt = 0
    for segmento, es_mt, cantidad in filas:
        total += cantidad
        if es_mt:
            total_mt += cantidad
        if segmento in ("hogar", "ambos"):
            hogar += cantidad
            if es_mt:
                hogar_mt += cantidad
        if segmento in ("movil", "ambos"):
            movil += cantidad
            if es_mt:
                movil_mt += cantidad

    return ParticipacionMT(
        ventas_totales=total,
        ventas_con_mt=total_mt,
        pct_venta_hogar_con_mt=_pct(hogar_mt, hogar),
        pct_venta_movil_con_mt=_pct(movil_mt, movil),
    )


@router.get("/resumen", response_model=MetricasResumen, summary="Resumen de gestiones")
def resumen(db: Session = Depends(get_db)) -> MetricasResumen:
    filas = db.execute(
        select(Gestion.resultado, func.count()).group_by(Gestion.resultado)
    ).all()
    por_resultado = {r: 0 for r in RESULTADOS}
    for resultado, cantidad in filas:
        por_resultado[resultado] = cantidad

    total = sum(por_resultado.values())
    cerradas = total - por_resultado["en_curso"]
    tasa = _pct(por_resultado["vendido"], cerradas)

    contactados = db.scalar(
        select(func.count()).where(Gestion.contactabilidad == "contactado")
    )
    tasa_contacto = _pct(contactados or 0, cerradas)

    motivos = db.execute(
        select(Gestion.motivo_real, func.count())
        .where(Gestion.motivo_real.is_not(None))
        .group_by(Gestion.motivo_real)
    ).all()

    # De las gestiones donde hubo rebate, cuantas terminaron en venta.
    con_rebate = db.scalar(
        select(func.count()).where(Gestion.es_rebate.is_(True), Gestion.resultado != "en_curso")
    )
    rebate_vendido = db.scalar(
        select(func.count()).where(Gestion.es_rebate.is_(True), Gestion.resultado == "vendido")
    )

    promedio, pertinentes, nps, total_calif = db.execute(
        select(
            func.avg(Calificacion.facilidad_venta),
            func.avg(cast(Calificacion.oferta_fue_pertinente, Integer)),
            func.avg(Calificacion.nps_declarado),
            func.count(Calificacion.id),
        )
    ).one()

    return MetricasResumen(
        total_gestiones=total,
        por_resultado=por_resultado,
        tasa_conversion=tasa,
        tasa_contactabilidad=tasa_contacto,
        participacion_mt=_participacion_mt(db),
        promedio_facilidad_venta=round(float(promedio), 2) if promedio is not None else None,
        pct_oferta_pertinente=round(float(pertinentes) * 100, 1)
        if pertinentes is not None
        else None,
        nps_promedio=round(float(nps), 1) if nps is not None else None,
        distribucion_motivos={m: c for m, c in motivos},
        efectividad_rebate=_pct(rebate_vendido or 0, con_rebate or 0) if con_rebate else None,
        total_calificaciones=total_calif or 0,
    )
