"""create orders

Revision ID: 202604200004
Revises: 202604200003
Create Date: 2026-04-20

"""
from alembic import op
import sqlalchemy as sa


revision = "202604200004"
down_revision = "202604200003"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "miniapp_orders",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("order_no", sa.String(length=32), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("product_type", sa.String(length=20), nullable=False),
        sa.Column("total_amount_cents", sa.Integer(), nullable=False),
        sa.Column("paid_amount_cents", sa.Integer(), nullable=False),
        sa.Column("payment_method", sa.String(length=30), nullable=False),
        sa.Column("service_user_name", sa.String(length=50), nullable=False),
        sa.Column("paid_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("refunded_at", sa.DateTime(), nullable=True),
        sa.Column("remark", sa.String(length=255), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["miniapp_users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("order_no"),
    )
    op.create_index(op.f("ix_miniapp_orders_deleted_at"), "miniapp_orders", ["deleted_at"])
    op.create_index(op.f("ix_miniapp_orders_order_no"), "miniapp_orders", ["order_no"])
    op.create_index(op.f("ix_miniapp_orders_product_type"), "miniapp_orders", ["product_type"])
    op.create_index(op.f("ix_miniapp_orders_status"), "miniapp_orders", ["status"])
    op.create_index(op.f("ix_miniapp_orders_user_id"), "miniapp_orders", ["user_id"])

    op.create_table(
        "miniapp_order_items",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("order_id", sa.BigInteger(), nullable=False),
        sa.Column("product_id", sa.BigInteger(), nullable=True),
        sa.Column("product_name_snapshot", sa.String(length=100), nullable=False),
        sa.Column("product_type_snapshot", sa.String(length=20), nullable=False),
        sa.Column("product_summary_snapshot", sa.String(length=120), nullable=False),
        sa.Column("price_cents_snapshot", sa.Integer(), nullable=False),
        sa.Column("validity_days_snapshot", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("subtotal_cents", sa.Integer(), nullable=False),
        sa.Column("image_url_snapshot", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["order_id"], ["miniapp_orders.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["admin_products.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_miniapp_order_items_order_id"), "miniapp_order_items", ["order_id"])
    op.create_index(op.f("ix_miniapp_order_items_product_id"), "miniapp_order_items", ["product_id"])


def downgrade():
    op.drop_index(op.f("ix_miniapp_order_items_product_id"), table_name="miniapp_order_items")
    op.drop_index(op.f("ix_miniapp_order_items_order_id"), table_name="miniapp_order_items")
    op.drop_table("miniapp_order_items")
    op.drop_index(op.f("ix_miniapp_orders_user_id"), table_name="miniapp_orders")
    op.drop_index(op.f("ix_miniapp_orders_status"), table_name="miniapp_orders")
    op.drop_index(op.f("ix_miniapp_orders_product_type"), table_name="miniapp_orders")
    op.drop_index(op.f("ix_miniapp_orders_order_no"), table_name="miniapp_orders")
    op.drop_index(op.f("ix_miniapp_orders_deleted_at"), table_name="miniapp_orders")
    op.drop_table("miniapp_orders")
