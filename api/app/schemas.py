"""Contrato publico de la API.

Estos esquemas son la frontera con el frontend. En la fase 2 los endpoints de
demo dejaran de leer el JSON y pasaran a leer el modelo, pero la forma de estos
objetos no debe cambiar.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Canal = Literal["tienda", "call_in", "call_out", "digital"]

# El resultado que registra el asesor. Mapea al dataset del reto así:
#   vendido → aceptada · rechazado → rechazada · sin_contacto → pendiente
# `en_curso` no existe en el histórico porque allí solo hay ofrecimientos cerrados.
Resultado = Literal["en_curso", "vendido", "rechazado", "sin_contacto"]

# Taxonomías tomadas del diccionario de datos del desafío, no inventadas:
# son los valores que traerá historial_campanias.csv y el target del modelo.
Motivo = Literal[
    "precio",
    "no_necesita",
    "ya_tiene_similar",
    "mal_momento",
    "no_confia",
    "otro",
]
MedioProbatorio = Literal["registro_plataforma", "audio_llamada", "chat_log"]
Contactabilidad = Literal["contactado", "no_contactado"]
TipoOferta = Literal[
    "plan_movil",
    "plan_hogar",
    "upgrade",
    "equipo",
    "paquete_adicional",
    "movistar_total",
]
SegmentoObjetivo = Literal["movil", "hogar", "ambos"]
TipoCliente = Literal["prepago", "postpago"]
EdadRango = Literal["18-25", "26-35", "36-45", "46-55", "56-65", "65+"]

TipoSugerencia = Literal["info", "warn", "risk", "good"]
Confianza = Literal["alta", "media", "baja"]
Origen = Literal["historial", "lookalike"]


# --------------------------------------------------------------------------
# Demo: cliente, recomendaciones, guion
# --------------------------------------------------------------------------
class Cliente(BaseModel):
    """Ficha del cliente, con los nombres de `dataset_clientes.csv`.

    Sin historial (`es_nuevo`) los campos de comportamiento viajan en null,
    nunca en cero: un cero se leería como dato real y sería falso.
    """

    # --- Identidad -------------------------------------------------------
    # El dataset del reto es anónimo: no trae DNI, nombre ni teléfono. La PK
    # real es `cliente_id`; `dni` y `nombre` existen solo para la demo, porque
    # en una consola real el asesor identifica al cliente por documento.
    cliente_id: str
    dni: str | None = None
    nombre: str | None = None

    # --- Perfil y relación comercial ------------------------------------
    tipo_cliente: TipoCliente | None = None
    antiguedad_meses: int
    tiene_movil: bool
    tiene_hogar: bool
    tiene_internet_hogar: bool
    es_movistar_total: bool
    # Segmento prioritario del desafío: móvil + internet hogar + postpago,
    # y todavía sin MT.
    elegible_mt: bool
    plan_actual: str | None = None
    monto_facturado_prom: float | None = None
    edad_rango: EdadRango | None = None
    ubicacion_departamento: str
    es_usuario_app: bool = False

    # --- Comportamiento de los últimos 6 meses ---------------------------
    consumo_datos_gb_prom: float | None = None
    consumo_voz_min_prom: float | None = None
    dias_mora_prom: float | None = None
    meses_moroso: int | None = None
    n_reclamos: int | None = None
    n_actividad_canal: int | None = None
    canal_mas_usado: Canal | None = None

    # --- Derivados por el modelo, no vienen en el CSV --------------------
    es_nuevo: bool = False
    # consumo_datos_gb_prom / gb_incluidos del plan actual.
    pct_consumo_datos: int | None = None
    prob_churn: float | None = None
    riesgo_baja: str | None = None


class Angulo(BaseModel):
    titulo: str
    texto: str


class Rebate(BaseModel):
    objecion: Motivo
    cita: str
    texto: str


class Recomendacion(BaseModel):
    """Oferta puntuada, con los campos de `catalogo_ofertas_entrega.csv`."""

    # --- Catálogo --------------------------------------------------------
    oferta_id: str
    oferta: str
    tipo_oferta: TipoOferta
    segmento_objetivo: SegmentoObjetivo
    es_movistar_total: bool = False
    precio_mensual: float | None = None
    # Solo aplica a las variantes de Movistar Total.
    ahorro_pct: int | None = None
    gb_incluidos: int | None = None

    # --- Score del motor -------------------------------------------------
    probabilidad: int
    # Incertidumbre del score: 0 cuando hay historial suficiente.
    margen: int = 0
    confianza: Confianza = "alta"
    origen: Origen = "historial"
    # Motivo de rechazo más probable para esta oferta y este cliente.
    riesgo_principal: Motivo | None = None
    ahorro: float | None = None
    instalacion: float | None = None
    # Cómo convencerlo: el speech personalizado de esta oferta para este
    # cliente. En la fase 2 lo genera el modelo; el contrato no cambia.
    speech: str | None = None
    explicacion: list[str] = Field(default_factory=list)
    # Probabilidad de aceptación estimada para cada canal. `canal_sugerido` es
    # el máximo: el asesor puede mirar los otros, pero el mejor no se esconde.
    prob_por_canal: dict[Canal, int] = Field(default_factory=dict)
    canal_sugerido: Canal | None = None
    franja_sugerida: str | None = None
    angulos: list[Angulo] = Field(default_factory=list)
    rebates: list[Rebate] = Field(default_factory=list)
    # Por qué el motor NO recomendó esta oferta.
    descartada: str | None = None
    nota: str | None = None


class Sugerencia(BaseModel):
    tipo: TipoSugerencia
    titulo: str
    texto: str


class TurnoGuion(BaseModel):
    cliente: str
    asesor: str
    probabilidad: int
    # El margen se estrecha turno a turno cuando el cliente revela información.
    margen: int | None = None
    temperatura: int
    estado: str
    etiqueta: str
    objecion: Motivo | None = None
    paso_funnel: int | None = None
    datos_capturados: dict[str, float] | None = None
    sugerencia: Sugerencia | None = None


class CalificacionSugerida(BaseModel):
    facilidad_venta: int
    oferta_fue_pertinente: bool


class Desenlace(BaseModel):
    """Cierre esperado del caso de demo. Solo prellena el panel de cierre."""

    resultado: Resultado
    motivo_real: Motivo | None = None
    prob_final: int
    contactabilidad: Contactabilidad = "contactado"
    es_rebate: bool = False
    medio_probatorio: MedioProbatorio | None = None
    calificacion_sugerida: CalificacionSugerida | None = None


# --------------------------------------------------------------------------
# Gestiones
# --------------------------------------------------------------------------
class GestionCrear(BaseModel):
    id_cliente: str
    oferta_id: str
    oferta_recomendada: str
    # Guardar si la oferta presentada era MT y a qué segmento apunta es lo que
    # permite medir el objetivo del reto: % de venta hogar y móvil con MT.
    oferta_es_mt: bool = False
    segmento_objetivo: SegmentoObjetivo = "ambos"
    canal: Canal
    id_asesor: str = "ASE-001"
    prob_inicial: float = Field(ge=0, le=100)


class GestionObjecion(BaseModel):
    objecion: Motivo


class GestionCerrar(BaseModel):
    resultado: Literal["vendido", "rechazado", "sin_contacto"]
    motivo_real: Motivo | None = None
    prob_final: float | None = Field(default=None, ge=0, le=100)
    contactabilidad: Contactabilidad = "contactado"
    # Hubo contraoferta tras una objeción.
    es_rebate: bool = False
    medio_probatorio: MedioProbatorio | None = None


class GestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_gestion: str
    id_cliente: str
    oferta_id: str | None
    oferta_recomendada: str
    oferta_es_mt: bool
    segmento_objetivo: str
    canal: str
    id_asesor: str
    inicio: datetime
    fin: datetime | None
    prob_inicial: float
    prob_final: float | None
    resultado: str
    motivo_real: str | None
    contactabilidad: str | None
    es_rebate: bool
    medio_probatorio: str | None
    objeciones_detectadas: list[str]


class CalificacionCrear(BaseModel):
    facilidad_venta: int = Field(ge=1, le=10)
    oferta_fue_pertinente: bool
    nps_declarado: int | None = Field(default=None, ge=0, le=10)
    comentario: str | None = None


class CalificacionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    id_gestion: str
    facilidad_venta: int
    oferta_fue_pertinente: bool
    nps_declarado: int | None
    comentario: str | None
    creado_en: datetime


# --------------------------------------------------------------------------
# Metricas
# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
# Copiloto conversacional (AI Engine)
# --------------------------------------------------------------------------
class CopilotoIniciar(BaseModel):
    canal: Canal | None = None


class CopilotoTurno(BaseModel):
    conversation_id: str
    texto: str = Field(min_length=1, max_length=1000)


class GuiaCopiloto(BaseModel):
    """Contrato Dashboard 0.1 del AI Engine, traducido a los nombres de la consola.

    Los enums (`response_type`, `recommended_action`, `conversation_stage`) y los
    flags de seguridad se devuelven tal cual: son del motor, no de la consola.
    """

    conversation_id: str
    response_type: str
    conversation_stage: str
    recommended_action: str
    resumen: str | None = None
    que_decir: str
    pregunta_seguimiento: str | None = None
    oferta_alternativa: str | None = None
    objecion_categoria: str | None = None
    objecion_confianza: float | None = None
    grounded: bool = True
    requiere_revision: bool = False
    flags: list[str] = Field(default_factory=list)


class ParticipacionMT(BaseModel):
    """Objetivo declarado del reto: >50% de la venta hogar y >10% de la móvil
    hechas con Movistar Total."""

    ventas_totales: int
    ventas_con_mt: int
    pct_venta_hogar_con_mt: float
    meta_hogar: float = 50.0
    pct_venta_movil_con_mt: float
    meta_movil: float = 10.0


class MetricasResumen(BaseModel):
    total_gestiones: int
    por_resultado: dict[str, int]
    tasa_conversion: float
    tasa_contactabilidad: float
    participacion_mt: ParticipacionMT
    promedio_facilidad_venta: float | None
    pct_oferta_pertinente: float | None
    nps_promedio: float | None
    distribucion_motivos: dict[str, int]
    efectividad_rebate: float | None
    total_calificaciones: int
