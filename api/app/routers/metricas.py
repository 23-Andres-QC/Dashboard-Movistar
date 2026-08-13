"""Metricas calculadas con SQL sobre lo realmente guardado."""

from fastapi import APIRouter, Depends
from sqlalchemy import Integer, cast, func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Calificacion, Gestion
from ..schemas import MetricasResumen

router = APIRouter(prefix="/api/metricas", tags=["metricas"])

RESULTADOS = ("en_curso", "vendido", "rechazado", "sin_contacto")


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
    tasa = round(por_resultado["vendido"] / cerradas * 100, 1) if cerradas else 0.0

    motivos = db.execute(
        select(Gestion.motivo_real, func.count())
        .where(Gestion.motivo_real.is_not(None))
        .group_by(Gestion.motivo_real)
    ).all()

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
        promedio_facilidad_venta=round(float(promedio), 2) if promedio is not None else None,
        pct_oferta_pertinente=round(float(pertinentes) * 100, 1)
        if pertinentes is not None
        else None,
        nps_promedio=round(float(nps), 1) if nps is not None else None,
        distribucion_motivos={m: c for m, c in motivos},
        total_calificaciones=total_calif or 0,
    )
