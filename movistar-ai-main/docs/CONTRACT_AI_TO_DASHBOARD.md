# Contrato conceptual AI Engine <-> Dashboard

## 1. Propósito

Definir el intercambio entre el dashboard del asesor y el AI Engine para iniciar una conversación, enviar turnos y presentar asistencia comercial estructurada.

## 2. Estado del contrato

- **Versión documental:** 0.1.
- **Estado:** borrador para alineación con el integrante de dashboard.
- **Productor de guidance:** AI Engine.
- **Consumidor y productor de turnos:** dashboard.
- **Implementación:** existen adapter de entrada, serializador de salida y transporte HTTP local de referencia para 0.1; todavía no existe confirmación del equipo de Dashboard.

Los nombres y tipos son conceptuales hasta su confirmación conjunta.

La coreografía HTTP provisional mantiene estos contratos aislados: `POST /v1/conversations` recibe una recomendación ML 0.1 para crear la sesión y `POST /v1/turns` recibe un turno Dashboard 0.1. Ambos devuelven la misma salida Dashboard 0.1. Los paths HTTP no convierten estos nombres en dominio interno estable.

## 3. Direcciones del intercambio

El contrato cubre:

1. dashboard -> AI Engine: creación o referencia de sesión;
2. dashboard -> AI Engine: turno textual del asesor o cliente;
3. AI Engine -> dashboard: guidance estructurado;
4. AI Engine -> dashboard: abstención, escalamiento o error;
5. opcionalmente, dashboard -> AI Engine: feedback o resultado de una sugerencia.

## 4. Entrada obligatoria propuesta por turno

| Campo | Tipo conceptual | Descripción | Regla |
|---|---|---|---|
| `request_id` | string | Identificador de la solicitud | Permite correlación e idempotencia |
| `conversation_id` | string | Identificador de sesión | Estable durante toda la conversación |
| `turn_id` | string | Identificador del turno | Único dentro de la sesión |
| `speaker` | enum | `customer` o `advisor` | No se infiere silenciosamente |
| `text` | string | Texto o transcripción del turno | No vacío para un evento conversacional |
| `timestamp` | datetime ISO 8601 | Momento del turno | Debe preservar orden |

Para procesar el primer turno también debe existir una recomendación ML válida asociada a la conversación. La forma exacta de asociación está pendiente de confirmar.

### Comportamiento ante ausencia

El AI Engine devuelve `DASHBOARD_CONTRACT_INVALID` y no genera una respuesta comercial normal.

## 5. Entrada opcional propuesta

| Campo | Tipo conceptual | Uso | Conducta si falta |
|---|---|---|---|
| `advisor_id` | string anonimizado | Auditoría y continuidad | Procesar sin atribución personal |
| `channel` | enum/string | Adaptar formato del mensaje | Usar canal ML o estilo neutro |
| `language` | string | Idioma de respuesta | Usar idioma configurado |
| `ui_context` | object | Indicar vista o acción actual | No adaptar a UI específica |
| `selected_suggestion_id` | string | Saber qué guidance utilizó el asesor | No inferir adopción |
| `event_type` | enum | Distinguir texto, feedback o control | Tratar como turno textual por defecto solo si se acuerda |
| `sequence_number` | integer | Detectar orden o pérdida | Usar timestamp y turn ID |
| `metadata` | object | Contexto no sensible acordado | Ignorar campos desconocidos de forma controlada |

## 6. Salida obligatoria propuesta del AI Engine

