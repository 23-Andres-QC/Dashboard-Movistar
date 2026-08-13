# Estado del proyecto

## Resumen

- **Proyecto:** AI Engine / Sales Copilot.
- **Última actualización:** 2026-08-12.
- **Fase:** handoff técnico al integrante de Dashboard.
- **Implementación:** núcleo conversacional, sesiones en memoria, API local FastAPI, baseline determinista predeterminado y `ContentGenerator` OpenAI opcional.
- **Estado general:** el flujo local puede instalarse y consumirse por HTTP sin API key; los contratos ML 0.1 y Dashboard 0.1 siguen siendo borradores aislados mediante adapters.
- **Git:** cambios locales sin commit para revisión; no hay remoto configurado.

## Objetivo vigente

Entregar al equipo de Dashboard un componente clonable que permita iniciar una conversación y enviar turnos por HTTP con instrucciones mínimas, preservando esta frontera:

```text
ML externo -> Adapter -> dominio interno estable -> AI Engine -> Adapter -> Dashboard externo
```

## Capacidades implementadas

- Adapter ML 0.1 hacia un dominio tipado e independiente.
- Context Builder y conservación estricta de `recommendation_id` y `offer_id`.
- Máquina de estados, interpretación determinista de objeciones y política de estrategia.
- Catálogo y playbook demo sintéticos detrás de límites reemplazables.
- Generación determinista grounded, guardrails, validación y abstención controlada.
- `ContentGenerator` LLM opcional, puerto neutral de proveedor y adapter OpenAI Responses.
- Contexto LLM mínimo, Structured Outputs, fallback determinista y evaluación offline.
- Adapter de turno Dashboard 0.1 y formatter de guidance Dashboard 0.1.
- Composición única del runtime con `AI_ENGINE_GENERATOR=deterministic` por defecto.
- API FastAPI sin lógica de negocio en endpoints: `GET /health`, `POST /v1/conversations` y `POST /v1/turns`.
- Schemas Pydantic, OpenAPI automático, CORS configurable para desarrollo local y errores HTTP estructurados.
- Fixtures sintéticos mínimos independientes de la carpeta local `Fuentes/`.
- Guía de integración en `docs/INTEGRATION_DASHBOARD.md`.

## Verificación actual

- Instalación limpia validada en un `.venv` nuevo con `python -m pip install -e ".[test]"`.
- **Suite:** 30 tests descubiertos, 29 aprobados, 0 fallidos y 1 integración OpenAI opt-in omitida.
- **Demo determinista:** recomendación `rec-demo-001` / `OF004` -> apertura grounded -> objeción `precio` -> `REFRAME_VALUE` -> JSON Dashboard 0.1.
- **Smoke HTTP:** health -> creación `conv-rec-demo-001` -> turno “Me parece demasiado caro” -> guidance grounded con IDs originales preservados.
- El flujo básico se ejecuta sin `OPENAI_API_KEY`, SDK de OpenAI ni llamada pagada.
- No se integraron ML real, Dashboard real, base externa, Redis, Docker, streaming, audio, RAG, multiagentes ni despliegue.

## Conocimiento utilizado

- `fixtures/demo_catalog_v01.csv` es un subconjunto sintético mínimo creado para demo y tests; no es catálogo oficial.
- `fixtures/demo_playbook_v01.json` es ficticio, `demo_only=true` y `approved=false`.
- Las respuestas exponen flags que identifican conocimiento demo/no aprobado.
- Una futura fuente comercial oficial puede sustituir ambos adapters sin cambiar el servicio central.

## Configuración vigente

- `AI_ENGINE_GENERATOR`: `deterministic` por defecto; `openai` es opt-in.
- `AI_ENGINE_HOST`: `127.0.0.1` por defecto.
- `AI_ENGINE_PORT`: `8000` por defecto.
- `AI_ENGINE_CORS_ORIGINS`: `*` por defecto únicamente para integración local.
- `OPENAI_API_KEY`, `OPENAI_MODEL` y `AI_ENGINE_LLM_TIMEOUT_SECONDS` solo aplican al modo OpenAI.
- `.env.example` no contiene secretos y el proyecto no carga `.env` automáticamente.

## Auditoría para repositorio compartido

- `.env`, entornos virtuales, caches, artefactos de build, IDEs y temporales están ignorados.
- `Fuentes/` quedó añadido a `.gitignore`, pero sus archivos ya están trackeados en el historial local actual. No se eliminaron ni se retiraron del tracking automáticamente.
- Antes de publicar el repositorio privado debe revisarse y ejecutar, con aprobación, `git rm --cached -r Fuentes` para preservar las copias locales y excluirlas del siguiente commit.
- Los PDFs, DOCX, datasets completos y material original dentro de `Fuentes/` no son necesarios para instalar, probar ni ejecutar la API.
- No se detectaron claves ni tokens en archivos de aplicación o fixtures; debe repetirse el escaneo antes del commit.

## Confirmaciones externas pendientes

### Equipo de ML

- Coreografía definitiva y responsable de invocar el inicio.
- Nombres, tipos, versionado y semántica final de IDs, probabilidades y reason codes.
- Vigencia, alternativas autorizadas y comportamiento sin recomendación.

### Equipo de Dashboard

- Propiedad, creación y expiración de `conversation_id`, `request_id` y `turn_id`.
- Retries, idempotencia, orden y concurrencia de turnos.
- Enums, longitudes de UI y campos visibles/internos.
- Forma final de errores, timeouts y CORS/origen de despliegue.
- Manejo visual de abstención, revisión humana y flags.

### Negocio, privacidad y proveedor

- Catálogo y playbook oficiales, tono y límites de insistencia.
- Política de privacidad, retención y datos conversacionales permitidos.
- Modelo/proveedor final, presupuesto, benchmark de calidad, latencia y costo.

## Riesgos y deuda técnica

- Los contratos 0.1 son referencias implementadas, no acuerdos cerrados.
- El store en memoria pierde sesiones al reiniciar y no debe ejecutarse con múltiples workers.
- La API local no tiene autenticación, rate limiting ni observabilidad productiva.
- CORS `*` es cómodo para hackathon, pero debe restringirse fuera de desarrollo local.
- El playbook demo cubre pocas objeciones y no constituye política comercial oficial.
- Los guardrails estructurales y léxicos no sustituyen evaluación semántica ni revisión humana del LLM.
- La dependencia FastAPI está acotada por rango, pero todavía no existe lockfile reproducible.
- La carpeta `Fuentes/` requiere retiro explícito del tracking antes del handoff por GitHub.

## Siguiente acción recomendada

Hacer una sesión corta de integración con el responsable de Dashboard usando `docs/INTEGRATION_DASHBOARD.md`, confirmar el payload real que su UI puede enviar y registrar feedback sobre IDs, enums y errores. Antes de publicar, retirar `Fuentes/` del tracking preservando la copia local. No avanzar automáticamente a persistencia o despliegue.
