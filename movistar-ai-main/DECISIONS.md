# Registro de decisiones

## D-0001 — Limitar el proyecto al AI Engine / Sales Copilot

- **Estado:** Aceptada.
- **Fecha:** 2026-08-11.

### Motivación

El propietario de este proyecto es responsable exclusivamente de Ingeniería de IA / IA generativa, no de la solución completa de Next Best Offer.

### Decisión

El proyecto implementará únicamente la capa conversacional situada entre ML y dashboard.

### Consecuencias

- El alcance se centra en speech, conversación, objeciones, rebate, siguiente acción y salidas estructuradas.
- Cualquier diseño de ML o dashboard se trata únicamente como una dependencia de integración.

## D-0002 — Tratar ML y dashboard como componentes externos

- **Estado:** Aceptada.
- **Fecha:** 2026-08-11.

### Motivación

Otros integrantes desarrollarán los modelos predictivos y el dashboard.

### Decisión

La integración se realizará mediante contratos explícitos y versionados. El AI Engine no importará implementación interna de ML ni asumirá responsabilidades de UI.

### Consecuencias

- Los equipos pueden evolucionar independientemente.
- Los cambios incompatibles deben gestionarse mediante versiones del contrato.

## D-0003 — Excluir ML, NBO y dashboard de la implementación

- **Estado:** Aceptada.
- **Fecha:** 2026-08-11.

### Motivación

Evitar duplicación, conflictos de propiedad y expansión accidental del alcance.

### Decisión

No se implementarán feature engineering, entrenamiento, scoring, ranking, dashboard ni analítica completa dentro de este proyecto.

### Consecuencias

- Los resultados predictivos se reciben como datos externos.
- La salida del AI Engine será una respuesta estructurada para consumo del dashboard.

## D-0004 — Usar orquestación explícita para el MVP

- **Estado:** Aceptada.
- **Fecha:** 2026-08-11.

### Motivación

El flujo conversacional es acotado y debe ser comprensible, demostrable y auditable dentro de una hackathon.

### Decisión

El MVP utilizará una máquina de estados ligera y orquestación explícita. No se diseñará como sistema multiagente.

### Consecuencias

- Menor complejidad de integración y depuración.
- Las transiciones, acciones y restricciones serán visibles.
- Una arquitectura multiagente requeriría una decisión posterior que sustituya esta decisión.

## D-0005 — Exigir structured outputs

- **Estado:** Aceptada.
- **Fecha:** 2026-08-11.

### Motivación

El dashboard necesita renderizar acciones, speech, objeciones y alertas de forma estable.

### Decisión

Las respuestas del AI Engine deberán ajustarse a un esquema versionado. El texto libre será un campo dentro de la respuesta, no el contrato completo.

### Consecuencias

- Las respuestas podrán validarse antes de entregarlas.
- Los errores de esquema deberán producir respuestas controladas.

## D-0006 — Prohibir que el LLM cambie la recomendación ML

- **Estado:** Aceptada.
- **Fecha:** 2026-08-11.

### Motivación

La recomendación y las predicciones son responsabilidad del equipo de ML.

### Decisión

El AI Engine podrá explicar, comunicar y usar la recomendación, pero no reemplazarla ni alterar su ranking o probabilidad.

### Consecuencias

- Toda alternativa debe venir autorizada en el payload o en una fuente comercial explícita.
- Si la recomendación es inválida o insuficiente, el componente se abstendrá o devolverá un error; no improvisará otra.

## D-0007 — Limitar rebates a tácticas y hechos autorizados

- **Estado:** Aceptada.
- **Fecha:** 2026-08-11.

### Motivación

Un modelo generativo podría inventar descuentos, beneficios o condiciones contractuales.

### Decisión

Los rebates se generarán exclusivamente a partir de catálogo, políticas y playbook aprobados.

### Consecuencias

- Sin una táctica autorizada aplicable, el AI Engine preguntará, se abstendrá o escalará.
- Los hechos utilizados deberán poder identificarse mediante referencias de grounding.

## D-0008 — Limitar el MVP a conversación textual

- **Estado:** Aceptada.
- **Fecha:** 2026-08-11.

### Motivación

El audio en tiempo real introduce transcripción, streaming, latencia, privacidad e infraestructura fuera del núcleo demostrable de la hackathon.

### Decisión

El MVP recibirá texto escrito o transcripciones ya producidas por otro componente. No implementará reconocimiento de voz.

### Consecuencias

- La arquitectura conservará un punto de integración futuro para transcripciones.
- El soporte de audio requerirá una decisión y alcance posteriores.

## D-0009 — Usar conocimiento estructurado sin vector database en el MVP

- **Estado:** Aceptada.
- **Fecha:** 2026-08-11.

### Motivación

El catálogo y playbook iniciales son pequeños y pueden consultarse de manera determinista.

### Decisión

El MVP utilizará fuentes estructuradas y versionadas, como JSON, Markdown o CSV. No requiere una base vectorial.

### Consecuencias

- Se reduce complejidad y se mejora la trazabilidad del grounding.
- Una capa RAG o vectorial solo se evaluará si el corpus productivo crece y existe una necesidad comprobada.

