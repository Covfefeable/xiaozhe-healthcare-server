"""add assistant type

Revision ID: 202604210002
Revises: 202604200008
Create Date: 2026-04-21

"""
from alembic import op
import sqlalchemy as sa


revision = "202604210002"
down_revision = "202604200008"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "admin_assistants",
        sa.Column(
            "assistant_type",
            sa.String(length=30),
            nullable=False,
            server_default="health_manager",
        ),
    )
    op.create_index(
        op.f("ix_admin_assistants_assistant_type"),
        "admin_assistants",
        ["assistant_type"],
    )


def downgrade():
    op.drop_index(op.f("ix_admin_assistants_assistant_type"), table_name="admin_assistants")
    op.drop_column("admin_assistants", "assistant_type")
