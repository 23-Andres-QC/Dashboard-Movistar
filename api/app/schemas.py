"""Contrato publico de la API.

Estos esquemas son la frontera con el frontend. En la fase 2 los endpoints de
demo dejaran de leer el JSON y pasaran a leer el modelo, pero la forma de estos
objetos no debe cambiar.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Canal = Literal["tienda", "call_in", "call_out", "digital"]
Resultado = Literal["en_curso", "vendido", "rechazado", "sin_contacto"]
Motivo = Literal[
    "precio",
    "permanencia",
    "no_entiende_beneficio",
    "ya_tiene_proveedor",
    "pide_tiempo",
    "sin_interes",
]
TipoSugerencia = Literal["info", "warn", "risk", "good"]
Confianza = Literal["alta", "media", "baja"]
Origen = Literal["historial", "lookalike"]


# --------------------------------------------------------------------------
# Demo: cliente, recomendaciones, guion
# --------------------------------------------------------------------------
class Cliente(BaseModel):
    """Ficha del cliente.

    En clientes nuevos (`es_nuevo`) no hay historial: `arpu`, `prob_churn`,
    `pct_consumo_datos` y `riesgo_baja` viajan en null, nunca en cero. Un cero
    se leería como un dato real y sería falso.
    """

    dni: str
    id_cliente: str
    es_nuevo: bool = False
    nombre: str
    distrito: str
    antiguedad_meses: int
    arpu: float | None = None
    productos: str
    riesgo_baja: str | None = None
    prob_churn: float | None = None
    pct_consumo_datos: int | None = None
    lineas_domicilio: int
    cobertura_fibra: bool


class Angulo(BaseModel):
    titulo: str
    texto: str


class Rebate(BaseModel):
    objecion: Motivo
    cita: str
    texto: str


class Recomendacion(BaseModel):
    oferta: str
    probabilidad: int
    # Incertidumbre del score: 0 cuando hay historial suficiente.
    margen: int = 0
    confianza: Confianza = "alta"
    origen: Origen = "historial"
    ahorro: float | None = None
    instalacion: float | None = None
    explicacion: list[str] = Field(default_factory=list)
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
    calificacion_sugerida: CalificacionSugerida | None = None


# --------------------------------------------------------------------------
# Gestiones
# --------------------------------------------------------------------------
class GestionCrear(BaseModel):
    id_cliente: str
    oferta_recomendada: str
    canal: Canal
    id_asesor: str = "ASE-001"
    prob_inicial: float = Field(ge=0, le=100)


class GestionObjecion(BaseModel):
    objecion: Motivo


class GestionCerrar(BaseModel):
    resultado: Literal["vendido", "rechazado", "sin_contacto"]
    motivo_real: Motivo | None = None
    prob_final: float | None = Field(default=None, ge=0, le=100)
    medio_probatorio: str | None = None


class GestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id_gestion: str
    id_cliente: str
    oferta_recomendada: str
    canal: str
    id_asesor: str
    inicio: datetime
    fin: datetime | None
    prob_inicial: float
    prob_final: float | None
    resultado: str
    motivo_real: str | None
    medio_probatorio: str | None
    objeciones_detectadas: list[str]


class CalificacionCrear(BaseModel):
    facilidad_venta: int = Field(ge=1, le=5)
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
class MetricasResumen(BaseModel):
    total_gestiones: int
    por_resultado: dict[str, int]
    tasa_conversion: float
    promedio_facilidad_venta: float | None
    pct_oferta_pertinente: float | None
    nps_promedio: float | None
    distribucion_motivos: dict[str, int]
    total_calificaciones: int
