"""add product type

Revision ID: 202604200006
Revises: 202604200005
Create Date: 2026-04-20

"""
from alembic import op
import sqlalchemy as sa


revision = "202604200006"
down_revision = "202604200005"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "admin_products",
        sa.Column("product_type", sa.String(length=20), nullable=False, server_default="other"),
    )
    op.create_index(op.f("ix_admin_products_product_type"), "admin_products", ["product_type"])
    op.alter_column("admin_products", "product_type", server_default=None)


def downgrade():
    op.drop_index(op.f("ix_admin_products_product_type"), table_name="admin_products")
    op.drop_column("admin_products", "product_type")
