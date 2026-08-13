# Bitácora del proyecto

## 2026-08-10 — Inspección y adopción inicial

### Objetivo

Inspeccionar el contenido completo de la carpeta sin implementar y reconstruir requisitos, flujo, datos y posibles fronteras técnicas.

### Trabajo realizado

- Se inventariaron los siete artefactos existentes.
- Se leyeron y verificaron los dos PDF, el diccionario DOCX, el informe Markdown y los tres CSV.
- Se confirmó que no existían código, pruebas, Git ni núcleo documental.
- Se identificaron requisitos generales del desafío de Personalización comercial inteligente.
- Se perfiló la integridad y las limitaciones de los datos sintéticos.
- Se formuló una primera arquitectura que cubría el flujo NBO completo.

### Resultado

Se produjo una propuesta conceptual sin modificar el proyecto. La propuesta inicial abarcó más responsabilidades que las correspondientes al propietario de este proyecto.

### Archivos actualizados

Ninguno.

## 2026-08-11 — Corrección de alcance

### Objetivo

Limitar el proyecto a la responsabilidad real de Ingeniería de IA / IA generativa.

### Decisión de alcance

El proyecto se ubica exclusivamente entre los componentes externos de ML y dashboard:

```text
ML -> AI Engine / Sales Copilot -> Dashboard
```

### Trabajo realizado

- Se excluyeron formalmente modelos ML, feature engineering, entrenamiento, ranking NBO, dashboard y analítica completa.
- Se redefinieron las responsabilidades como speech personalizado, asistencia conversacional, interpretación de objeciones, rebate, siguiente acción y salida estructurada.
- Se propuso una arquitectura conceptual interna.
- Se separó el MVP textual de hackathon de una eventual arquitectura productiva.
- Se propusieron las decisiones D-0004 a D-0009.

### Resultado

El usuario aprobó la arquitectura conceptual corregida y las decisiones D-0004 a D-0009.

### Archivos actualizados

Ninguno en esta etapa.

## 2026-08-11 — Adopción documental aprobada

### Objetivo

Crear únicamente la documentación de gobierno, arquitectura, contratos y estados conversacionales, sin iniciar implementación.

### Trabajo realizado

- Se crearon `README.md`, `STATE.md`, `LOGBOOK.md` y `DECISIONS.md`.
- Se documentó la arquitectura en `docs/ARCHITECTURE_AI_ENGINE.md`.
- Se documentó el contrato ML -> AI Engine en `docs/CONTRACT_ML_TO_AI.md`.
- Se documentó el contrato AI Engine <-> Dashboard en `docs/CONTRACT_AI_TO_DASHBOARD.md`.
- Se documentaron estados y transiciones en `docs/CONVERSATION_STATES.md`.
- Los contratos separan campos obligatorios, opcionales y pendientes de confirmar.
- Se actualizaron estado, dependencias, riesgos y siguiente acción.

### Decisiones formalizadas

- D-0001 a D-0009 quedaron aceptadas.

### Verificación

- Se comprobó consistencia de alcance entre los ocho documentos.
- No se creó código, API, configuración ejecutable, prompt, prueba ni dependencia.
- No se movieron ni modificaron los siete artefactos originales.

### Siguiente paso

Alinear los campos pendientes de ambos contratos con los equipos de ML y dashboard y validar catálogo/playbook con negocio. No implementar hasta una nueva autorización explícita.

## 2026-08-11 — Primer vertical slice mock ejecutable

### Objetivo

Implementar exclusivamente el recorrido mínimo aprobado, manteniendo contratos provisionales aislados y todas las dependencias externas reemplazadas por mocks.

### Trabajo realizado

- Se creó el paquete Python mínimo bajo `src/ai_engine`.
- Se creó un fixture local para el contrato ML 0.1.
- Se implementó un adaptador ML 0.1 que valida y traduce a modelos internos.
- Se implementó un adaptador Dashboard 0.1 que serializa la respuesta interna.
- Se implementó almacenamiento de sesión exclusivamente en memoria.
- Se implementaron generadores deterministas por plantillas.
- Se implementó interpretación de objeciones y selección de estrategia mediante reglas.
- Se implementó el flujo de demo por CLI.
- Se añadieron pruebas con la biblioteca estándar `unittest`.

