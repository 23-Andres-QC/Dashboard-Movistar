# Integración LLM del AI Engine

## 1. Alcance

Esta fase incorpora generación de lenguaje real únicamente como implementación opcional del puerto `ContentGenerator`. No altera la arquitectura central ni convierte al LLM en orquestador.

Las autoridades permanecen separadas:

| Decisión o dato | Autoridad |
|---|---|
| Recomendación, oferta y predicciones | Machine Learning externo |
| Estado y transición | `ConversationStateMachine` |
| Estrategia siguiente | `ConversationalStrategyPolicy` |
| Hechos comerciales | `CommercialCatalog` |
| Táctica comercial | `SalesPlaybook` |
| Redacción sugerida | `ContentGenerator` determinista o LLM |
| Entrega o bloqueo | `ResponseValidator` y orquestación |
| Forma externa | adapters ML 0.1 y Dashboard 0.1 |

El intérprete de objeciones continúa siendo `RuleBasedObjectionInterpreter`; el LLM no participa todavía en esa clasificación.

## 2. Flujo implementado

```text
ML 0.1 fixture
  -> adapter ML 0.1
  -> dominio interno
  -> estado + intérprete determinista + estrategia
  -> contexto LLM mínimo y autorizado
  -> ContentGenerator LLM
      -> puerto neutral StructuredGenerationProvider
      -> adapter OpenAI Responses API
  -> GuidanceDraft estructurado
  -> guardrails
      -> válido: respuesta interna
      -> inválido/fallo: ContentGenerator determinista y segunda validación
      -> fallback inválido: abstención/escalamiento
  -> adapter Dashboard 0.1
```

Los contratos externos 0.1 no se modificaron. La traza de generación se mantiene interna para evaluación; el formatter Dashboard 0.1 continúa exponiendo únicamente sus campos provisionales existentes.

## 3. Límites de código

| Archivo | Responsabilidad |
|---|---|
| `ports.py` | Conserva el puerto de aplicación `ContentGenerator` |
| `generation.py` | Define solicitud, resultado, uso y errores neutrales al proveedor |
| `llm.py` | Construye contexto autorizado, define esquema y transforma salida a dominio |
| `openai_responses.py` | Único módulo acoplado al SDK y a Responses API |
| `configuration.py` | Lee clave, modelo y timeout desde variables externas |
| `service.py` | Valida generación y activa fallback tanto por fallo técnico como por guardrail |
| `deterministic.py` | Baseline, fallback y referencia reproducible |
| `evaluation.py` | Ejecuta casos comunes y obtiene métricas comparables |

El SDK se importa de manera diferida dentro del adapter. La suite normal puede ejecutarse sin instalarlo. `pyproject.toml` publica el extra opcional `openai` con el SDK oficial mínimo.

## 4. Contexto enviado

`AuthorizedPromptContextBuilder` construye un objeto nuevo para cada llamada. Incluye solamente:

- `recommendation_id` y `offer_id` inmutables;
- estado conversacional vigente;
- hasta cuatro turnos recientes con actor y texto;
- objeción ya interpretada, si existe;
- estrategia y estado destino ya seleccionados;
- oferta activa;
- únicamente los hechos de catálogo requeridos para la apertura o táctica;
- táctica del playbook ya elegida, si aplica;
- restricciones explícitas de identidad, estrategia, grounding y no invención.

No incluye:

- datasets ni filas de clientes;
- alternativas ML;
- probabilidades, ranking o metadatos del modelo ML;
- perfil completo ni `customer_id`;
- catálogo o playbook completos;
- razonamiento interno;
- estados de otras conversaciones.

El playbook y catálogo actuales son sintéticos. En una integración real siguen requiriendo sustitución o aprobación comercial.

## 5. Salida estructurada

La llamada utiliza Responses API y `text.format` con un JSON Schema estricto. El modelo devuelve:

- `response_type` esperado;
- `recommended_action` esperada;
- `summary` para el asesor;
- `suggested_customer_response`;
- `follow_up_question` o `null`;
- `grounding_fact_ids`;
- `claims`, cada uno con `text` y `fact_id`;
- `source_recommendation_id` inmutable;
- `source_offer_id` inmutable.

El schema restringe tipo, acción e identidades al valor decidido aguas arriba. Después se aplica validación local de tipos y enums, seguida de los guardrails de dominio.

