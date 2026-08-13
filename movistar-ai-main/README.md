# AI Engine / Sales Copilot

## Identidad

Este proyecto desarrolla exclusivamente el componente de Ingeniería de IA generativa del desafío **Personalización comercial inteligente** del Hackathon AI Telecom Challenge 2026.

El componente ocupa la frontera entre los resultados predictivos producidos por el equipo de Machine Learning y la interfaz construida por el equipo de dashboard:

```text
ML -> AI Engine / Sales Copilot -> Dashboard
```

El AI Engine recibe una recomendación comercial ya calculada y la transforma en asistencia conversacional, contextual, segura y estructurada para un asesor.

## Quick Start

El modo predeterminado es determinista: no requiere API key, SDK de OpenAI ni conexión a un LLM.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\ai-engine-api.exe
```

Con el servidor activo:

```powershell
curl.exe http://127.0.0.1:8000/health
curl.exe -X POST http://127.0.0.1:8000/v1/conversations -H "Content-Type: application/json" --data-binary "@fixtures/ml_recommendation_v01.json"
curl.exe -X POST http://127.0.0.1:8000/v1/turns -H "Content-Type: application/json" --data-binary "@fixtures/dashboard_turn_v01.json"
```

La documentación interactiva está en `http://127.0.0.1:8000/docs`. El contrato HTTP, ejemplos y responsabilidades para el equipo de Dashboard están en [docs/INTEGRATION_DASHBOARD.md](docs/INTEGRATION_DASHBOARD.md).

## Propósito

Ayudar al asesor a conducir una interacción comercial mediante:

- un speech inicial personalizado;
- asistencia conversacional durante la interacción;
- interpretación estructurada de objeciones;
- generación de rebates autorizados;
- sugerencia de la siguiente acción conversacional;
- respuestas estructuradas y trazables para el dashboard.

El componente no decide qué oferta es la mejor. Consume y respeta las recomendaciones y predicciones entregadas por ML.

## Alcance

El proyecto incluye:

- validación y adaptación del contrato recibido desde ML;
- construcción del contexto mínimo necesario para cada turno;
- gestión del estado conversacional;
- interpretación de intención y objeciones;
- selección de una estrategia conversacional permitida;
- generación grounded de speech, preguntas, rebate y cierre;
- aplicación de guardrails comerciales y de seguridad;
- generación de respuestas JSON estructuradas para el dashboard;
- trazabilidad técnica del componente de IA;
- evaluación técnica propia del AI Engine.

## Fuera de alcance

Este proyecto no incluye:

- feature engineering;
- entrenamiento, calibración o evaluación de modelos de Machine Learning;
- recomendación o ranking de Next Best Offer;
- predicción de aceptación, canal, churn, momento u otras variables;
- definición de elegibilidad comercial;
- desarrollo del dashboard;
- analítica completa del funnel;
- ejecución o confirmación de ventas;
- desarrollo de reconocimiento de voz;
- modificación silenciosa de una recomendación recibida desde ML;
- invención de precios, promociones, beneficios o descuentos.

## Usuarios y actores

- **Asesor comercial:** usuario principal del Sales Copilot a través del dashboard.
- **Cliente:** participa en la conversación, pero no interactúa necesariamente de forma directa con este componente.
- **Equipo de ML:** produce recomendaciones y predicciones consumidas por el AI Engine.
- **Equipo de dashboard:** presenta las sugerencias al asesor y remite las intervenciones de la conversación.
- **Equipo comercial o de producto:** debe aprobar catálogo, beneficios, restricciones, rebates y tácticas permitidas.

## Dependencias externas

El AI Engine depende de:

1. un contrato estable de salida del componente ML;
2. un contrato estable de entrada y salida con el dashboard;
3. un catálogo de ofertas y beneficios autorizados;
4. un playbook comercial de objeciones y rebates;
5. una política de privacidad, retención y trazabilidad;
6. OpenAI como primer proveedor LLM opcional, aislado detrás de un puerto neutral y sujeto a configuración, privacidad y credenciales autorizadas.

## Principios de diseño

- **Contract-first:** ML, AI Engine y dashboard se integran mediante esquemas versionados.
- **Grounding obligatorio:** toda afirmación comercial debe estar respaldada por hechos autorizados.
- **Separación de responsabilidades:** el LLM no reemplaza los modelos de ML ni la decisión comercial.
- **Structured outputs:** el dashboard recibe datos estructurados, no únicamente texto libre.
- **Abstención segura:** ante falta de contexto o una solicitud no autorizada, el componente pregunta, se abstiene o escala.
- **Contexto mínimo:** solo se procesa la información necesaria para el turno.
- **Trazabilidad sin razonamiento privado:** se registran versiones, fuentes y flags, no cadenas internas de razonamiento.
- **Prototipo proporcional:** el MVP evita infraestructura y orquestación innecesarias para una hackathon.

## Arquitectura aprobada

La arquitectura conceptual y la separación entre MVP y evolución productiva se encuentran en [docs/ARCHITECTURE_AI_ENGINE.md](docs/ARCHITECTURE_AI_ENGINE.md).

Contratos conceptuales:

