# Arquitectura conceptual del AI Engine / Sales Copilot

## 1. Objetivo

Definir la arquitectura conceptual del componente de IA generativa que transforma resultados producidos por Machine Learning en asistencia conversacional estructurada para un asesor comercial.

El componente ocupa exclusivamente esta posición:

```text
ML -> AI Engine / Sales Copilot -> Dashboard
```

Este documento define responsabilidades estables. El núcleo local implementa estas responsabilidades con generación determinista, una integración LLM opcional sobre OpenAI Responses API aislada mediante un puerto neutral y una capa HTTP FastAPI delgada para el handoff al Dashboard. No incorpora infraestructura productiva.

## 2. Responsabilidad arquitectónica

El AI Engine debe:

1. aceptar y validar una recomendación externa;
2. combinarla con conocimiento comercial autorizado;
3. generar un speech inicial;
4. mantener el estado de una conversación textual;
5. interpretar intención y objeciones;
6. seleccionar una estrategia conversacional permitida;
7. generar una respuesta o rebate grounded;
8. sugerir la siguiente acción;
9. devolver una respuesta estructurada al dashboard;
10. abstenerse o escalar cuando no pueda responder de forma autorizada.

## 3. Límites

### Dentro del componente

- adaptación y validación de contratos;
- gestión de contexto y sesión;
- estados conversacionales;
- interpretación de objeciones;
- orquestación generativa;
- grounding comercial;
- guardrails y validación de salida;
- formato estructurado;
- trazabilidad técnica del AI Engine.

### Fuera del componente

- construcción de features;
- entrenamiento y serving de modelos predictivos;
- cálculo de scores;
- selección, elegibilidad o ranking NBO;
- UI y experiencia visual del dashboard;
- captura o transcripción de audio;
- ejecución de la venta;
- analítica comercial completa;
- administración maestra del catálogo.

## 4. Contextos que consume

El contexto de cada respuesta se compone de fuentes con autoridades diferentes.

| Fuente | Contenido | Autoridad |
|---|---|---|
| ML | Recomendación, predicciones, reason codes y metadatos | Equipo de ML |
| Catálogo | Nombre, precio, beneficios y restricciones | Fuente sintética demo; negocio/producto deberá sustituirla |
| Playbook | Objeciones, tácticas, rebates y escalamiento | Playbook demo no aprobado; negocio/comercial deberá sustituirlo |
| Dashboard | Turnos, actor, sesión y contexto de UI | Equipo de dashboard |
| Estado del AI Engine | Etapa, objeciones, acciones previas y referencias | Este componente |

Una fuente de menor autoridad no puede sobrescribir una de mayor autoridad. En particular, el texto generado nunca modifica la recomendación ML ni los hechos del catálogo.

## 5. Componentes internos

### 5.1 Copilot Interface

Punto lógico de entrada y salida del AI Engine.

Responsabilidades:

- recibir solicitudes del flujo de integración acordado;
- aplicar versionado de contratos;
- correlacionar `request_id`, `recommendation_id` y `conversation_id`;
- devolver éxito, abstención o error estructurado.

La implementación local usa FastAPI y schemas Pydantic exclusivamente como transporte. Los endpoints no contienen lógica conversacional y componen el mismo `SalesCopilotService` usado por demo y pruebas.

### 5.2 Contract Adapter

Valida y normaliza el payload de ML y los turnos recibidos del dashboard.

Debe detectar:

- campos obligatorios ausentes;
- tipos o enums inválidos;
- versiones incompatibles;
- identificadores inconsistentes;
- turnos duplicados o fuera de orden, si el contrato final permite detectarlos.

No completa silenciosamente valores predictivos ausentes.

### 5.3 Context Builder

Construye el contexto mínimo necesario para la tarea actual.

Puede incluir:

- oferta recomendada;
- reason codes;
- perfil resumido autorizado;
- hechos comerciales aplicables;
- etapa de conversación;
- últimos turnos relevantes;
- objeciones ya tratadas;
- tácticas todavía permitidas.

No debe enviar datasets completos ni historia irrelevante al modelo generativo.

### 5.4 Conversation State Manager

Mantiene el estado operativo de la sesión:

- etapa actual;
- recomendación activa;
- oferta ya presentada;
- objeciones detectadas;
- preguntas aclaratorias pendientes;
- rebates utilizados;
- señales de interés o cierre;
- necesidad de seguimiento o escalamiento.

Los estados aprobados se describen en `CONVERSATION_STATES.md`.

### 5.5 Intent and Objection Interpreter

Convierte un turno de lenguaje natural en una interpretación estructurada.

Salida conceptual:

