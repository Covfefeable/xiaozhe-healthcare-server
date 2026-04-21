"""add order refund fields

Revision ID: 202604220001
Revises: 202604210002
Create Date: 2026-04-22

"""
from alembic import op
import sqlalchemy as sa


revision = "202604220001"
down_revision = "202604210002"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("miniapp_orders", sa.Column("refund_reason", sa.String(length=100), nullable=False, server_default=""))
    op.add_column("miniapp_orders", sa.Column("refund_description", sa.Text(), nullable=False, server_default=""))
    op.add_column(
        "miniapp_orders",
        sa.Column("refund_image_urls", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
    )
    op.add_column("miniapp_orders", sa.Column("refund_requested_at", sa.DateTime(), nullable=True))
    op.add_column("miniapp_orders", sa.Column("refund_handled_at", sa.DateTime(), nullable=True))
    op.add_column(
        "miniapp_orders",
        sa.Column("refund_reject_reason", sa.String(length=255), nullable=False, server_default=""),
    )


def downgrade():
    op.drop_column("miniapp_orders", "refund_reject_reason")
    op.drop_column("miniapp_orders", "refund_handled_at")
    op.drop_column("miniapp_orders", "refund_requested_at")
    op.drop_column("miniapp_orders", "refund_image_urls")
    op.drop_column("miniapp_orders", "refund_description")
    op.drop_column("miniapp_orders", "refund_reason")