| Campo | Tipo conceptual | Descripción |
|---|---|---|
| `response_id` | string | Identificador único de respuesta |
| `request_id` | string | Correlación con la solicitud |
| `conversation_id` | string | Sesión a la que pertenece |
| `in_reply_to_turn_id` | string | Turno procesado |
| `created_at` | datetime ISO 8601 | Momento de generación |
| `response_type` | enum | Tipo de guidance o resultado |
| `conversation_stage` | enum | Estado conversacional resultante |
| `advisor_guidance.recommended_action` | enum | Siguiente acción sugerida |
| `advisor_guidance.suggested_customer_response` | string/null | Texto que el asesor puede utilizar |
| `safety.grounded` | boolean | Resultado de validación de grounding |
| `safety.requires_human_review` | boolean | Indica revisión o escalamiento |
| `safety.flags` | array[string] | Alertas aplicables, puede estar vacío |
| `trace.recommendation_id` | string | Recomendación ML vigente |
| `trace.prompt_version` | string | Versión lógica de la instrucción |
| `trace.knowledge_version` | string | Versión de catálogo/playbook |

Si la respuesta es un error, `suggested_customer_response` puede ser `null`, pero debe existir un bloque de error estructurado.

## 7. Salida opcional propuesta

| Campo | Tipo conceptual | Uso en dashboard |
|---|---|---|
| `advisor_guidance.summary` | string | Orientación interna breve |
| `advisor_guidance.follow_up_question` | string | Pregunta sugerida |
| `advisor_guidance.alternative_offer_id` | string | Alternativa autorizada |
| `advisor_guidance.display_priority` | enum/int | Orden visual |
| `objection.category` | enum | Categoría principal |
| `objection.secondary_categories` | array[enum] | Objeciones adicionales |
| `objection.confidence` | number | Confianza de interpretación |
| `objection.customer_evidence` | string | Fragmento justificativo del turno |
| `grounding.fact_ids` | array[string] | Hechos utilizados |
| `grounding.offer_id` | string | Oferta sobre la que se responde |
| `suggested_questions` | array[string] | Opciones adicionales |
| `display_hints` | object | Pistas visuales no vinculantes |
| `trace.llm_provider` | string | Diagnóstico técnico, no necesariamente visible |
| `trace.latency_ms` | integer | Diagnóstico técnico |

## 8. Campos y decisiones pendientes de confirmar con dashboard

| Tema o campo | Pregunta que debe resolver el equipo | Impacto |
|---|---|---|
| `contract_version` | ¿Qué esquema de versionado usaremos? | Compatibilidad |
| Coreografía | ¿Dashboard pasa el payload ML o solo un `recommendation_id`? | Inicialización de sesión |
| `conversation_id` | ¿Quién lo crea y cuándo expira? | Estado y correlación |
| `request_id` | ¿Lo genera dashboard por cada intento? | Retries e idempotencia |
| `turn_id` | ¿Es único y estable durante retries? | Duplicados |
| `speaker` | ¿Cómo se distingue cliente, asesor y sistema? | Interpretación |
| Orden | ¿Habrá `sequence_number` además de timestamp? | Turnos fuera de orden |
| Entrada | ¿Texto manual, transcripción final o segmentos incrementales? | Flujo y latencia |
| Streaming | ¿El dashboard requiere tokens/eventos parciales o respuesta completa? | Transporte |
| Estados | ¿Qué estados y acciones necesita renderizar la UI? | Enums compartidos |
| Longitudes | ¿Cuánto texto cabe en cada bloque visual? | Prompt y formato |
| Guidance interno | ¿Qué campos no deben mostrarse al cliente? | Diseño y seguridad |
| Alternativas | ¿Cómo presenta y confirma una oferta alternativa? | Control comercial |
| Errores | ¿Qué estructura y mensajes espera la UI? | Degradación |
| Timeouts | ¿Cuánto puede esperar el dashboard? | Tecnología y UX |
| Retries | ¿Cómo se reintenta sin duplicar estado? | Idempotencia |
| Feedback | ¿Se notificará si el asesor usó, editó o ignoró una sugerencia? | Evaluación del componente |
| Resultado | ¿Se enviará aceptación, rechazo, seguimiento o cierre? | Estado final |
| Seguridad | ¿Cómo llega identidad/autorización del asesor? | Acceso |
| Privacidad | ¿Se almacenan textos completos o solo metadatos? | Retención |

## 9. Enums conceptuales

### `response_type`

