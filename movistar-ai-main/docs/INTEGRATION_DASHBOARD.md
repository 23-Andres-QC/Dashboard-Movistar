# Handoff para Dashboard

## ¿Qué me entrega Frank?

Un AI Engine local que recibe una recomendación ML, crea una conversación y devuelve guidance JSON para la UI. Incluye speech inicial, interpretación determinista de objeciones, siguiente estrategia, respuesta grounded y flags de seguridad.

El modo predeterminado es determinista. No necesitas LLM local, cuenta OpenAI ni API key.

## Cómo levantarlo

Requiere Python 3.11 o superior. Desde la raíz del repo, en PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\ai-engine-api.exe
```

En macOS/Linux, cambia las rutas por `.venv/bin/python` y `.venv/bin/ai-engine-api`.

El servicio queda en `http://127.0.0.1:8000`. Swagger UI está en `http://127.0.0.1:8000/docs` y OpenAPI en `/openapi.json`.

## Endpoints

- `GET /health`: estado, versión, modo de generación y versiones de contrato.
- `POST /v1/conversations`: crea una sesión desde una recomendación ML 0.1 y devuelve el speech inicial.
- `POST /v1/turns`: procesa un turno textual del cliente y devuelve guidance actualizado.

Las sesiones viven en memoria. Inicia la conversación antes de enviar turnos y no ejecutes varios workers: reiniciar el proceso borra las sesiones.

## Probar el flujo completo

Health check:

```powershell
curl.exe http://127.0.0.1:8000/health
```

Respuesta:

```json
{
  "status": "ok",
  "service": "ai-engine-sales-copilot",
  "version": "0.4.0",
  "generator_mode": "deterministic",
  "ml_contract_version": "0.1",
  "dashboard_contract_version": "0.1"
}
```

Crear conversación:

```powershell
curl.exe -X POST http://127.0.0.1:8000/v1/conversations -H "Content-Type: application/json" --data-binary "@fixtures/ml_recommendation_v01.json"
```

La respuesta `201` usa el contrato Dashboard 0.1. Lo esencial para la apertura:

```json
{
  "contract_version": "0.1",
  "response_id": "resp-session-start",
  "request_id": "req-demo-001",
  "conversation_id": "conv-rec-demo-001",
  "in_reply_to_turn_id": "session-start",
  "created_at": "2026-08-12T23:40:15.032668Z",
  "response_type": "initial_speech",
  "conversation_stage": "opening",
  "advisor_guidance": {
    "recommended_action": "PRESENT_INITIAL_SPEECH",
    "summary": "Presentar la oferta recomendada y abrir descubrimiento.",
    "suggested_customer_response": "Quisiera comentarle una opción que podría ajustarse a sus necesidades: Plan Movil Ilimitado.",
    "follow_up_question": "¿Qué aspecto de su servicio actual le gustaría mejorar?",
    "alternative_offer_id": null
  },
  "grounding": {
    "offer_id": "OF004",
    "fact_ids": ["demo_catalog:OF004:name"]
  },
  "safety": {
    "grounded": true,
    "requires_human_review": false,
    "flags": ["DEMO_CATALOG_NOT_OFFICIAL"]
  },
  "trace": {
    "recommendation_id": "rec-demo-001",
    "prompt_version": "deterministic-core-v2",
    "knowledge_version": "challenge-synthetic-catalog-2026+demo-playbook-0.1"
  }
}
```

Enviar el turno de precio:

```powershell
curl.exe -X POST http://127.0.0.1:8000/v1/turns -H "Content-Type: application/json" --data-binary "@fixtures/dashboard_turn_v01.json"
```

El fixture contiene:

```json
{
  "contract_version": "0.1",
  "request_id": "req-turn-demo-001",
  "conversation_id": "conv-rec-demo-001",
  "turn_id": "turn-demo-001",
  "speaker": "customer",
  "text": "Me parece demasiado caro",
  "timestamp": "2026-08-12T15:30:00Z"
}
```

La respuesta `200` conserva `OF004` y `rec-demo-001`, detecta `objection.category = "precio"` y entrega:

