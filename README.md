# NBO Movistar · Consola del asesor (fase 1)

Motor de **Next Best Offer** para el reto *AI Telecom Challenge* (Movistar × Universidad de Lima).
Esta fase entrega el **dashboard del asesor** funcionando de punta a punta, con el mínimo
backend que lo sostiene y persistencia real en PostgreSQL.

El usuario es un asesor comercial con **menos de un minuto por llamada**: la pantalla está
diseñada para densidad y lectura rápida.

---

## Arranque

```bash
cp .env.example .env
docker compose up --build
```

Eso deja los tres servicios listos, sin pasos manuales. Las migraciones de Alembic se aplican
solas al arrancar la API.

| Servicio | URL | Qué es |
|---|---|---|
| **Dashboard** | <http://localhost:5173> | La consola del asesor |
| API + documentación | <http://localhost:8000/docs> | OpenAPI interactivo |
| PostgreSQL | `localhost:5432` | usuario `nbo`, base `nbo` |

Entrada directa a un caso: <http://localhost:5173/asesor/45789123>

---

## Los cuatro casos de demo

Se buscan por DNI en el rail superior. Cubren la matriz **tipo de cliente × desenlace**, para
que la demo no sugiera que el motor siempre recomienda Movistar Total ni que un cliente nuevo
siempre termina en rechazo.

| DNI | Perfil | Oferta que gana | Desenlace | Probabilidad por turno |
|---|---|---|---|---|
| `45789123` | Antiguo, 6 años, alto consumo | Movistar Total | Vendido | 78 → 74 → 61 → 69 → 89 |
| `70112384` | Nuevo, sin historial | Plan móvil de entrada | Rechazado | 42 → 38 → 24 |
| `08954412` | Antiguo, riesgo de baja alto | Retención, **no** MT | Vendido tras rebate | 66 → 54 → 79 → 91 |
| `76340219` | Nuevo, portabilidad digital | Plan 45 GB + equipo | Vendido | 48 → 59 → 71 → 86 |

La última columna **no se grafica en pantalla**: el valor del último turno se guarda como
`prob_final` al cerrar la gestión y alimenta las métricas.

En los casos 2 y 3, Movistar Total aparece **tachada** en la lista de alternativas con el motivo
del descarte. Poder explicar por qué el motor *no* recomendó algo vale tanto como explicar por
qué sí.

### Cómo recorrer la demo

1. Busque un DNI. Se carga la ficha y el argumentario; el funnel marca *Clasificado*.
2. **Iniciar gestión** abre la fila en PostgreSQL y arranca el cronómetro.
3. **Siguiente turno** recorre el guion. Cada turno mueve el termómetro, las sugerencias, el
   rebate resaltado y el funnel; si hay objeción, la envía por `PATCH`.
4. Elija resultado, motivo y medio probatorio, y pulse **Cerrar gestión**.
5. El modal pide la calificación. *Omitir* también registra el cierre: no se pierde el resultado.

### Incertidumbre en clientes nuevos

Cuando el cliente no tiene historial (`es_nuevo`), el score no es una medición sino un estimado
sobre clientes similares, y la pantalla lo dice:

- Los campos sin dato muestran **`—`**, nunca `0` ni `0%`: un cero se leería como dato real.
- Etiqueta **Sin historial** junto al nombre y sello **Confianza baja** en la oferta.
- La probabilidad viaja con su margen (`42% ±12`) y el medidor de la tarjeta añade un **tramo
  claro** que muestra hasta dónde podría llegar el estimado.
- En el caso `76340219`, cada dato que el cliente revela llena un campo de la ficha —con un
  realce breve— y **estrecha el margen**: de ±14 a ±3 a lo largo de la llamada.

---

## Qué es real y qué está simulado

Esta distinción es deliberada: los endpoints ya tienen su **forma definitiva**, así que la fase 2
solo cambia la implementación interna. El frontend no se toca.

### Simulado (JSON estático, `api/app/data/demo.json`)

Todo lo que en producción vendría de un modelo:

- Fichas de cliente, probabilidades y su margen de incertidumbre.
- Ranking de ofertas, ángulos de convencimiento, rebates y explicaciones.
- Guion de conversación, objeciones detectadas y sugerencias.

**No hay** modelos de ML, entrenamiento, SHAP, detección de objeciones por texto ni
reconocimiento de voz. Eso es fase 2.

### Real (PostgreSQL, con migraciones)

Lo que produce el asesor durante la gestión, que es lo que permitirá medir la calidad del
servicio y realimentar el modelo:

- **`gestiones`** — el ofrecimiento: canal, asesor, probabilidad inicial y final, resultado,
  motivo real, medio probatorio y las objeciones marcadas (`JSONB`).
- **`calificaciones`** — la calidad del servicio: facilidad de venta (1–5), si la oferta fue
  pertinente, NPS declarado y comentario.

No existen tablas de clientes ni de ofertas: eso vive en el JSON.

Verificación directa:

```bash
docker compose exec db psql -U nbo -d nbo \
  -c "SELECT id_gestion, resultado, motivo_real, objeciones_detectadas FROM gestiones;" \
  -c "SELECT id_gestion, facilidad_venta, oferta_fue_pertinente FROM calificaciones;"

curl -s localhost:8000/api/metricas/resumen | python3 -m json.tool
```

`/api/metricas/resumen` se calcula con SQL sobre lo realmente guardado. Sin gestiones devuelve
ceros, no un error. La `tasa_conversion` es `vendido / gestiones cerradas` (las `en_curso` no
entran en el denominador).

