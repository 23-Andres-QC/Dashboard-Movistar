# Estados conversacionales del Sales Copilot

## 1. Propósito

Definir una máquina de estados ligera y explícita para el MVP textual del AI Engine. Los estados orientan la estrategia conversacional; no representan etapas del funnel comercial global ni sustituyen el estado registrado por el dashboard.

La implementación local se encuentra en `src/ai_engine/state_machine.py`. Toda transición se valida antes de mutar la sesión y queda registrada en su historial.

## 2. Principios

- Una conversación mantiene una recomendación ML activa.
- El estado limita las acciones permitidas del generador.
- El modelo puede proponer una transición, pero la orquestación debe validarla.
- Una transición inválida no se aplica silenciosamente.
- El estado debe permitir aclaración, abstención y escalamiento.
- El cierre sugerido por el AI Engine no confirma una venta real.

## 3. Estados del MVP

| Estado | Propósito | Entrada típica | Salida o acción esperada |
|---|---|---|---|
| `CONTEXT_RECEIVED` | Contexto ML validado y sesión preparada | Recomendación válida | Crear speech inicial |
| `OPENING` | Iniciar interacción de forma personalizada | Inicio de sesión | Speech y pregunta breve |
| `DISCOVERY` | Comprender necesidad o prioridad | Respuesta inicial del cliente | Pregunta o conexión con oferta |
| `OFFER_PRESENTATION` | Comunicar oferta y beneficio autorizado | Contexto suficiente | Speech de oferta |
| `OBJECTION_HANDLING` | Interpretar y atender objeción | Señal de rechazo o duda | Clarificar, responder o rebate |
| `CLARIFICATION` | Resolver ambigüedad antes de responder | Intención poco clara | Pregunta aclaratoria |
| `REBATE` | Aplicar táctica autorizada | Objeción conocida y playbook aplicable | Rebate o alternativa permitida |
| `CLOSING_GUIDANCE` | Orientar el siguiente paso de cierre | Señal de interés | Confirmación o guía de cierre |
| `FOLLOW_UP` | Recomendar contacto posterior | Mal momento o aplazamiento | Mensaje y acción de seguimiento |
| `ESCALATION` | Derivar por límite o riesgo | Solicitud no autorizada o contexto crítico | Instrucción de escalamiento |
| `COMPLETED` | Cerrar asistencia de la sesión | Cierre, seguimiento o escalamiento | Sin nueva generación normal |
| `ERROR` | Estado técnico no recuperable en el turno | Contrato o dependencia inválida | Error estructurado |

## 4. Flujo principal

```text
CONTEXT_RECEIVED
  -> OPENING
  -> DISCOVERY
  -> OFFER_PRESENTATION
  -> CLOSING_GUIDANCE
  -> COMPLETED
```

## 5. Flujo de objeción

```text
OFFER_PRESENTATION
  -> OBJECTION_HANDLING
      -> CLARIFICATION -> OBJECTION_HANDLING
      -> REBATE -> CLOSING_GUIDANCE
      -> FOLLOW_UP -> COMPLETED
      -> ESCALATION -> COMPLETED
```

Una objeción también puede aparecer durante `DISCOVERY`, `REBATE` o `CLOSING_GUIDANCE`. En esos casos la orquestación puede volver a `OBJECTION_HANDLING` si no se exceden los límites del playbook.

## 6. Eventos conceptuales

