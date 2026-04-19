"""create assistants and customer services

Revision ID: 202604200005
Revises: 202604200004
Create Date: 2026-04-20

"""
from alembic import op
import sqlalchemy as sa


revision = "202604200005"
down_revision = "202604200004"
branch_labels = None
depends_on = None


def _create_staff_table(table_name: str) -> None:
    op.create_table(
        table_name,
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("avatar_url", sa.Text(), nullable=True),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("remark", sa.String(length=255), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f(f"ix_{table_name}_deleted_at"), table_name, ["deleted_at"])
    op.create_index(op.f(f"ix_{table_name}_name"), table_name, ["name"])
    op.create_index(op.f(f"ix_{table_name}_phone"), table_name, ["phone"])
    op.create_index(op.f(f"ix_{table_name}_status"), table_name, ["status"])
    op.create_index(
        f"uq_{table_name}_phone_active",
        table_name,
        ["phone"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )


def _drop_staff_table(table_name: str) -> None:
    op.drop_index(f"uq_{table_name}_phone_active", table_name=table_name)
    op.drop_index(op.f(f"ix_{table_name}_status"), table_name=table_name)
    op.drop_index(op.f(f"ix_{table_name}_phone"), table_name=table_name)
    op.drop_index(op.f(f"ix_{table_name}_name"), table_name=table_name)
    op.drop_index(op.f(f"ix_{table_name}_deleted_at"), table_name=table_name)
    op.drop_table(table_name)


def upgrade():
    _create_staff_table("admin_assistants")
    _create_staff_table("admin_customer_services")


def downgrade():
    _drop_staff_table("admin_customer_services")
    _drop_staff_table("admin_assistants")
