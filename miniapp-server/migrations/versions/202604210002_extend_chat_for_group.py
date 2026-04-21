"""extend chat for group conversations

Revision ID: 202604210002
Revises: 202604210001
Create Date: 2026-04-21

"""
from alembic import op
import sqlalchemy as sa


revision = "202604210002"
down_revision = "202604210001"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "miniapp_chat_conversation_members",
        sa.Column("display_name", sa.String(length=100), nullable=False, server_default=""),
    )
    op.add_column(
        "miniapp_chat_conversation_members",
        sa.Column("avatar_url", sa.Text(), nullable=False, server_default=""),
    )
    op.add_column(
        "miniapp_chat_conversation_members",
        sa.Column("role_label", sa.String(length=30), nullable=False, server_default=""),
    )
    op.add_column(
        "miniapp_chat_conversation_members",
        sa.Column("invited_by_type", sa.String(length=20), nullable=False, server_default=""),
    )
    op.add_column(
        "miniapp_chat_conversation_members",
        sa.Column("invited_by_id", sa.BigInteger(), nullable=True),
    )
    op.add_column(
        "miniapp_chat_messages",
        sa.Column("sender_name", sa.String(length=100), nullable=False, server_default=""),
    )
    op.add_column(
        "miniapp_chat_messages",
        sa.Column("sender_avatar", sa.Text(), nullable=False, server_default=""),
    )
    op.add_column(
        "miniapp_chat_messages",
        sa.Column("sender_role_label", sa.String(length=30), nullable=False, server_default=""),
    )


def downgrade():
    op.drop_column("miniapp_chat_messages", "sender_role_label")
    op.drop_column("miniapp_chat_messages", "sender_avatar")
    op.drop_column("miniapp_chat_messages", "sender_name")
    op.drop_column("miniapp_chat_conversation_members", "invited_by_id")
    op.drop_column("miniapp_chat_conversation_members", "invited_by_type")
    op.drop_column("miniapp_chat_conversation_members", "role_label")
    op.drop_column("miniapp_chat_conversation_members", "avatar_url")
    op.drop_column("miniapp_chat_conversation_members", "display_name")