### Recorrido verificado

```text
fixture ML
-> adapter ML 0.1
-> modelo interno
-> sesión en memoria
-> speech inicial
-> “Me parece demasiado caro”
-> objeción precio
-> REFRAME_VALUE
-> respuesta grounded
-> JSON Dashboard 0.1
```

### Verificación

- Tests ejecutados: 3.
- Tests aprobados: 3.
- Tests fallidos: 0.
- Demo ejecutada correctamente.
- La recomendación `rec-demo-001` y la oferta `OF004` se conservaron sin modificación.
- La salida clasificó la objeción como `precio` con estrategia `REFRAME_VALUE`.

### Restricciones preservadas

No se incorporaron FastAPI, API ML real, LLM, dashboard, base de datos, Docker, audio, streaming, framework de agentes ni analítica.

### Siguiente paso

Detener implementación. Alinear contratos 0.1, catálogo y playbook con los otros integrantes antes de solicitar autorización para sustituir cualquier mock.

## 2026-08-12 — Núcleo conversacional interno

### Objetivo

Evolucionar el vertical slice determinista hacia un núcleo conversacional local, mantenible y testeable, sin integrar todavía ML, Dashboard o LLM reales.

### Inspección inicial

- Git estaba limpio en `master`, con dos commits locales y sin remotos configurados.
- Los adaptadores 0.1 estaban correctamente separados del dominio.
- El servicio asignaba estados directamente y solo representaba tres de los estados documentados.
- No existían Context Builder, fuente de conocimiento, playbook, política basada en estado, guardrails ni validador de respuestas.
- `grounded=true` se establecía sin comprobar los IDs de hechos.
- El nombre recibido desde ML se usaba sin contrastarlo con el catálogo.
- `README.md` aún afirmaba que no existía implementación y sus rutas de fuentes no reflejaban la carpeta `Fuentes/`.

### Trabajo realizado

- Se creó `AGENTS.md` con instrucciones persistentes de alcance, pruebas, documentación, seguridad y Git.
- Se amplió el dominio interno con estados, eventos, hechos comerciales, tácticas, claims, errores y transiciones.
- Se implementó una máquina de estados explícita con rechazo de transiciones inválidas.
- Se implementó `ContextBuilder` para unir la recomendación inmutable con catálogo reemplazable.
- Se implementó `CsvDemoCatalog` sobre el catálogo sintético del desafío.
- Se creó `fixtures/demo_playbook_v01.json`, marcado explícitamente como sintético, demo-only y no aprobado.
- Se implementó `JsonDemoPlaybook` detrás del puerto `SalesPlaybook`.
- Se separaron hechos del catálogo, tácticas del playbook y contenido generado.
- Se implementó una política conversacional que considera estado, objeción, táctica y hechos requeridos.
- Se reemplazaron los dos generadores anteriores por un único puerto `ContentGenerator`, punto de sustitución futuro para un LLM.
- Se implementó generación determinista grounded para apertura, precio, seguimiento, aclaración y abstención.
- Se implementaron guardrails de grounding, precios/promociones no autorizados y preservación de la recomendación original.
- Se añadieron abstención, escalamiento y errores estructurados.
- Se mantuvieron sin cambios los nombres de campos de los contratos 0.1.
- Se corrigió documentación objetivamente desactualizada sin registrar decisiones nuevas.

### Refactors y motivación

- `mocks.py` quedó limitado a dependencias externas simuladas: fuente ML y store en memoria.
- Interpretación y generación deterministas pasaron a `deterministic.py`, porque son implementaciones sustituibles del comportamiento de IA, no mocks de infraestructura.
- Catálogo y playbook pasaron a `knowledge.py` para preservar su autoridad y procedencia separadas.
- Estado, política, contexto y guardrails se implementaron como lógica interna concreta; no se añadieron puertos donde no existe una sustitución real prevista.
- `SalesCopilotService` quedó como orquestador y dejó de decidir contenido, conocimiento o reglas de transición por asignación directa.

### Verificación

