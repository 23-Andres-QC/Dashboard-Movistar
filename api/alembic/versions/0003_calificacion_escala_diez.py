"""Amplía facilidad de uso a escala 1–10.

Revision ID: 0003_calificacion_escala_diez
Revises: 0002_diccionario_datos
"""

from alembic import op


revision = "0003_calificacion_escala_diez"
down_revision = "0002_diccionario_datos"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("ck_calificaciones_facilidad", "calificaciones", type_="check")
    op.create_check_constraint(
        "ck_calificaciones_facilidad",
        "calificaciones",
        "facilidad_venta >= 1 AND facilidad_venta <= 10",
    )


def downgrade() -> None:
    op.drop_constraint("ck_calificaciones_facilidad", "calificaciones", type_="check")
    op.create_check_constraint(
        "ck_calificaciones_facilidad",
        "calificaciones",
        "facilidad_venta >= 1 AND facilidad_venta <= 5",
    )