- `initial_speech`;
- `discovery_question`;
- `objection_analysis`;
- `objection_response`;
- `rebate`;
- `closing_guidance`;
- `schedule_followup`;
- `escalation`;
- `insufficient_context`;
- `error`.

### `recommended_action`

- `PRESENT_INITIAL_SPEECH`;
- `ASK_DISCOVERY_QUESTION`;
- `ASK_CLARIFYING_QUESTION`;
- `EXPLAIN_BENEFIT`;
- `REFRAME_VALUE`;
- `ADDRESS_TRUST`;
- `PRESENT_AUTHORIZED_REBATE`;
- `PRESENT_AUTHORIZED_ALTERNATIVE`;
- `PROPOSE_FOLLOW_UP`;
- `GUIDE_CLOSE`;
- `ESCALATE_TO_HUMAN`;
- `ABSTAIN`.

Los enums definitivos deben confirmarse con la UI y los estados de `CONVERSATION_STATES.md`.

## 10. Ejemplo de turno de entrada

```json
{
  "contract_version": "0.1",
  "request_id": "req-turn-004",
  "conversation_id": "conv-789",
  "turn_id": "turn-004",
  "speaker": "customer",
  "text": "Me parece demasiado caro y ya pago bastante.",
  "timestamp": "2026-08-11T10:34:12-05:00",
  "channel": "Call In",
  "language": "es-PE"
}
```

## 11. Ejemplo de salida

```json
{
  "contract_version": "0.1",
  "response_id": "resp-004",
  "request_id": "req-turn-004",
  "conversation_id": "conv-789",
  "in_reply_to_turn_id": "turn-004",
  "created_at": "2026-08-11T10:34:13-05:00",
  "response_type": "objection_response",
  "conversation_stage": "objection_handling",
  "advisor_guidance": {
    "recommended_action": "REFRAME_VALUE",
    "summary": "Reconocer la preocupación y aclarar el valor sin ofrecer descuentos no autorizados.",
    "suggested_customer_response": "Entiendo que el precio es importante. La diferencia principal de esta opción es...",
    "follow_up_question": "¿Lo que más le preocupa es el monto mensual o no tener claro el beneficio adicional?",
    "alternative_offer_id": null
  },
  "objection": {
    "category": "precio",
    "secondary_categories": [],
    "confidence": 0.94,
    "customer_evidence": "Me parece demasiado caro"
  },
  "grounding": {
    "offer_id": "OF004",
    "fact_ids": ["OF004_PRICE", "OF004_UNLIMITED_DATA"]
  },
  "safety": {
    "grounded": true,
    "requires_human_review": false,
    "flags": []
  },
  "trace": {
    "recommendation_id": "rec-456",
    "prompt_version": "objection-v1",
    "knowledge_version": "catalog-2026-08"
  }
}
```

Los textos son ilustrativos y no constituyen copy comercial aprobado.

## 12. Errores estructurados propuestos

| Código | Situación |
|---|---|
| `DASHBOARD_CONTRACT_INVALID` | Falta o invalidez de entrada obligatoria |
| `CONVERSATION_NOT_FOUND` | Sesión inexistente o expirada |
| `TURN_ALREADY_PROCESSED` | Retry o turno duplicado |
| `TURN_OUT_OF_ORDER` | Orden inconsistente |
| `RECOMMENDATION_CONTEXT_MISSING` | No existe recomendación asociada |
| `KNOWLEDGE_GROUNDING_FAILED` | No se pudo validar una respuesta comercial |
| `HUMAN_REVIEW_REQUIRED` | La situación debe escalarse |
| `AI_ENGINE_UNAVAILABLE` | Fallo temporal del componente |

## 13. Criterio de aceptación del contrato

El contrato podrá pasar de borrador a candidato aprobado cuando:

- se confirme la coreografía de inicio de sesión;
- dashboard acepte campos obligatorios de entrada y salida;
- se acuerden IDs, orden e idempotencia;
- se cierren enums y límites de presentación;
- se decida si habrá streaming;
- se acuerden errores, timeouts y retries;
- se definan ejemplos válidos e inválidos.