## 6. Guardrails y fallback

Los guardrails comprueban después de toda generación:

- identidad de recomendación y oferta;
- coincidencia exacta con la estrategia seleccionada;
- tipo de respuesta definido por la táctica;
- IDs de grounding conocidos;
- correspondencia entre grounding y claims;
- coincidencia exacta de cada claim con el valor autorizado del catálogo;
- presencia del claim en el contenido generado;
- hechos requeridos por la táctica;
- precios, porcentajes y términos promocionales respaldados.

Se intenta el generador determinista cuando:

- el proveedor no está disponible o supera el timeout;
- existe rechazo, respuesta incompleta o JSON inutilizable;
- la estructura local no es válida;
- el LLM cambia oferta, recomendación, tipo o estrategia;
- los guardrails detectan grounding o claims no autorizados.

El fallback atraviesa los mismos guardrails. Una respuesta degradada incluye internamente `fallback_used`, motivo, latencia y uso reportado por el intento primario, y añade `GENERATION_FALLBACK_USED` a los flags. Si tampoco puede validarse, el servicio se abstiene y escala.

## 7. Configuración y ejecución

No existe modelo hardcodeado. Para la ruta real se requieren:

```text
AI_ENGINE_GENERATOR=openai
OPENAI_API_KEY
OPENAI_MODEL
AI_ENGINE_LLM_TIMEOUT_SECONDS  # opcional; 20 por defecto
```

Instalación y demo manual en PowerShell:

```powershell
python -m pip install -e ".[openai]"
$env:AI_ENGINE_GENERATOR="openai"
$env:OPENAI_API_KEY="<configurar-fuera-de-Git>"
$env:OPENAI_MODEL="<modelo-compatible-con-structured-outputs>"
$env:AI_ENGINE_LLM_TIMEOUT_SECONDS="20"
$env:PYTHONPATH="src"
python -m ai_engine.demo_llm
```

La llamada configura `store=False`, no usa conversación persistida por el proveedor y no habilita herramientas, streaming ni agentes.

La prueba real es separada y requiere opt-in explícito porque puede consumir red y crédito:

```powershell
$env:AI_ENGINE_RUN_OPENAI_INTEGRATION="1"
python -m unittest discover -s tests -p "test_openai_integration_opt_in.py" -v
```

## 8. Evaluación

`fixtures/evaluation_cases_v01.json` contiene escenarios sintéticos comunes a ambos generadores: apertura, precio, mal momento, ambigüedad y ausencia de conocimiento con abstención. El arnés reporta:

- cumplimiento estructural;
- grounding;
- conservación de IDs;
- ausencia de frases promocionales no autorizadas;
- respeto de estrategia y tipo de respuesta;
- consistencia con objeción y contexto;
- abstención o fallback;
- latencia extremo a extremo;
- latencia del proveedor para la respuesta final;
- tokens de entrada, salida y total cuando el proveedor los informa;
- un proxy mecánico de naturalidad;
- focos explícitos para revisión humana de naturalidad y calidad.

El proxy de naturalidad solo detecta defectos básicos de forma. No reemplaza evaluación humana ni un grader semántico.

```powershell
$env:PYTHONPATH="src"
python -m ai_engine.evaluation --generator deterministic
python -m ai_engine.evaluation --generator openai
```

La segunda orden requiere la configuración y el SDK anteriores y puede efectuar varias llamadas pagadas.

## 9. Riesgos y pendientes

- Los guardrails léxicos y estructurados no garantizan detectar todo beneficio implícito inventado si el modelo omite declararlo como claim.
- El prompt y los casos son de demostración, no copy ni playbook aprobados.
- Falta política aprobada de privacidad, retención y datos permitidos antes de usar conversaciones reales.
- Falta fijar un modelo autorizado, presupuesto, límites de tasa y objetivo de latencia.
- La evaluación de calidad requiere revisión humana ciega y un conjunto mayor antes de cualquier uso real.
- La traza de proveedor/tokens aún no forma parte del contrato Dashboard 0.1 y no debe añadirse sin acuerdo externo.

## 10. Referencias técnicas

- [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs)
- [Migración y conceptos de Responses API](https://developers.openai.com/api/docs/guides/migrate-to-responses)