| Evento | Descripción |
|---|---|
| `RECOMMENDATION_CONTEXT_VALIDATED` | Payload ML aceptado |
| `INITIAL_SPEECH_REQUESTED` | Dashboard solicita apertura |
| `CUSTOMER_TURN_RECEIVED` | Se recibe texto del cliente |
| `ADVISOR_TURN_RECEIVED` | Se recibe texto o consulta del asesor |
| `DISCOVERY_NEEDED` | Falta información para presentar valor |
| `OFFER_PRESENTED` | El asesor o dashboard confirma presentación |
| `OBJECTION_DETECTED` | Se detecta una o más objeciones |
| `CLARIFICATION_NEEDED` | Confianza insuficiente o ambigüedad material |
| `AUTHORIZED_REBATE_AVAILABLE` | Existe táctica permitida aplicable |
| `CUSTOMER_INTEREST_SIGNAL` | Se detecta interés o intención de continuar |
| `FOLLOW_UP_REQUESTED` | El cliente prefiere otro momento |
| `ESCALATION_REQUIRED` | La respuesta excede autoridad o conocimiento |
| `SESSION_COMPLETED` | Dashboard o flujo cierra asistencia |
| `CONTRACT_ERROR` | Entrada inválida o incompatible |

## 7. Transiciones permitidas

| Desde | Evento/condición | Hacia | Acción principal |
|---|---|---|---|
| `CONTEXT_RECEIVED` | Contexto válido | `OPENING` | Generar speech inicial |
| `CONTEXT_RECEIVED` | Conocimiento ausente o inconsistente | `ESCALATION` | Abstenerse y solicitar revisión |
| `OPENING` | Cliente responde | `DISCOVERY` | Interpretar necesidad |
| `OPENING` | Oferta debe presentarse directamente | `OFFER_PRESENTATION` | Comunicar oferta |
| `DISCOVERY` | Contexto suficiente | `OFFER_PRESENTATION` | Conectar necesidad y beneficio |
| `DISCOVERY` | Ambigüedad | `CLARIFICATION` | Preguntar |
| `DISCOVERY` | Objeción detectada | `OBJECTION_HANDLING` | Clasificar y seleccionar táctica |
| `OFFER_PRESENTATION` | Interés | `CLOSING_GUIDANCE` | Orientar cierre |
| `OFFER_PRESENTATION` | Objeción | `OBJECTION_HANDLING` | Clasificar objeción |
| `OBJECTION_HANDLING` | Ambigüedad | `CLARIFICATION` | Preguntar antes de responder |
| `CLARIFICATION` | Nueva evidencia | `OBJECTION_HANDLING` | Reclasificar |
| `OBJECTION_HANDLING` | Táctica autorizada | `REBATE` | Generar respuesta grounded |
| `OBJECTION_HANDLING` | Mal momento | `FOLLOW_UP` | Proponer seguimiento |
| `OBJECTION_HANDLING` | Sin autoridad o conocimiento | `ESCALATION` | Derivar o abstenerse |
| `REBATE` | Interés | `CLOSING_GUIDANCE` | Guiar siguiente paso |
| `REBATE` | Nueva objeción | `OBJECTION_HANDLING` | Interpretar sin repetir táctica automáticamente |
| `REBATE` | Sin avance | `FOLLOW_UP` o `ESCALATION` | Cerrar de forma segura |
| `CLOSING_GUIDANCE` | Acción propuesta | `COMPLETED` | Finalizar asistencia |
| `FOLLOW_UP` | Acción propuesta | `COMPLETED` | Finalizar asistencia |
| `ESCALATION` | Derivación indicada | `COMPLETED` | Finalizar asistencia |
| Cualquier estado activo | Error no recuperable | `ERROR` | Devolver error estructurado |
| Cualquier estado activo | Guardrail bloquea la salida | `ESCALATION` | Abstenerse y solicitar revisión |

## 8. Acciones por estado

### `OPENING`

Permitidas:

- presentar saludo contextual;
- ofrecer un speech inicial breve;
- formular una pregunta de descubrimiento.

Prohibidas:

- inventar contexto del cliente;
- prometer condiciones no presentes;
- presentar alternativas no autorizadas.

### `DISCOVERY`

Permitidas:

- preguntar por necesidad o prioridad;
- resumir una necesidad expresada;
- conectar reason codes con preguntas, sin revelarlos como scoring técnico.

Prohibidas:

- volver a calcular la recomendación;
- atribuir al cliente características no recibidas.

### `OFFER_PRESENTATION`

Permitidas:

