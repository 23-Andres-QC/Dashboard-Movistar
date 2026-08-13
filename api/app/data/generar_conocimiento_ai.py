"""Genera el conocimiento autorizado que consume el AI Engine.

El motor solo redacta sobre hechos de su catálogo y tácticas de su playbook: si
una oferta no está, se abstiene. Este script deriva ambos archivos de
`demo.json` para que el copiloto pueda hablar exactamente de las ofertas que la
consola presenta, sin tocar el repositorio del motor (se montan en el
contenedor sobre `fixtures/`).

    python3 api/app/data/generar_conocimiento_ai.py
"""

import csv
import json
from pathlib import Path

AQUI = Path(__file__).parent
DEMO = AQUI / "demo.json"
SALIDA = AQUI / "ai"

# Se conserva la oferta de ejemplo del motor para que sus propios fixtures y
# tests sigan funcionando tal cual.
CATALOGO_BASE = [{"oferta_id": "OF004", "nombre_oferta": "Plan Movil Ilimitado", "precio_mensual": "99.90"}]

PLAYBOOK = {
    "metadata": {
        "name": "Playbook de demostración · consola NBO",
        "version": "nbo-demo-playbook-0.2",
        "demo_only": True,
        "approved": False,
        "notice": (
            "Contenido de demostración para la fase 1. No representa un playbook "
            "oficial de Movistar y no está aprobado por negocio."
        ),
    },
    "tactics": [
        {
            "tactic_id": "nbo-price-reframe",
            "objection_category": "precio",
            "allowed_states": ["objection_handling", "rebate", "clarification", "follow_up"],
            "strategy": "REFRAME_VALUE",
            "target_state": "rebate",
            "response_type": "rebate",
            "required_fact_kinds": ["offer_name", "monthly_price"],
            "summary": "Reconocer la preocupación y aclarar el valor sin ofrecer descuentos.",
            "response_template": (
                "Entiendo que el precio pese. {offer_name} cuesta {monthly_price} al mes. "
                "Comparémoslo con lo que ya paga hoy antes de decidir."
            ),
            "follow_up_template": (
                "¿Le preocupa el monto mensual o no le queda claro qué incluye?"
            ),
        },
        {
            "tactic_id": "nbo-follow-up-later",
            "objection_category": "mal_momento",
            "allowed_states": ["objection_handling", "rebate", "clarification", "follow_up"],
            "strategy": "PROPOSE_FOLLOW_UP",
            "target_state": "follow_up",
            "response_type": "schedule_followup",
            "required_fact_kinds": [],
            "summary": "Respetar el momento del cliente y proponer seguimiento sin presión.",
            "response_template": (
                "Entiendo, no hace falta decidirlo ahora. Le puedo dejar la propuesta "
                "reservada y lo retomamos cuando le acomode."
            ),
            "follow_up_template": "¿Qué día de esta semana le viene mejor que lo llame?",
        },
        # Ojo: el generador determinista solo renderiza `response_template` en
        # estrategias distintas de ASK_CLARIFYING_QUESTION y ABSTAIN, que tienen
        # texto fijo. Por eso estas tácticas usan ASK_DISCOVERY_QUESTION o
        # REFRAME_VALUE: si no, el guardrail las tumba por falta de hechos.
        {
            "tactic_id": "nbo-clarify-need",
            "objection_category": "no_necesita",
            "allowed_states": ["objection_handling", "rebate", "clarification", "follow_up"],
            "strategy": "ASK_DISCOVERY_QUESTION",
            "target_state": "clarification",
            "response_type": "objection_response",
            "required_fact_kinds": ["offer_name"],
            "summary": "No insistir: entender el uso real antes de volver a ofrecer.",
            "response_template": (
                "Puede que tenga razón y {offer_name} no sea para usted. "
                "Cuénteme cómo usa hoy el servicio y lo revisamos juntos."
            ),
            "follow_up_template": "¿Qué es lo que más le falta hoy con lo que tiene?",
        },
        {
            "tactic_id": "nbo-compare-existing",
            "objection_category": "ya_tiene_similar",
            "allowed_states": ["objection_handling", "rebate", "clarification", "follow_up"],
            "strategy": "ASK_DISCOVERY_QUESTION",
            "target_state": "clarification",
            "response_type": "objection_response",
            "required_fact_kinds": ["offer_name"],
            "summary": "No competir a ciegas por precio: levantar qué tiene y qué le falta.",
            "response_template": (
                "Me parece bien que ya tenga algo contratado. Para no hacerle perder "
                "el tiempo con {offer_name}, dígame qué incluye lo suyo hoy."
            ),
            "follow_up_template": "¿Hay algo de su servicio actual que le gustaría mejorar?",
        },
        {
            "tactic_id": "nbo-build-trust",
            "objection_category": "no_confia",
            "allowed_states": ["objection_handling", "rebate", "clarification", "follow_up"],
            "strategy": "REFRAME_VALUE",
            "target_state": "rebate",
            "response_type": "objection_response",
            "required_fact_kinds": ["offer_name"],
            "summary": "Bajar el riesgo percibido con condiciones concretas, sin prometer de más.",
            "response_template": (
                "Es razonable querer estar seguro antes de comprometerse. Le detallo "
                "exactamente qué condiciones tiene {offer_name} y qué puede cancelar."
            ),
            "follow_up_template": "¿Qué parte le genera más dudas: el plazo o lo que incluye?",
        },
    ],
}


def main() -> None:
    with DEMO.open(encoding="utf-8") as f:
        clientes = json.load(f)["clientes"]

    # Una fila por oferta, sin repetir: el catálogo es conocimiento, no historial.
    ofertas: dict[str, dict[str, str]] = {}
    for entrada in clientes:
        for reco in entrada["recomendaciones"]:
            precio = reco.get("precio_mensual")
            ofertas[reco["oferta_id"]] = {
                "oferta_id": reco["oferta_id"],
                "nombre_oferta": reco["oferta"],
                "precio_mensual": f"{precio:.2f}" if precio is not None else "",
            }

    filas = CATALOGO_BASE + [ofertas[k] for k in sorted(ofertas)]

    SALIDA.mkdir(exist_ok=True)
    catalogo = SALIDA / "demo_catalog_v01.csv"
    with catalogo.open("w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=["oferta_id", "nombre_oferta", "precio_mensual"])
        escritor.writeheader()
        escritor.writerows(filas)

    playbook = SALIDA / "demo_playbook_v01.json"
    with playbook.open("w", encoding="utf-8") as f:
        json.dump(PLAYBOOK, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"catálogo: {len(filas)} ofertas -> {catalogo}")
    print(f"playbook: {len(PLAYBOOK['tactics'])} tácticas -> {playbook}")


if __name__ == "__main__":
    main()
