"""Alinea gestiones con el diccionario de datos del desafío

Cambia la taxonomía de motivo_real a la del reto, acota medio_probatorio a sus
tres valores, y añade las columnas que faltaban para medir el objetivo de
negocio (participación de Movistar Total) y la contactabilidad real.

Revision ID: 0002
Revises: 0001
Create Date: 2026-08-13

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

MOTIVOS_NUEVOS = ("precio", "no_necesita", "ya_tiene_similar", "mal_momento", "no_confia", "otro")
MOTIVOS_VIEJOS = (
    "precio",
    "permanencia",
    "no_entiende_beneficio",
    "ya_tiene_proveedor",
    "pide_tiempo",
    "sin_interes",
)
MEDIOS = ("registro_plataforma", "audio_llamada", "chat_log")
CONTACTABILIDAD = ("contactado", "no_contactado")
SEGMENTOS = ("movil", "hogar", "ambos")

# Equivalencias para no perder las filas ya registradas con la taxonomía vieja.
MAPEO = {
    "permanencia": "no_confia",
    "no_entiende_beneficio": "no_necesita",
    "ya_tiene_proveedor": "ya_tiene_similar",
    "pide_tiempo": "mal_momento",
    "sin_interes": "no_necesita",
}


def _en(columna: str, valores: Sequence[str]) -> str:
    lista = ", ".join(f"'{v}'" for v in valores)
    return f"{columna} IN ({lista})"


def upgrade() -> None:
    # --- Columnas nuevas -------------------------------------------------
    op.add_column("gestiones", sa.Column("oferta_id", sa.Text(), nullable=True))
    op.add_column(
        "gestiones",
        sa.Column("oferta_es_mt", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "gestiones",
        sa.Column("segmento_objetivo", sa.Text(), nullable=False, server_default="ambos"),
    )
    op.add_column("gestiones", sa.Column("contactabilidad", sa.Text(), nullable=True))
    op.add_column(
        "gestiones",
        sa.Column("es_rebate", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.create_index("ix_gestiones_oferta_es_mt", "gestiones", ["oferta_es_mt"])

    # --- Taxonomía de motivo_real ---------------------------------------
    op.drop_constraint("ck_gestiones_motivo_real", "gestiones", type_="check")
    for viejo, nuevo in MAPEO.items():
        op.execute(
            sa.text("UPDATE gestiones SET motivo_real = :nuevo WHERE motivo_real = :viejo").bindparams(
                nuevo=nuevo, viejo=viejo
            )
        )
    op.create_check_constraint(
        "ck_gestiones_motivo_real",
        "gestiones",
        f"motivo_real IS NULL OR {_en('motivo_real', MOTIVOS_NUEVOS)}",
    )

    # --- medio_probatorio pasa de texto libre a catálogo ------------------
    # Lo registrado antes era texto libre y no encaja en las tres categorías:
    # se descarta en vez de inventar una equivalencia falsa.
    op.execute(
        sa.text("UPDATE gestiones SET medio_probatorio = NULL WHERE medio_probatorio IS NOT NULL")
    )
    op.create_check_constraint(
        "ck_gestiones_medio_probatorio",
        "gestiones",
        f"medio_probatorio IS NULL OR {_en('medio_probatorio', MEDIOS)}",
    )
    op.create_check_constraint(
        "ck_gestiones_contactabilidad",
        "gestiones",
        f"contactabilidad IS NULL OR {_en('contactabilidad', CONTACTABILIDAD)}",
    )
    op.create_check_constraint(
        "ck_gestiones_segmento", "gestiones", _en("segmento_objetivo", SEGMENTOS)
    )


def downgrade() -> None:
    op.drop_constraint("ck_gestiones_segmento", "gestiones", type_="check")
    op.drop_constraint("ck_gestiones_contactabilidad", "gestiones", type_="check")
    op.drop_constraint("ck_gestiones_medio_probatorio", "gestiones", type_="check")

    op.drop_constraint("ck_gestiones_motivo_real", "gestiones", type_="check")
    inverso = {v: k for k, v in MAPEO.items()}
    for nuevo, viejo in inverso.items():
        op.execute(
            sa.text("UPDATE gestiones SET motivo_real = :viejo WHERE motivo_real = :nuevo").bindparams(
                viejo=viejo, nuevo=nuevo
            )
        )
    op.execute(sa.text("UPDATE gestiones SET motivo_real = NULL WHERE motivo_real = 'otro'"))
    op.create_check_constraint(
        "ck_gestiones_motivo_real",
        "gestiones",
        f"motivo_real IS NULL OR {_en('motivo_real', MOTIVOS_VIEJOS)}",
    )

    op.drop_index("ix_gestiones_oferta_es_mt", table_name="gestiones")
    op.drop_column("gestiones", "es_rebate")
    op.drop_column("gestiones", "contactabilidad")
    op.drop_column("gestiones", "segmento_objetivo")
    op.drop_column("gestiones", "oferta_es_mt")
    op.drop_column("gestiones", "oferta_id")
