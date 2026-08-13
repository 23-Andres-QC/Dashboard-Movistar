# Instrucciones persistentes para Codex

Antes de trabajar en este repositorio:

1. Lee `README.md` y `STATE.md`.
2. Consulta las decisiones relevantes de `DECISIONS.md`.
3. Lee los documentos especializados de `docs/` relacionados con la tarea.

Durante el trabajo:

- Respeta estrictamente la frontera `ML externo -> Adapter -> dominio interno estable -> AI Engine -> Adapter -> Dashboard externo`.
- No implementes modelos, feature engineering, ranking ni serving de ML.
- No implementes el Dashboard ni asumas decisiones propias de su interfaz.
- Mantén los contratos externos aislados en adaptadores; sus nombres provisionales no deben propagarse al dominio.
- Mantén catálogo, playbook, generación y persistencia detrás de límites reemplazables cuando exista una dependencia externa real.
- No presentes el catálogo sintético ni el playbook demo como información comercial oficial.
- No inventes precios, beneficios, descuentos, condiciones ni decisiones ausentes.
- Ejecuta toda la suite de pruebas después de cambios de código.
- Actualiza `STATE.md` y `LOGBOOK.md` al cerrar un hito.
- Registra en `DECISIONS.md` únicamente decisiones realmente aceptadas por la persona con autoridad.
- No incluyas secretos, claves API, credenciales ni datasets o fuentes confidenciales en Git.
- No introduzcas infraestructura productiva, servicios externos o dependencias operativas sin necesidad demostrada y autorización.
- No hagas push, configures remotos ni commits automáticos salvo instrucción explícita.

Al cerrar una sesión de código:

1. verifica pruebas y demo aplicables;
2. revisa el diff de Git;
3. documenta resultado, riesgos y siguiente acción;
4. confirma que no se amplió el alcance hacia ML o Dashboard.

