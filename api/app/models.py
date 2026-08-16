"""Tablas reales y persistentes de la fase 1.

Solo se modela lo que produce el asesor durante la gestion: el ofrecimiento y
su calificacion. Clientes, ofertas y guiones viven en el JSON de demo porque en
produccion los sirve el modelo, no la base transaccional.
"""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base

CANALES = ("tienda", "call_in", "call_out", "digital")
RESULTADOS = ("en_curso", "vendido", "rechazado", "sin_contacto")
# Taxonomía del diccionario de datos del desafío.
MOTIVOS = (
    "precio",
    "no_necesita",
    "ya_tiene_similar",
    "mal_momento",
    "no_confia",
    "otro",
)
MEDIOS_PROBATORIOS = ("registro_plataforma", "audio_llamada", "chat_log")
CONTACTABILIDAD = ("contactado", "no_contactado")
SEGMENTOS = ("movil", "hogar", "ambos")


def _en(columna: str, valores: tuple[str, ...]) -> str:
    return f"{columna} IN ({', '.join(repr(v) for v in valores)})"


class Gestion(Base):
    __tablename__ = "gestiones"
    __table_args__ = (
        CheckConstraint(_en("canal", CANALES), name="ck_gestiones_canal"),
        CheckConstraint(_en("resultado", RESULTADOS), name="ck_gestiones_resultado"),
        CheckConstraint(
            f"motivo_real IS NULL OR {_en('motivo_real', MOTIVOS)}",
            name="ck_gestiones_motivo_real",
        ),
        CheckConstraint(
            "prob_inicial >= 0 AND prob_inicial <= 100", name="ck_gestiones_prob_inicial"
        ),
        CheckConstraint(
            "prob_final IS NULL OR (prob_final >= 0 AND prob_final <= 100)",
            name="ck_gestiones_prob_final",
        ),
        CheckConstraint(
            f"medio_probatorio IS NULL OR {_en('medio_probatorio', MEDIOS_PROBATORIOS)}",
            name="ck_gestiones_medio_probatorio",
        ),
        CheckConstraint(
            f"contactabilidad IS NULL OR {_en('contactabilidad', CONTACTABILIDAD)}",
            name="ck_gestiones_contactabilidad",
        ),
        CheckConstraint(_en("segmento_objetivo", SEGMENTOS), name="ck_gestiones_segmento"),
    )

    id_gestion: Mapped[str] = mapped_column(String, primary_key=True)
    id_cliente: Mapped[str] = mapped_column(String, nullable=False, index=True)
    oferta_id: Mapped[str | None] = mapped_column(String)
    oferta_recomendada: Mapped[str] = mapped_column(String, nullable=False)
    # Sin estas dos columnas no se puede medir el objetivo del reto.
    oferta_es_mt: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false", index=True
    )
    segmento_objetivo: Mapped[str] = mapped_column(
        String, nullable=False, default="ambos", server_default="ambos"
    )
    canal: Mapped[str] = mapped_column(String, nullable=False)
    id_asesor: Mapped[str] = mapped_column(String, nullable=False, index=True)

    inicio: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    fin: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    prob_inicial: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    prob_final: Mapped[float | None] = mapped_column(Numeric(5, 2))

    resultado: Mapped[str] = mapped_column(
        String, nullable=False, default="en_curso", index=True
    )
    motivo_real: Mapped[str | None] = mapped_column(String)
    contactabilidad: Mapped[str | None] = mapped_column(String)
    es_rebate: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    medio_probatorio: Mapped[str | None] = mapped_column(String)

    objeciones_detectadas: Mapped[list] = mapped_column(
        JSONB, nullable=False, default=list, server_default="[]"
    )

    calificaciones: Mapped[list["Calificacion"]] = relationship(
        back_populates="gestion", cascade="all, delete-orphan"
    )


class Calificacion(Base):
    __tablename__ = "calificaciones"
    __table_args__ = (
        CheckConstraint(
            "facilidad_venta >= 1 AND facilidad_venta <= 10", name="ck_calificaciones_facilidad"
        ),
        CheckConstraint(
            "nps_declarado IS NULL OR (nps_declarado >= 0 AND nps_declarado <= 10)",
            name="ck_calificaciones_nps",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_gestion: Mapped[str] = mapped_column(
        ForeignKey("gestiones.id_gestion", ondelete="CASCADE"), nullable=False, index=True
    )

    facilidad_venta: Mapped[int] = mapped_column(Integer, nullable=False)
    oferta_fue_pertinente: Mapped[bool] = mapped_column(Boolean, nullable=False)
    nps_declarado: Mapped[int | None] = mapped_column(Integer)
    comentario: Mapped[str | None] = mapped_column(String)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    gestion: Mapped[Gestion] = relationship(back_populates="calificaciones")