---

## Endpoints

Servidos desde el JSON de demo — en la fase 2 los alimentará el modelo, con el mismo contrato:

```
GET  /api/clientes/buscar?dni=                  ficha del cliente o 404
GET  /api/clientes/{id_cliente}/recomendaciones ofertas ordenadas, con ángulos y rebates
GET  /api/clientes/{id_cliente}/guion           turnos de la conversación
GET  /api/clientes/{id_cliente}/desenlace       cierre esperado del caso (solo demo)
```

Persistidos en PostgreSQL:

```
POST  /api/gestiones                     abre gestión, devuelve id_gestion (GES-77412)
PATCH /api/gestiones/{id}/objecion       marca una objeción detectada
POST  /api/gestiones/{id}/cerrar         resultado, motivo_real, prob_final, medio probatorio
POST  /api/gestiones/{id}/calificacion   facilidad_venta, pertinencia, NPS, comentario
GET   /api/gestiones/{id}                consulta una gestión
GET   /api/metricas/resumen              conteos, conversión, promedios, motivos
GET   /health
```

`/api/clientes/{id}/desenlace` es andamiaje de demo: solo prellena el panel de cierre para que
el asesor no teclee durante la presentación. Desaparece en la fase 2 sin afectar al resto.

---

## Estructura

```
.
├── docker-compose.yml        db · api · web
├── .env.example
├── api/
│   ├── alembic/versions/     migración inicial con CHECK constraints
│   ├── entrypoint.sh         aplica migraciones y arranca Uvicorn
│   └── app/
│       ├── models.py         solo gestiones y calificaciones
│       ├── schemas.py        el contrato con el frontend
│       ├── demo_data.py      carga el JSON; en fase 2 se cambia solo esto
│       ├── data/demo.json    los cuatro casos
│       └── routers/          demo · gestiones · metricas
└── web/src/
    ├── stores/gestion.ts     toda la lógica de la llamada
    ├── api/                  client.ts · tipos.ts · etiquetas.ts
    ├── styles/tokens.css     identidad visual
    ├── views/ConsolaAsesor.vue
    └── components/
        ├── rail/             marca, buscador, cronómetro, estado de llamada
        ├── ficha/            franja de datos del cliente
        ├── argumentario/     oferta, alternativas, ángulos, rebates
        ├── conversacion/     burbujas, termómetro, sugerencias
        ├── seguimiento/      funnel, cierre, por qué esta oferta
        ├── calificacion/     modal
        └── ui/               piezas compartidas
```

El frontend está deliberadamente troceado: **un componente por pieza**, con la lógica
concentrada en el store, para poder mover bloques de la pantalla sin reescribir nada.

---

## Detalles de implementación

- **No hay gráfico de probabilidad, y es a propósito.** La probabilidad no es una señal
  continua que se pueda «ver en vivo»: es una tasa que el modelo emite para una oferta. Se
  muestra una sola vez, donde el asesor la necesita —en la tarjeta de oferta—, como un
  **medidor sobre escala fija 0–100** que se llena. Graficar su recorrido durante la llamada
  ocupaba el ancho completo de la pantalla para decir algo que el asesor no puede accionar.
- **Qué es «en vivo».** Lo que cambia turno a turno es la **guía**: la oferta, los rebates y
  las sugerencias. Por eso la insignia *En vivo* está sobre «Qué decirle ahora», «Rebates por
  objeción» y «Sugerencias clave», y el rail dice *En llamada*.
- **La columna izquierda manda.** Es lo que el asesor lee mientras habla, así que es la más
  ancha (384 px) y la de mayor contraste tipográfico: nombre de la oferta a 21 px, la tasa a
  40 px, ángulos numerados y rebates a cuerpo pleno. El resto de la pantalla la acompaña.
- **El margen se ve en el propio medidor**: un tramo claro a continuación del relleno muestra
  hasta dónde podría llegar el estimado cuando la confianza es baja.
- **El funnel solo avanza**: nunca retrocede al recalcularse.
- **Integridad en la base**: `CHECK` sobre canal, resultado, motivo, rangos de probabilidad,
  facilidad 1–5 y NPS 0–10. Las reglas no dependen solo de la capa de aplicación.
- **Accesibilidad**: foco de teclado visible, `role`/`aria` en medidores y modal,
  `prefers-reduced-motion` respetado.
- **Tipografía**: `Telefónica Sans` → `Inter` para cuerpo, `Barlow Semi Condensed` para
  micro-etiquetas y `JetBrains Mono` para cifras. No se descargan desde CDN: si no están
  instaladas en el sistema, caen a los respaldos declarados en `tokens.css`.
- **Logotipo**: el símbolo oficial vive en `web/src/assets/logo-movistar.png`, extraído del
  archivo entregado y limpiado (fondo transparente real, color plano `#0066FF`). El nombre
  «movistar» del rail va como **texto**, no como reproducción del lettering. El favicon
  (`web/public/favicon.png`) se genera del mismo símbolo. El azul de marca vive en su propio
  token, `--marca-azul`, separado del azul de interfaz `--movistar-azul` que fija la paleta.

---

## Desarrollo fuera de Docker

```bash
# API
cd api && pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg://nbo:nbo@localhost:5432/nbo
alembic upgrade head && uvicorn app.main:app --reload

# Web (proxya /api a localhost:8000 por defecto)
cd web && npm install && npm run dev
```

El servicio `web` monta `./web` como volumen, así que dentro de Docker los cambios en el código
se recargan sin reconstruir la imagen.