```text
intención + objeciones + confianza + evidencia textual + necesidad de aclaración
```

La taxonomía inicial de objeciones es:

- `precio`;
- `no_necesita`;
- `ya_tiene_similar`;
- `mal_momento`;
- `no_confia`;
- `otro`.

Debe admitir objeciones múltiples y una categoría desconocida o ambigua.

### 5.6 Response Strategy Selector

Selecciona una acción dentro de un conjunto permitido, por ejemplo:

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

La estrategia se limita por el estado conversacional, el catálogo y el playbook. No vuelve a calcular el ranking NBO.

### 5.7 Grounded Response Generator

Genera texto para el asesor usando exclusivamente el contexto preparado.

Tipos principales:

- speech inicial;
- pregunta de descubrimiento;
- aclaración de oferta;
- respuesta a objeción;
- rebate;
- pregunta de seguimiento;
- guía de cierre;
- mensaje de seguimiento o escalamiento.

Debe diferenciar texto dirigido al cliente de orientación interna para el asesor.

La implementación actual conserva dos generadores intercambiables:

- `DeterministicContentGenerator`, baseline reproducible y fallback seguro;
- `LlmContentGenerator`, redactor opcional que consume estrategia y hechos ya decididos.

El segundo depende de `StructuredGenerationProvider`, no del SDK de OpenAI. `OpenAIResponsesProvider` es el primer adapter real y utiliza Structured Outputs. El LLM no interpreta objeciones, selecciona tácticas, cambia estado ni decide oferta.

### 5.8 Guardrails and Output Validator

Verifica antes de entregar:

- esquema estructurado válido;
- coherencia con la recomendación recibida;
- correspondencia de precios y beneficios con fuentes autorizadas;
- ausencia de descuentos inventados;
- ausencia de afirmaciones contractuales no respaldadas;
- tratamiento apropiado de contexto insuficiente;
- cumplimiento de restricciones de privacidad;
- necesidad de revisión humana.

Una respuesta que no supere validación no se entrega como respuesta comercial normal.

### 5.9 Structured Response Formatter

Transforma el resultado en el contrato esperado por el dashboard.

La respuesta separa:

- `advisor_guidance`;
- `suggested_customer_response`;
- interpretación de la objeción;
- siguiente acción;
- grounding;
- safety flags;
- metadatos de trazabilidad.

### 5.10 Trace and Audit

Registra metadatos mínimos del componente:

- IDs de correlación;
- versiones de contrato, prompt y conocimiento;
- tipo de respuesta;
- grounding utilizado;
- flags de seguridad;
- latencia técnica;
- resultado de validación.

No registra razonamiento privado del modelo ni sustituye la analítica comercial del dashboard.

### 5.11 Implementación local actual

| Responsabilidad | Módulo actual |
|---|---|
| Composición y selección de generador | `composition.py`, `configuration.py` |
| Transporte HTTP y schemas | `api.py`, `http_schemas.py` |
| Dominio interno | `src/ai_engine/domain.py` |
| Contratos externos | `contract_ml_v01.py`, `contract_dashboard_v01.py` |
| Context Builder | `context.py` |
| Fuentes demo reemplazables | `knowledge.py` |
| Máquina de estados | `state_machine.py` |
| Política conversacional | `strategy.py` |
| Puerto y generación determinista | `ports.py`, `deterministic.py` |
| Contexto y generación LLM | `llm.py` |
| Puerto neutral de proveedor | `generation.py` |
| Adapter OpenAI Responses | `openai_responses.py` |
| Configuración externa | `configuration.py`, `.env.example` |
| Guardrails y validación | `guardrails.py` |
| Orquestación | `service.py` |
| Composición y demo | `demo.py` |
| Demo LLM opt-in | `demo_llm.py` |
| Evaluación comparativa | `evaluation.py`, `fixtures/evaluation_cases_v01.json` |

Las interfaces se limitan a dependencias con una sustitución concreta: ML, persistencia, catálogo, playbook, interpretación, generación y proveedor generativo. La máquina de estados, política, Context Builder y validación permanecen como lógica interna explícita.

## 6. Flujo de inicio de conversación

1. Se recibe o recupera la recomendación ML.
2. El Contract Adapter valida los campos obligatorios.
3. El Context Builder obtiene hechos autorizados de la oferta.
4. El State Manager crea una sesión en `CONTEXT_RECEIVED`.
5. El Strategy Selector elige `GENERATE_INITIAL_SPEECH`.
6. El generador produce speech y pregunta inicial.
7. Los guardrails verifican grounding y formato.
8. Si el generador LLM falla o no supera validación, el generador determinista produce un fallback que vuelve a validarse.
9. El formatter devuelve la respuesta al dashboard.
10. La sesión pasa a `OPENING` o `DISCOVERY`.

