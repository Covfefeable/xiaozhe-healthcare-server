"""extend chat targets

Revision ID: 202604200003
Revises: 202604200002
Create Date: 2026-04-20

"""
from alembic import op
import sqlalchemy as sa


revision = "202604200003"
down_revision = "202604200002"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "miniapp_chat_conversations",
        sa.Column("target_type", sa.String(length=30), nullable=False, server_default="doctor"),
    )
    op.add_column(
        "miniapp_chat_conversations",
        sa.Column("customer_service_id", sa.BigInteger(), nullable=True),
    )
    op.add_column(
        "miniapp_chat_conversations",
        sa.Column("assistant_id", sa.BigInteger(), nullable=True),
    )
    op.create_foreign_key(
        "fk_miniapp_chat_conversations_customer_service_id",
        "miniapp_chat_conversations",
        "admin_customer_services",
        ["customer_service_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_miniapp_chat_conversations_assistant_id",
        "miniapp_chat_conversations",
        "admin_assistants",
        ["assistant_id"],
        ["id"],
    )
    op.create_index(
        op.f("ix_miniapp_chat_conversations_target_type"),
        "miniapp_chat_conversations",
        ["target_type"],
    )
    op.create_index(
        op.f("ix_miniapp_chat_conversations_customer_service_id"),
        "miniapp_chat_conversations",
        ["customer_service_id"],
    )
    op.create_index(
        op.f("ix_miniapp_chat_conversations_assistant_id"),
        "miniapp_chat_conversations",
        ["assistant_id"],
    )
    op.alter_column("miniapp_chat_conversations", "target_type", server_default=None)


def downgrade():
    op.drop_index(op.f("ix_miniapp_chat_conversations_assistant_id"), table_name="miniapp_chat_conversations")
    op.drop_index(op.f("ix_miniapp_chat_conversations_customer_service_id"), table_name="miniapp_chat_conversations")
    op.drop_index(op.f("ix_miniapp_chat_conversations_target_type"), table_name="miniapp_chat_conversations")
    op.drop_constraint(
        "fk_miniapp_chat_conversations_assistant_id",
        "miniapp_chat_conversations",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_miniapp_chat_conversations_customer_service_id",
        "miniapp_chat_conversations",
        type_="foreignkey",
    )
    op.drop_column("miniapp_chat_conversations", "assistant_id")
    op.drop_column("miniapp_chat_conversations", "customer_service_id")
    op.drop_column("miniapp_chat_conversations", "target_type")
