"""create cart items

Revision ID: 202604200002
Revises: 202604200001
Create Date: 2026-04-20

"""
from alembic import op
import sqlalchemy as sa


revision = "202604200002"
down_revision = "202604200001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "miniapp_cart_items",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("product_id", sa.BigInteger(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["miniapp_users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_miniapp_cart_items_deleted_at"), "miniapp_cart_items", ["deleted_at"])
    op.create_index(op.f("ix_miniapp_cart_items_product_id"), "miniapp_cart_items", ["product_id"])
    op.create_index(op.f("ix_miniapp_cart_items_user_id"), "miniapp_cart_items", ["user_id"])
    op.create_index(
        "uq_miniapp_cart_user_product_active",
        "miniapp_cart_items",
        ["user_id", "product_id"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )


def downgrade():
    op.drop_index("uq_miniapp_cart_user_product_active", table_name="miniapp_cart_items")
    op.drop_index(op.f("ix_miniapp_cart_items_user_id"), table_name="miniapp_cart_items")
    op.drop_index(op.f("ix_miniapp_cart_items_product_id"), table_name="miniapp_cart_items")
    op.drop_index(op.f("ix_miniapp_cart_items_deleted_at"), table_name="miniapp_cart_items")
    op.drop_table("miniapp_cart_items")
