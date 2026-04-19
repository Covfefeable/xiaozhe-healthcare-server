"""add product summary

Revision ID: 202604200001
Revises: 202604190003
Create Date: 2026-04-20

"""
from alembic import op
import sqlalchemy as sa


revision = "202604200001"
down_revision = "202604190003"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "admin_products",
        sa.Column("summary", sa.String(length=20), nullable=False, server_default=""),
    )
    op.alter_column("admin_products", "summary", server_default=None)


def downgrade():
    op.drop_column("admin_products", "summary")
