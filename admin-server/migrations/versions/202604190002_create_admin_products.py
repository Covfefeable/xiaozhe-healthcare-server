"""create admin products

Revision ID: 202604190002
Revises: 202604190001
Create Date: 2026-04-19

"""
from alembic import op
import sqlalchemy as sa


revision = "202604190002"
down_revision = "202604190001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "admin_products",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("price_cents", sa.Integer(), nullable=False),
        sa.Column("validity_days", sa.Integer(), nullable=False),
        sa.Column("detail_markdown", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_admin_products_deleted_at"),
        "admin_products",
        ["deleted_at"],
        unique=False,
    )
    op.create_index(op.f("ix_admin_products_name"), "admin_products", ["name"], unique=False)
    op.create_index(
        op.f("ix_admin_products_status"),
        "admin_products",
        ["status"],
        unique=False,
    )


def downgrade():
    op.drop_index(op.f("ix_admin_products_status"), table_name="admin_products")
    op.drop_index(op.f("ix_admin_products_name"), table_name="admin_products")
    op.drop_index(op.f("ix_admin_products_deleted_at"), table_name="admin_products")
    op.drop_table("admin_products")