- explicar oferta, precio y beneficios autorizados;
- adaptar longitud y tono al canal;
- señalar valor relevante para el perfil recibido.

Prohibidas:

- alterar el precio;
- asegurar ahorros o resultados no respaldados;
- ocultar restricciones materiales.

### `OBJECTION_HANDLING`

Permitidas:

- identificar hasta varias objeciones;
- citar evidencia textual breve;
- pedir aclaración;
- seleccionar una estrategia del playbook.

Prohibidas:

- interpretar baja confianza como certeza;
- responder con un rebate no autorizado.

### `REBATE`

Permitidas:

- reformular valor;
- aclarar hechos;
- presentar una táctica aprobada;
- ofrecer una alternativa explícitamente autorizada;
- formular una pregunta final.

Prohibidas:

- inventar descuentos;
- insistir indefinidamente;
- cambiar la recomendación principal sin señal externa.

### `CLOSING_GUIDANCE`

Permitidas:

- sugerir confirmación de interés;
- indicar el siguiente paso operativo al asesor;
- resumir la propuesta.

Prohibidas:

- declarar una venta completada;
- ejecutar transacciones.

### `FOLLOW_UP`

Permitidas:

- sugerir agendar otro contacto;
- redactar un cierre respetuoso;
- conservar el motivo declarado.

El dashboard o sistema externo decide y registra el seguimiento real.

### `ESCALATION`

Se utiliza cuando:

- el cliente pide una condición fuera del playbook;
- hay contradicción entre ML y catálogo;
- aparece una pregunta contractual o sensible;
- faltan hechos necesarios;
- los guardrails bloquean la salida;
- existe riesgo de privacidad.

## 9. Taxonomía inicial de objeciones

| Categoría | Señal típica | Estrategias candidatas |
|---|---|---|
| `precio` | “Es muy caro” | Aclarar valor, desglosar beneficio, alternativa autorizada |
| `no_necesita` | “No lo necesito” | Descubrimiento, conectar necesidad real, cierre respetuoso |
| `ya_tiene_similar` | “Ya tengo algo parecido” | Comparar solo hechos autorizados, preguntar diferencias |
| `mal_momento` | “Ahora no puedo” | Aclarar momento, proponer seguimiento |
| `no_confia` | “No confío” | Transparencia, explicar condiciones, escalar si corresponde |
| `otro` | No encaja claramente | Preguntar o escalar |

La taxonomía debe ser validada por negocio. El dataset aporta estas categorías, pero no constituye por sí mismo autorización comercial.

## 10. Confianza y aclaración

El umbral numérico de confianza está pendiente de definición. Conceptualmente:

- confianza alta: seleccionar estrategia permitida;
- confianza media: responder con cautela y formular una pregunta;
- confianza baja o múltiples lecturas materiales: pasar a `CLARIFICATION`;
- contenido fuera de conocimiento: `ESCALATION` o abstención.

## 11. Prevención de insistencia

El playbook final debe definir límites. Como principio:

- no repetir el mismo rebate sin información nueva;
- no encadenar ofertas alternativas ilimitadas;
- respetar una negativa clara;
- preferir seguimiento o cierre cuando no hay progreso;
- registrar tácticas ya utilizadas dentro de la sesión.

Los números máximos de intentos están pendientes de aprobación comercial.

## 12. Datos mínimos de estado

```text
conversation_id
recommendation_id
current_state
active_offer_id
last_processed_turn_id
detected_objections[]
pending_clarification
used_strategy_codes[]
presented_alternative_ids[]
requires_human_review
state_updated_at
```

La persistencia concreta de estos datos se decidirá en la fase de implementación.

## 13. Cierre y resultado

El AI Engine finaliza su asistencia con un estado conversacional, no con una verdad comercial definitiva.

El dashboard o sistema externo debe confirmar resultados como:

- oferta aceptada;
- oferta rechazada;
- seguimiento acordado;
- derivación realizada;
- venta confirmada.

La relación entre estos resultados externos y el estado interno queda pendiente en el contrato con dashboard.
