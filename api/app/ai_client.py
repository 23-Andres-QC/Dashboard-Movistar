"""Cliente del AI Engine (Sales Copilot).

La frontera es: ML decide qué ofrecer, el AI Engine redacta cómo decirlo, y el
dashboard lo presenta. Este módulo traduce el dominio de la consola al contrato
ML 0.1 de entrada y devuelve el contrato Dashboard 0.1 tal cual, sin
reinterpretarlo: los enums y los flags de seguridad son suyos.
"""

import json
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from typing import Any

from .config import get_settings

TIMEOUT = 12

# El AI Engine espera los canales con la grafía del dataset del reto.
CANAL_A_CONTRATO = {
    "tienda": "Tienda",
    "call_in": "Call In",
    "call_out": "Call Out",
    "digital": "Digital",
}


class ErrorCopiloto(Exception):
    """El motor no pudo responder. Lleva el código del contrato si lo hubo."""

    def __init__(self, mensaje: str, codigo: str = "AI_ENGINE_UNAVAILABLE", status: int = 502):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo = codigo
        self.status = status


def _ahora() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _pedir(ruta: str, cuerpo: dict[str, Any]) -> dict[str, Any]:
    url = f"{get_settings().ai_engine_url.rstrip('/')}{ruta}"
    datos = json.dumps(cuerpo).encode("utf-8")
    peticion = urllib.request.Request(
        url, data=datos, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(peticion, timeout=TIMEOUT) as respuesta:
            return json.loads(respuesta.read())
    except urllib.error.HTTPError as e:
        detalle = {}
        try:
            detalle = json.loads(e.read()).get("error", {})
        except Exception:
            pass
        raise ErrorCopiloto(
            detalle.get("message", f"El copiloto respondió {e.code}"),
            detalle.get("code", "AI_ENGINE_ERROR"),
            e.code if e.code in (404, 409, 422) else 502,
        ) from e
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        raise ErrorCopiloto(f"No se pudo contactar con el copiloto: {e}") from e


def _probabilidad(valor: int | float) -> float:
    """El contrato ML usa 0–1; la consola trabaja en 0–100."""
    return round(min(100, max(0, float(valor))) / 100, 4)


def iniciar_conversacion(
    *,
    id_gestion: str,
    cliente: dict[str, Any],
    principal: dict[str, Any],
    alternativas: list[dict[str, Any]],
    canal: str,
) -> dict[str, Any]:
    """Abre la sesión en el motor y devuelve el speech inicial.

    Se usa una recomendación por gestión: así el `recommendation_id` es único y
    el motor no rechaza el inicio con CONVERSATION_ALREADY_EXISTS.
    """
    payload = {
        "contract_version": "0.1",
        "request_id": f"req-{uuid.uuid4().hex[:12]}",
        "recommendation_id": f"rec-{id_gestion.lower()}",
        "generated_at": _ahora(),
        "customer": {
            "customer_id": cliente["cliente_id"],
            "profile_summary": {
                "customer_type": cliente.get("tipo_cliente"),
                "age_range": cliente.get("edad_rango"),
                "tenure_months": cliente.get("antiguedad_meses", 0),
                "has_mobile": cliente.get("tiene_movil", False),
                "has_home": cliente.get("tiene_hogar", False),
                "app_user": cliente.get("es_usuario_app", False),
            },
        },
        "primary_recommendation": {
            "offer_id": principal["oferta_id"],
            "offer_name": principal["oferta"],
            "acceptance_probability": _probabilidad(principal["probabilidad"]),
            "recommended_channel": CANAL_A_CONTRATO.get(canal, "Call Out"),
            "recommended_moment": principal.get("franja_sugerida"),
            "reason_codes": _codigos(principal),
        },
        "alternatives": [
            {
                "offer_id": alt["oferta_id"],
                "offer_name": alt["oferta"],
                "acceptance_probability": _probabilidad(alt["probabilidad"]),
                "reason_codes": [],
            }
            for alt in alternativas
        ],
        "model_metadata": {"model_version": principal.get("origen", "demo")},
    }
    return _pedir("/v1/conversations", payload)


def enviar_turno(*, conversation_id: str, texto: str) -> dict[str, Any]:
    """Manda lo que dijo el cliente y devuelve la guía para el asesor."""
    payload = {
        "contract_version": "0.1",
        "request_id": f"req-{uuid.uuid4().hex[:12]}",
        "conversation_id": conversation_id,
        "turn_id": f"turn-{uuid.uuid4().hex[:12]}",
        "speaker": "customer",
        "text": texto,
        "timestamp": _ahora(),
    }
    return _pedir("/v1/turns", payload)


def _codigos(principal: dict[str, Any]) -> list[str]:
    """Traduce las señales de la explicación a reason codes del contrato."""
    codigos: list[str] = []
    texto = " ".join(principal.get("explicacion", [])).lower()
    if "consumo" in texto:
        codigos.append("HIGH_DATA_USAGE")
    if "elegible mt" in texto:
        codigos.append("MT_ELIGIBLE")
    if "riesgo de baja" in texto:
        codigos.append("CHURN_RISK")
    if "sin historial" in texto:
        codigos.append("NO_HISTORY_LOOKALIKE")
    return codigos or ["MODEL_SCORE"]
