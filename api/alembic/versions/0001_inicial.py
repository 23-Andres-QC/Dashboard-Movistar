"""Tablas gestiones y calificaciones

Revision ID: 0001
Revises:
Create Date: 2026-08-12

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

CANALES = ("tienda", "call_in", "call_out", "digital")
RESULTADOS = ("en_curso", "vendido", "rechazado", "sin_contacto")
MOTIVOS = (
    "precio",
    "permanencia",
    "no_entiende_beneficio",
    "ya_tiene_proveedor",
    "pide_tiempo",
    "sin_interes",
)


def _en(columna: str, valores: Sequence[str]) -> str:
    lista = ", ".join(f"'{v}'" for v in valores)
    return f"{columna} IN ({lista})"


def upgrade() -> None:
    op.create_table(
        "gestiones",
        sa.Column("id_gestion", sa.Text(), primary_key=True),
        sa.Column("id_cliente", sa.Text(), nullable=False),
        sa.Column("oferta_recomendada", sa.Text(), nullable=False),
        sa.Column("canal", sa.Text(), nullable=False),
        sa.Column("id_asesor", sa.Text(), nullable=False),
        sa.Column("inicio", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("fin", sa.DateTime(timezone=True), nullable=True),
        sa.Column("prob_inicial", sa.Numeric(5, 2), nullable=False),
        sa.Column("prob_final", sa.Numeric(5, 2), nullable=True),
        sa.Column("resultado", sa.Text(), nullable=False, server_default="en_curso"),
        sa.Column("motivo_real", sa.Text(), nullable=True),
        sa.Column("medio_probatorio", sa.Text(), nullable=True),
        sa.Column(
            "objeciones_detectadas",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.CheckConstraint(_en("canal", CANALES), name="ck_gestiones_canal"),
        sa.CheckConstraint(_en("resultado", RESULTADOS), name="ck_gestiones_resultado"),
        sa.CheckConstraint(
            f"motivo_real IS NULL OR {_en('motivo_real', MOTIVOS)}",
            name="ck_gestiones_motivo_real",
        ),
        sa.CheckConstraint(
            "prob_inicial >= 0 AND prob_inicial <= 100", name="ck_gestiones_prob_inicial"
        ),
        sa.CheckConstraint(
            "prob_final IS NULL OR (prob_final >= 0 AND prob_final <= 100)",
            name="ck_gestiones_prob_final",
        ),
    )
    op.create_index("ix_gestiones_id_cliente", "gestiones", ["id_cliente"])
    op.create_index("ix_gestiones_id_asesor", "gestiones", ["id_asesor"])
    op.create_index("ix_gestiones_resultado", "gestiones", ["resultado"])

    op.create_table(
        "calificaciones",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("id_gestion", sa.Text(), nullable=False),
        sa.Column("facilidad_venta", sa.Integer(), nullable=False),
        sa.Column("oferta_fue_pertinente", sa.Boolean(), nullable=False),
        sa.Column("nps_declarado", sa.Integer(), nullable=True),
        sa.Column("comentario", sa.Text(), nullable=True),
        sa.Column("creado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["id_gestion"],
            ["gestiones.id_gestion"],
            name="fk_calificaciones_gestion",
            ondelete="CASCADE",
        ),
        sa.CheckConstraint(
            "facilidad_venta >= 1 AND facilidad_venta <= 5", name="ck_calificaciones_facilidad"
        ),
        sa.CheckConstraint(
            "nps_declarado IS NULL OR (nps_declarado >= 0 AND nps_declarado <= 10)",
            name="ck_calificaciones_nps",
        ),
    )
    op.create_index("ix_calificaciones_id_gestion", "calificaciones", ["id_gestion"])


def downgrade() -> None:
    op.drop_index("ix_calificaciones_id_gestion", table_name="calificaciones")
    op.drop_table("calificaciones")
    op.drop_index("ix_gestiones_resultado", table_name="gestiones")
    op.drop_index("ix_gestiones_id_asesor", table_name="gestiones")
    op.drop_index("ix_gestiones_id_cliente", table_name="gestiones")
    op.drop_table("gestiones")