- [ML -> AI Engine](docs/CONTRACT_ML_TO_AI.md)
- [AI Engine <-> Dashboard](docs/CONTRACT_AI_TO_DASHBOARD.md)

Flujo conversacional:

- [Estados de conversación](docs/CONVERSATION_STATES.md)

## Fuentes locales del desafío

La carpeta `Fuentes/` es material local de referencia, no una dependencia del AI Engine y no debe incluirse en el repositorio compartido. La API, demo y tests usan únicamente fixtures sintéticos mínimos versionables.

- `Fuentes/02. Desafío personalización comercial inteligente_VF.pdf`: fuente principal del desafío.
- `Fuentes/Desafíos Hackathon AI Telecom 2026 (V.FINAL).pdf`: presentación general.
- `Fuentes/diccionario_datos_participantes.docx`: diccionario de los datos suministrados.
- `Fuentes/dataset_clientes.csv`: perfiles sintéticos de clientes.
- `Fuentes/catalogo_ofertas_entrega.csv`: catálogo ficticio de ofertas.
- `Fuentes/historial_campanias.csv`: historial sintético de ofrecimientos.
- `Fuentes/Informe_Organizacion_Entorno_IA_y_Nube.md`: protocolo usado para adoptar documentalmente el proyecto.

Los datasets sirven como contexto del desafío. Su modelado predictivo pertenece al equipo de ML y queda fuera de este proyecto.

## Núcleo documental

- `README.md`: identidad, alcance y orientación estable.
- `STATE.md`: realidad vigente, dependencias y siguiente acción.
- `LOGBOOK.md`: historial de sesiones e hitos.
- `DECISIONS.md`: decisiones aceptadas y sus consecuencias.

## Estado actual

Existe un núcleo conversacional local con una API FastAPI delgada para integración, baseline determinista y un `ContentGenerator` LLM opcional sobre OpenAI Responses API con Structured Outputs. ML y Dashboard reales continúan fuera del repositorio y aislados mediante adapters. La ruta LLM construye contexto mínimo, valida su salida con los mismos guardrails y degrada al generador determinista ante indisponibilidad, estructura inválida o fallo de grounding. Consultar [STATE.md](STATE.md) antes de iniciar cualquier trabajo.

La estructura interna principal es:

```text
contract_ml_v01.py
  -> domain.py
  -> context.py + knowledge.py
  -> state_machine.py + strategy.py
  -> deterministic.py o llm.py
       -> generation.py (puerto neutral)
       -> openai_responses.py (adapter opcional)
  -> guardrails.py
  -> service.py
  -> contract_dashboard_v01.py
  -> api.py (transporte HTTP)
```

El proveedor no recibe datasets completos, alternativas, probabilidades ni el perfil completo. Recibe la oferta activa, únicamente los hechos requeridos, estado, objeción, estrategia ya seleccionada, táctica aplicable, restricciones y hasta cuatro turnos recientes. La implementación y operación se detallan en [docs/LLM_INTEGRATION.md](docs/LLM_INTEGRATION.md).

## Desarrollo y LLM opcional

La suite completa requiere el extra de tests, pero ni los tests normales ni la demo determinista necesitan clave ni llamadas de red:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" -v
.\.venv\Scripts\python.exe -m ai_engine.demo
.\.venv\Scripts\python.exe -m ai_engine.evaluation --generator deterministic
```

La integración real es opt-in. El SDK oficial se mantiene como dependencia opcional para no convertir la ruta determinista ni las pruebas offline en consumidoras del proveedor:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[openai]"
$env:AI_ENGINE_GENERATOR="openai"
$env:OPENAI_API_KEY="<configurar-fuera-de-Git>"
$env:OPENAI_MODEL="<modelo-compatible-con-structured-outputs>"
.\.venv\Scripts\ai-engine-api.exe
```

`.env.example` enumera las variables sin incluir secretos. El proyecto no carga archivos `.env` automáticamente.

## Criterio de éxito del prototipo

El prototipo se considerará exitoso cuando, usando un payload de recomendación acordado con ML y una conversación textual, pueda:

1. producir un speech inicial grounded;
2. interpretar una objeción dentro de la taxonomía acordada;
3. generar una respuesta o rebate permitido;
4. recomendar una siguiente acción;
5. devolver una respuesta estructurada consumible por el dashboard;
6. abstenerse o escalar cuando falte información o se solicite una acción no autorizada.

El núcleo local cubre actualmente este criterio con conocimiento sintético, generación determinista y una ruta LLM opcional. Esto no implica que el catálogo o playbook sean oficiales ni que cualquier dato pueda enviarse al proveedor sin aprobación de privacidad.

## Protocolo de trabajo

Al comenzar una sesión:

1. leer `README.md` y `STATE.md`;
2. consultar las decisiones aplicables en `DECISIONS.md`;
3. revisar el contrato o documento especializado relacionado con la tarea.

Al terminar:

1. registrar decisiones aceptadas;
2. actualizar `STATE.md` con la realidad y siguiente acción;
3. registrar el hito en `LOGBOOK.md`;
4. comprobar que no se ha ampliado el alcance hacia ML o dashboard.