- Compilación Python completada correctamente.
- Tests ejecutados: 12.
- Tests aprobados: 12.
- Tests fallidos: 0.
- La demo completa se ejecutó correctamente.
- La salida de apertura quedó grounded en `demo_catalog:OF004:name`.
- La objeción `precio` produjo `REFRAME_VALUE`, estado `rebate` y grounding de nombre y precio.
- Un descuento no autorizado fue bloqueado.
- Un intento de cambiar `OF004` fue bloqueado y la respuesta conservó la recomendación original.
- Una oferta sin catálogo y una objeción sin táctica produjeron abstención controlada.

### Restricciones preservadas

No se integraron ML real, Dashboard real, FastAPI, LLM, base externa, Redis, Docker, streaming, audio, RAG, vector database, multiagentes ni despliegue.

### Estado de Git

Los cambios permanecen locales y sin commit para revisión. No se configuró remoto ni se hizo push.

### Siguiente paso recomendado

Tras revisar y aprobar este diff, decidir proveedor y política de privacidad del LLM. Después podría implementarse un `ContentGenerator` LLM con pruebas de contrato y evaluación, conservando el generador determinista como baseline. No iniciar automáticamente.

## 2026-08-12 — Integración generativa opcional

### Objetivo

Incorporar un proveedor LLM real exclusivamente como reemplazo opcional de `ContentGenerator`, preservando las autoridades de ML, máquina de estados, selector de estrategia, catálogo/playbook y guardrails.

### Inspección inicial

- Git estaba limpio en `master`, sin remotos configurados.
- La suite base ejecutó 12 de 12 pruebas correctamente.
- El puerto `ContentGenerator` ya ofrecía el punto de sustitución necesario.
- Estado, estrategia, conocimiento y validación estaban separados de la generación, por lo que no fue necesario modificar contratos 0.1 ni el dominio de recomendación.
- La documentación aún indicaba que un LLM no estaba autorizado y requería actualización objetiva.
- El entorno no tenía SDK OpenAI ni `OPENAI_API_KEY` configurados.

### Trabajo realizado

- Se creó un puerto neutral para generación estructurada, con resultados, errores y métricas independientes del proveedor.
- Se implementó `OpenAIResponsesProvider` sobre Responses API y JSON Schema estricto, con `store=false` e import diferido del SDK.
- El modelo, la clave y el timeout quedaron fuera de la lógica de dominio y se leen desde variables de entorno.
- Se implementó `LlmContentGenerator` sin asignarle interpretación de objeciones, selección de estrategia, transiciones ni elección de oferta.
- Se creó un Context Builder específico del prompt que excluye perfil, probabilidades, alternativas y datasets completos.
- Se mantuvo `DeterministicContentGenerator` como baseline y fallback.
- El servicio intenta fallback tanto por fallo del proveedor/estructura como por bloqueo posterior de guardrails y vuelve a validar el resultado.
- Se reforzó el grounding para exigir correspondencia entre IDs, claims, valores autorizados y contenido generado.
- Se añadió metadata interna de generador, proveedor, modelo, latencia, tokens y degradación sin modificar Dashboard 0.1.
- Se creó una demo LLM opt-in y una prueba de integración real separada y deshabilitada por defecto.
- Se creó un arnés de evaluación común con cinco casos sintéticos y criterios automáticos más focos de revisión humana.
- Se añadió `.env.example` sin secretos y el SDK oficial como extra opcional `openai`.
- Se documentó la integración en `docs/LLM_INTEGRATION.md` y se actualizaron README, arquitectura y estado.

### Verificación

- Compilación Python completada correctamente.
- Tests descubiertos: 23.
- Tests aprobados: 22.
- Tests fallidos: 0.
- Test real opt-in omitido: 1.
- La demo determinista y su JSON Dashboard 0.1 continuaron funcionando.
- La evaluación determinista completó apertura, precio, mal momento, ambigüedad y abstención por conocimiento ausente, preservando estructura, grounding, oferta, recomendación y estrategia.
- Fakes verificaron salida LLM válida, contexto mínimo, métricas, indisponibilidad, estructura inválida, estrategia alterada y claim inventado.
- No se efectuó ninguna llamada de red ni consumo pagado.

### Restricciones preservadas

No se integraron FastAPI, ML real, Dashboard real, base externa, Redis, Docker, streaming, audio, RAG, base vectorial, multiagentes ni despliegue. El intérprete de objeciones continúa siendo determinista.

