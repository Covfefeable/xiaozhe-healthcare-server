"""create health records

Revision ID: 202604210001
Revises: 202604200004
Create Date: 2026-04-21

"""
from alembic import op
import sqlalchemy as sa


revision = "202604210001"
down_revision = "202604200004"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "miniapp_health_records",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("record_type", sa.String(length=30), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("image_urls", sa.JSON(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["miniapp_users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_miniapp_health_records_deleted_at"), "miniapp_health_records", ["deleted_at"])
    op.create_index(op.f("ix_miniapp_health_records_record_type"), "miniapp_health_records", ["record_type"])
    op.create_index(op.f("ix_miniapp_health_records_user_id"), "miniapp_health_records", ["user_id"])


def downgrade():
    op.drop_index(op.f("ix_miniapp_health_records_user_id"), table_name="miniapp_health_records")
    op.drop_index(op.f("ix_miniapp_health_records_record_type"), table_name="miniapp_health_records")
    op.drop_index(op.f("ix_miniapp_health_records_deleted_at"), table_name="miniapp_health_records")
    op.drop_table("miniapp_health_records")
