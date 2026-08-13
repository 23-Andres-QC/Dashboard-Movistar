"""Fuente de datos simulada de la fase 1.

Carga el JSON una sola vez y lo expone con la misma forma que tendra el servicio
del modelo en la fase 2. Todo lo que devuelve este modulo (probabilidades,
angulos, rebates, guion) es demo: cuando exista el modelo, solo se reemplaza la
implementacion de estas funciones.
"""

import json
from functools import lru_cache
from pathlib import Path

DEMO_PATH = Path(__file__).parent / "data" / "demo.json"


@lru_cache
def _cargar() -> list[dict]:
    with DEMO_PATH.open(encoding="utf-8") as f:
        return json.load(f)["clientes"]


def buscar_por_dni(dni: str) -> dict | None:
    """Ficha del cliente cuyo DNI coincide, o None."""
    for entrada in _cargar():
        if entrada["cliente"]["dni"] == dni.strip():
            return entrada["cliente"]
    return None


def _entrada_por_id(id_cliente: str) -> dict | None:
    for entrada in _cargar():
        if entrada["cliente"]["id_cliente"] == id_cliente:
            return entrada
    return None


def recomendaciones(id_cliente: str) -> list[dict] | None:
    """Ofertas ordenadas de mayor a menor probabilidad de aceptacion."""
    entrada = _entrada_por_id(id_cliente)
    if entrada is None:
        return None
    return sorted(entrada["recomendaciones"], key=lambda r: r["probabilidad"], reverse=True)


def guion(id_cliente: str) -> list[dict] | None:
    """Turnos de la conversacion de demo, en orden."""
    entrada = _entrada_por_id(id_cliente)
    if entrada is None:
        return None
    return entrada["guion"]


def desenlace(id_cliente: str) -> dict | None:
    """Cierre esperado del caso. Solo existe en la demo: prellena el panel de
    cierre para que el asesor no teclee durante la presentacion."""
    entrada = _entrada_por_id(id_cliente)
    if entrada is None:
        return None
    return entrada.get("desenlace")