## 7. Flujo por turno

1. El dashboard envía el turno textual.
2. Se valida identidad, orden y relación con la sesión.
3. Se interpreta intención y objeciones.
4. Se actualiza el estado conversacional.
5. Se recuperan tácticas y hechos aplicables.
6. Se selecciona una siguiente acción permitida.
7. Se genera la respuesta grounded.
8. Se valida seguridad y estructura.
9. Ante fallo técnico o de guardrail se intenta el baseline determinista y se valida nuevamente.
10. Se responde al dashboard.
11. Se registra trazabilidad mínima.

## 8. Reglas de degradación segura

| Situación | Conducta |
|---|---|
| Falta un campo obligatorio de ML | Rechazar o devolver `contract_error` |
| Falta un dato opcional | Omitirlo y ajustar la respuesta sin inventarlo |
| La objeción es ambigua | Formular una pregunta aclaratoria |
| Se solicita un descuento no autorizado | No prometerlo; explicar límite o escalar |
| El cliente pregunta algo ajeno al conocimiento disponible | Abstenerse o escalar |
| La recomendación contradice el catálogo | Bloquear respuesta comercial y reportar inconsistencia |
| La salida no cumple el esquema | Fallback determinista; si tampoco valida, error seguro |
| El proveedor LLM no está disponible | Fallback determinista con flag y traza interna |
| El LLM intenta cambiar oferta, estrategia o IDs | Bloquear, regenerar con baseline y conservar autoridades |
| Existe riesgo de privacidad o contenido sensible | Minimizar, bloquear o escalar según política |

## 9. MVP de hackathon

### Capacidades

- conversación textual;
- una recomendación activa por sesión;
- speech inicial;
- interpretación de objeciones;
- rebate desde playbook autorizado;
- siguiente acción;
- salida estructurada;
- trazabilidad básica;
- abstención y escalamiento.

### Simplificaciones

- catálogo y playbook pequeños en formatos estructurados;
- estado local o persistencia ligera;
- sin base vectorial;
- sin audio;
- sin aprendizaje en línea;
- sin agentes múltiples;
- sin integración con sistemas internos de venta;
- sin memoria permanente del cliente.

### Tecnologías del núcleo y candidatas futuras

| Capacidad | Candidatos |
|---|---|
| Lenguaje | Python, seleccionado para el núcleo local |
| Interfaz de servicio | FastAPI u otra interfaz HTTP ligera |
| Validación | Pydantic o JSON Schema |
| Orquestación | Código explícito y máquina de estados ligera |
| Generación | API de LLM con salidas estructuradas |
| Conocimiento | JSON, Markdown o CSV versionado |
| Estado | Memoria local o SQLite |
| Entrega incremental | SSE o WebSocket, solo si dashboard lo requiere |

La generación LLM permanece únicamente como reemplazo opcional de `ContentGenerator`. FastAPI está implementado como transporte local de integración; persistencia externa y entrega incremental siguen fuera del alcance.

## 10. Evolución productiva eventual

Una versión productiva podría incorporar, sujeto a nuevas decisiones:

- servicio independiente y contenedorizado;
- autenticación y autorización;
- gestor distribuido de sesiones;
- Redis para estado temporal;
- PostgreSQL para auditoría y configuración;
- recuperación semántica si el corpus lo justifica;
- gateway intercambiable de modelos y proveedores;
- transcripción de voz como dependencia separada;
- redacción o tokenización de PII;
- rate limiting, timeouts y circuit breakers;
- versionado y aprobación de prompts y playbooks;
- evaluación continua del componente;
- monitoreo de grounding, seguridad, costo y latencia;
- políticas formales de retención.

La arquitectura productiva no forma parte del MVP aprobado.

## 11. Atributos de calidad

- **Seguridad:** no inventar ni exponer información innecesaria.
- **Trazabilidad:** correlacionar recomendación, conversación y respuesta.
- **Interoperabilidad:** contratos versionados e independientes de proveedor.
- **Auditabilidad:** fuentes y versiones identificables.
- **Disponibilidad degradada:** abstención controlada ante fallos.
- **Latencia conversacional:** objetivo pendiente de acordar con dashboard.
- **Privacidad:** política pendiente de aprobar con responsables del proyecto.

## 12. Integración LLM vigente

La estructura del contexto autorizado, el schema de salida, el adapter OpenAI, fallback, configuración y evaluación se detallan en `LLM_INTEGRATION.md`.

## 13. Decisiones relacionadas

Esta arquitectura aplica las decisiones D-0001 a D-0009 de `DECISIONS.md`.
