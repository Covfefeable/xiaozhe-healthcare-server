"""add user health manager

Revision ID: 202604250001
Revises: 202604220002
Create Date: 2026-04-25

"""
from alembic import op
import sqlalchemy as sa


revision = "202604250001"
down_revision = "202604220002"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("miniapp_users", sa.Column("health_manager_id", sa.BigInteger(), nullable=True))
    op.create_index(op.f("ix_miniapp_users_health_manager_id"), "miniapp_users", ["health_manager_id"], unique=False)
    op.create_foreign_key(
        "fk_miniapp_users_health_manager_id_admin_assistants",
        "miniapp_users",
        "admin_assistants",
        ["health_manager_id"],
        ["id"],
    )


def downgrade():
    op.drop_constraint("fk_miniapp_users_health_manager_id_admin_assistants", "miniapp_users", type_="foreignkey")
    op.drop_index(op.f("ix_miniapp_users_health_manager_id"), table_name="miniapp_users")
    op.drop_column("miniapp_users", "health_manager_id")