```json
{
  "contract_version": "0.1",
  "response_id": "resp-turn-demo-001",
  "request_id": "req-turn-demo-001",
  "conversation_id": "conv-rec-demo-001",
  "in_reply_to_turn_id": "turn-demo-001",
  "response_type": "rebate",
  "conversation_stage": "rebate",
  "advisor_guidance": {
    "recommended_action": "REFRAME_VALUE",
    "summary": "Reconocer la preocupación y aclarar el valor sin ofrecer descuentos.",
    "suggested_customer_response": "Entiendo que el precio es importante. Plan Movil Ilimitado tiene un precio mensual de S/ 99.90. Revisemos si sus características responden a lo que necesita.",
    "follow_up_question": "¿Su principal preocupación es el monto mensual o no tener claro el valor de la oferta?",
    "alternative_offer_id": null
  },
  "objection": {
    "category": "precio",
    "secondary_categories": [],
    "confidence": 0.95,
    "customer_evidence": "Me parece demasiado caro"
  },
  "grounding": {
    "offer_id": "OF004",
    "fact_ids": ["demo_catalog:OF004:name", "demo_catalog:OF004:monthly_price"]
  },
  "safety": {
    "grounded": true,
    "requires_human_review": false,
    "flags": ["DEMO_CATALOG_NOT_OFFICIAL", "DEMO_PLAYBOOK_NOT_APPROVED"]
  },
  "trace": {
    "recommendation_id": "rec-demo-001",
    "prompt_version": "deterministic-core-v2",
    "knowledge_version": "challenge-synthetic-catalog-2026+demo-playbook-0.1"
  }
}
```

`created_at` también se entrega en ISO 8601 y cambia en cada ejecución; se omitió arriba para abreviar.

## Campos importantes para la UI

- Muestra `advisor_guidance.suggested_customer_response` como speech sugerido y `follow_up_question` cuando no sea `null`.
- Usa `recommended_action`, `response_type` y `conversation_stage` para decidir el tratamiento visual; los enums aún son provisionales.
- Muestra una alerta o evita presentar el speech cuando `requires_human_review` sea `true`, `grounded` sea `false` o exista `error`.
- Conserva `conversation_id`, genera un `request_id` y `turn_id` nuevos por turno, y no cambies `recommendation_id` ni `offer_id`.
- `summary` es orientación interna para el asesor. `grounding`, `safety` y `trace` sirven para control y diagnóstico, no son copy para el cliente.

## Errores HTTP

Los errores de transporte usan siempre esta forma:

```json
{
  "error": {
    "code": "CONVERSATION_NOT_FOUND",
    "message": "Conversation 'conv-missing' does not exist.",
    "details": []
  }
}
```

- `422 ML_CONTRACT_INVALID`: recomendación de inicio incompleta o inválida.
- `422 DASHBOARD_CONTRACT_INVALID`: turno incompleto o inválido.
- `404 CONVERSATION_NOT_FOUND`: no se creó la sesión o el servidor se reinició.
- `409 CONVERSATION_ALREADY_EXISTS`: se repitió el inicio con la misma recomendación.
- `409 TURN_ALREADY_PROCESSED`: se reutilizó un `turn_id`.
- `409 INVALID_CONVERSATION_STATE`: el turno no es válido en el estado actual.

Una abstención comercial no es un fallo HTTP: llega como respuesta Dashboard 0.1 con `error`, flags de seguridad y posible revisión humana.

## Configuración opcional

```text
AI_ENGINE_HOST=127.0.0.1
AI_ENGINE_PORT=8000
AI_ENGINE_CORS_ORIGINS=*
AI_ENGINE_GENERATOR=deterministic
```

`AI_ENGINE_CORS_ORIGINS=*` facilita desarrollo local y no es configuración productiva. Para probar el adapter OpenAI existente instala `.[openai]`, usa `AI_ENGINE_GENERATOR=openai` y configura `OPENAI_API_KEY`, `OPENAI_MODEL` y opcionalmente `AI_ENGINE_LLM_TIMEOUT_SECONDS`. El contrato HTTP no cambia y, si el proveedor falla o viola guardrails, el servicio intenta el fallback determinista.

## Qué puede cambiar

Los contratos ML 0.1 y Dashboard 0.1 siguen pendientes de confirmación. Debemos acordar propiedad y expiración de IDs, retries/idempotencia, orden de turnos, enums y longitudes de UI, timeouts, errores, CORS/origen de despliegue y privacidad. La persistencia en memoria también tendrá que sustituirse si se requieren reinicios, concurrencia entre procesos o despliegue real.

## Responsabilidades

- ML elige la recomendación, oferta y predicciones.
- AI Engine conserva esa recomendación, gestiona estado y estrategia, usa conocimiento autorizado, redacta guidance y aplica guardrails.
- Dashboard captura turnos, mantiene los IDs de integración y presenta guidance/alertas; no necesita conocer el proveedor generativo.
- Negocio debe aprobar catálogo, playbook, condiciones, tono y límites de uso.

## Costos y escalabilidad

El LLM se invoca por interacción que requiere generación, no una vez por cada cliente del dataset. El desarrollo y la integración básica pueden ejecutarse en modo determinista sin costo de API. Una demo LLM puede activar un proveedor configurado sin cambiar al Dashboard.

La arquitectura no depende de un proveedor concreto. En producción habrá que medir tokens por generación, cantidad de conversaciones y turnos, latencia, concurrencia e infraestructura. Un modelo local elimina la tarifa por llamada, pero mantiene costos de cómputo y operación. La elección final sigue pendiente de benchmark; por eso no se incluyen estimaciones de tráfico ni cifras de costo.