### Decisiones

No se añadieron decisiones a `DECISIONS.md`. El modelo concreto, la política de privacidad, el presupuesto y los criterios humanos de calidad permanecen pendientes.

### Estado de Git

Los cambios permanecen locales y sin commit. No se configuró remoto ni se hizo push.

### Siguiente paso recomendado

Tras revisión humana, aprobar modelo y política de datos; después ejecutar la evaluación opt-in con un proyecto OpenAI de prueba y revisar la calidad natural de forma ciega. No iniciar automáticamente una API ni integración con ML/Dashboard.

## 2026-08-12 — Handoff HTTP al integrante de Dashboard

### Objetivo

Convertir el núcleo local en un componente clonable, instalable y consumible por HTTP sin LLM ni API key, manteniendo intactas las autoridades y los adapters externos.

### Inspección inicial

- Git estaba limpio en `master` y no tenía remotos configurados.
- La suite base descubrió 23 pruebas: 22 aprobadas y una integración OpenAI opt-in omitida.
- El servicio y dominio ya estaban suficientemente separados para añadir transporte sin mover lógica de negocio.
- No existían API, composición configurable del proceso, schema HTTP ni guía operativa para Dashboard.
- Demo y tests dependían del catálogo dentro de `Fuentes/`.
- Todos los archivos de `Fuentes/`, incluidos PDFs y datasets completos, estaban trackeados; no son necesarios para ejecutar el componente ni adecuados para el handoff compartido.

### Trabajo realizado

- Se añadió una composición única que selecciona generación determinista por defecto u OpenAI por variable de entorno.
- Se creó una API FastAPI delgada con health check, creación de conversación y procesamiento de turnos.
- Se añadieron schemas Pydantic/OpenAPI y errores de transporte uniformes.
- Se implementó el adapter de entrada Dashboard 0.1 sin propagar nombres externos al dominio.
- Se habilitó CORS configurable para desarrollo local.
- Se añadió un comando instalable `ai-engine-api` y dependencias mínimas/extra de tests.
- Se creó un catálogo sintético mínimo en `fixtures/`; runtime, demo y tests dejaron de depender de `Fuentes/`.
- Se creó un fixture de turno Dashboard y pruebas HTTP de health, contratos, sesión, turno, errores, modo sin clave e invariantes.
- Se creó `docs/INTEGRATION_DASHBOARD.md` con comandos y JSON copiables, responsabilidades, límites, configuración y nota de costos/escalabilidad.
- Se actualizó README, arquitectura, contrato Dashboard, integración LLM, estado y `.env.example` conforme a la realidad implementada.
- Se añadió `Fuentes/` a `.gitignore` sin borrar ni retirar silenciosamente archivos ya trackeados.

### Verificación

- Se creó un entorno virtual nuevo y la instalación editable con extras de test completó correctamente.
- Tests descubiertos: 30.
- Tests aprobados: 29.
- Tests fallidos: 0.
- Integración OpenAI real opt-in omitida: 1.
- La demo determinista ejecutó apertura y objeción de precio correctamente.
- El servidor real respondió por HTTP a health, creación de `conv-rec-demo-001` y turno de precio.
- El smoke test devolvió `REFRAME_VALUE`, grounding en `OF004` y preservó `rec-demo-001` sin API key.
- `git diff --check` terminó sin errores.

### Auditoría de publicación

- No se encontraron secretos con patrones comunes en archivos trackeados.
- `.env`, `.venv`, caches, IDEs, builds y temporales están ignorados.
- `Fuentes/` sigue trackeado y debe retirarse con aprobación mediante `git rm --cached -r Fuentes` antes de publicar, preservando la copia local.
- No se hizo commit, push ni configuración de remoto.

### Decisiones

No se añadió ninguna decisión a `DECISIONS.md`. Los contratos 0.1, propiedad de IDs, persistencia, seguridad, proveedor/modelo y despliegue siguen pendientes de intervención humana.

### Siguiente paso recomendado

Realizar una integración conjunta corta con el desarrollador de Dashboard, cerrar feedback sobre IDs/enums/errores y retirar `Fuentes/` del tracking antes del primer push privado. No avanzar automáticamente a persistencia o despliegue.
