"""unique active doctor phone

Revision ID: 202604200008
Revises: 202604200007
Create Date: 2026-04-20

"""
from alembic import op
import sqlalchemy as sa


revision = "202604200008"
down_revision = "202604200007"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        "uq_admin_doctors_phone_active",
        "admin_doctors",
        ["phone"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )


def downgrade():
    op.drop_index("uq_admin_doctors_phone_active", table_name="admin_doctors")
