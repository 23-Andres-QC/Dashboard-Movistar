"""Endpoints alimentados por el JSON de demo (fase 1).

En la fase 2 estos mismos endpoints los alimentara el modelo. El contrato de
entrada y salida no cambia.
"""

from fastapi import APIRouter, HTTPException, Query

from .. import demo_data
from ..schemas import Cliente, Desenlace, Recomendacion, TurnoGuion

router = APIRouter(prefix="/api/clientes", tags=["demo"])


@router.get("/buscar", response_model=Cliente, summary="Ficha del cliente por DNI")
def buscar_cliente(dni: str = Query(..., min_length=6, max_length=12)) -> Cliente:
    cliente = demo_data.buscar_por_dni(dni)
    if cliente is None:
        raise HTTPException(status_code=404, detail="No se encontró un cliente con ese DNI")
    return Cliente(**cliente)


@router.get(
    "/{id_cliente}/recomendaciones",
    response_model=list[Recomendacion],
    summary="Ofertas ordenadas por probabilidad",
)
def listar_recomendaciones(id_cliente: str) -> list[Recomendacion]:
    datos = demo_data.recomendaciones(id_cliente)
    if datos is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return [Recomendacion(**r) for r in datos]


@router.get(
    "/{id_cliente}/guion",
    response_model=list[TurnoGuion],
    summary="Turnos de la conversación de demo",
)
def obtener_guion(id_cliente: str) -> list[TurnoGuion]:
    datos = demo_data.guion(id_cliente)
    if datos is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return [TurnoGuion(**t) for t in datos]


@router.get(
    "/{id_cliente}/desenlace",
    response_model=Desenlace,
    summary="Cierre esperado del caso de demo",
    description="Solo existe en la fase 1: prellena el panel de cierre durante la demo.",
)
def obtener_desenlace(id_cliente: str) -> Desenlace:
    datos = demo_data.desenlace(id_cliente)
    if datos is None:
        raise HTTPException(status_code=404, detail="Cliente o desenlace no encontrado")
    return Desenlace(**datos)
