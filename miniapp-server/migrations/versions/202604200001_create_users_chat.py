"""create users and chat tables

Revision ID: 202604200001
Revises:
Create Date: 2026-04-20

"""
from alembic import op
import sqlalchemy as sa


revision = "202604200001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "miniapp_users",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("openid", sa.String(length=64), nullable=False),
        sa.Column("unionid", sa.String(length=64), nullable=True),
        sa.Column("nickname", sa.String(length=50), nullable=False),
        sa.Column("avatar_url", sa.Text(), nullable=True),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("gender", sa.String(length=10), nullable=False),
        sa.Column("birthday", sa.Date(), nullable=True),
        sa.Column("real_name", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("membership_status", sa.String(length=20), nullable=False),
        sa.Column("membership_expires_at", sa.DateTime(), nullable=True),
        sa.Column("last_login_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("openid"),
    )
    op.create_index(op.f("ix_miniapp_users_deleted_at"), "miniapp_users", ["deleted_at"])
    op.create_index(op.f("ix_miniapp_users_openid"), "miniapp_users", ["openid"])
    op.create_index(op.f("ix_miniapp_users_phone"), "miniapp_users", ["phone"])
    op.create_index(op.f("ix_miniapp_users_status"), "miniapp_users", ["status"])
    op.create_index(op.f("ix_miniapp_users_unionid"), "miniapp_users", ["unionid"])

    op.create_table(
        "miniapp_user_memberships",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("product_id", sa.BigInteger(), nullable=True),
        sa.Column("level", sa.String(length=30), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("starts_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("source_type", sa.String(length=30), nullable=False),
        sa.Column("source_id", sa.BigInteger(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["miniapp_users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_miniapp_user_memberships_deleted_at"), "miniapp_user_memberships", ["deleted_at"])
    op.create_index(op.f("ix_miniapp_user_memberships_expires_at"), "miniapp_user_memberships", ["expires_at"])
    op.create_index(op.f("ix_miniapp_user_memberships_product_id"), "miniapp_user_memberships", ["product_id"])
    op.create_index(op.f("ix_miniapp_user_memberships_status"), "miniapp_user_memberships", ["status"])
    op.create_index(op.f("ix_miniapp_user_memberships_user_id"), "miniapp_user_memberships", ["user_id"])

    op.create_table(
        "miniapp_chat_conversations",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("conversation_type", sa.String(length=20), nullable=False),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("doctor_id", sa.BigInteger(), nullable=True),
        sa.Column("owner_user_id", sa.BigInteger(), nullable=False),
        sa.Column("last_message_id", sa.BigInteger(), nullable=True),
        sa.Column("last_message_preview", sa.String(length=255), nullable=False),
        sa.Column("last_message_type", sa.String(length=20), nullable=False),
        sa.Column("last_message_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["doctor_id"], ["admin_doctors.id"]),
        sa.ForeignKeyConstraint(["owner_user_id"], ["miniapp_users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_miniapp_chat_conversations_conversation_type"), "miniapp_chat_conversations", ["conversation_type"])
    op.create_index(op.f("ix_miniapp_chat_conversations_deleted_at"), "miniapp_chat_conversations", ["deleted_at"])
    op.create_index(op.f("ix_miniapp_chat_conversations_doctor_id"), "miniapp_chat_conversations", ["doctor_id"])
    op.create_index(op.f("ix_miniapp_chat_conversations_last_message_at"), "miniapp_chat_conversations", ["last_message_at"])
    op.create_index(op.f("ix_miniapp_chat_conversations_owner_user_id"), "miniapp_chat_conversations", ["owner_user_id"])
    op.create_unique_constraint(
        "uq_miniapp_chat_single_user_doctor",
        "miniapp_chat_conversations",
        ["owner_user_id", "doctor_id"],
    )

    op.create_table(
        "miniapp_chat_conversation_members",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("conversation_id", sa.BigInteger(), nullable=False),
        sa.Column("member_type", sa.String(length=20), nullable=False),
        sa.Column("member_id", sa.BigInteger(), nullable=False),
        sa.Column("unread_count", sa.Integer(), nullable=False),
        sa.Column("last_read_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["conversation_id"], ["miniapp_chat_conversations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_miniapp_chat_conversation_members_conversation_id"), "miniapp_chat_conversation_members", ["conversation_id"])
    op.create_index(op.f("ix_miniapp_chat_conversation_members_deleted_at"), "miniapp_chat_conversation_members", ["deleted_at"])
    op.create_index(op.f("ix_miniapp_chat_conversation_members_member_id"), "miniapp_chat_conversation_members", ["member_id"])
    op.create_index(op.f("ix_miniapp_chat_conversation_members_member_type"), "miniapp_chat_conversation_members", ["member_type"])
    op.create_unique_constraint(
        "uq_miniapp_chat_member",
        "miniapp_chat_conversation_members",
        ["conversation_id", "member_type", "member_id"],
    )

    op.create_table(
        "miniapp_chat_messages",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("conversation_id", sa.BigInteger(), nullable=False),
        sa.Column("sender_type", sa.String(length=20), nullable=False),
        sa.Column("sender_id", sa.BigInteger(), nullable=False),
        sa.Column("message_type", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("sent_at", sa.DateTime(), nullable=False),
        sa.Column("recalled_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["conversation_id"], ["miniapp_chat_conversations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_miniapp_chat_messages_conversation_id"), "miniapp_chat_messages", ["conversation_id"])
    op.create_index(op.f("ix_miniapp_chat_messages_deleted_at"), "miniapp_chat_messages", ["deleted_at"])
    op.create_index(op.f("ix_miniapp_chat_messages_message_type"), "miniapp_chat_messages", ["message_type"])
    op.create_index(op.f("ix_miniapp_chat_messages_sender_id"), "miniapp_chat_messages", ["sender_id"])
    op.create_index(op.f("ix_miniapp_chat_messages_sender_type"), "miniapp_chat_messages", ["sender_type"])
    op.create_index(op.f("ix_miniapp_chat_messages_sent_at"), "miniapp_chat_messages", ["sent_at"])
    op.create_index(op.f("ix_miniapp_chat_messages_status"), "miniapp_chat_messages", ["status"])

    op.create_table(
        "miniapp_chat_message_attachments",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("message_id", sa.BigInteger(), nullable=False),
        sa.Column("file_type", sa.String(length=20), nullable=False),
        sa.Column("file_url", sa.Text(), nullable=False),
        sa.Column("thumbnail_url", sa.Text(), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column("file_size", sa.BigInteger(), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("width", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["message_id"], ["miniapp_chat_messages.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_miniapp_chat_message_attachments_file_type"), "miniapp_chat_message_attachments", ["file_type"])
    op.create_index(op.f("ix_miniapp_chat_message_attachments_message_id"), "miniapp_chat_message_attachments", ["message_id"])


def downgrade():
    op.drop_index(op.f("ix_miniapp_chat_message_attachments_message_id"), table_name="miniapp_chat_message_attachments")
    op.drop_index(op.f("ix_miniapp_chat_message_attachments_file_type"), table_name="miniapp_chat_message_attachments")
    op.drop_table("miniapp_chat_message_attachments")
    op.drop_index(op.f("ix_miniapp_chat_messages_status"), table_name="miniapp_chat_messages")
    op.drop_index(op.f("ix_miniapp_chat_messages_sent_at"), table_name="miniapp_chat_messages")
    op.drop_index(op.f("ix_miniapp_chat_messages_sender_type"), table_name="miniapp_chat_messages")
    op.drop_index(op.f("ix_miniapp_chat_messages_sender_id"), table_name="miniapp_chat_messages")
    op.drop_index(op.f("ix_miniapp_chat_messages_message_type"), table_name="miniapp_chat_messages")
    op.drop_index(op.f("ix_miniapp_chat_messages_deleted_at"), table_name="miniapp_chat_messages")
    op.drop_index(op.f("ix_miniapp_chat_messages_conversation_id"), table_name="miniapp_chat_messages")
    op.drop_table("miniapp_chat_messages")
    op.drop_constraint("uq_miniapp_chat_member", "miniapp_chat_conversation_members", type_="unique")
    op.drop_index(op.f("ix_miniapp_chat_conversation_members_member_type"), table_name="miniapp_chat_conversation_members")
    op.drop_index(op.f("ix_miniapp_chat_conversation_members_member_id"), table_name="miniapp_chat_conversation_members")
    op.drop_index(op.f("ix_miniapp_chat_conversation_members_deleted_at"), table_name="miniapp_chat_conversation_members")
    op.drop_index(op.f("ix_miniapp_chat_conversation_members_conversation_id"), table_name="miniapp_chat_conversation_members")
    op.drop_table("miniapp_chat_conversation_members")
    op.drop_constraint("uq_miniapp_chat_single_user_doctor", "miniapp_chat_conversations", type_="unique")
    op.drop_index(op.f("ix_miniapp_chat_conversations_owner_user_id"), table_name="miniapp_chat_conversations")
    op.drop_index(op.f("ix_miniapp_chat_conversations_last_message_at"), table_name="miniapp_chat_conversations")
    op.drop_index(op.f("ix_miniapp_chat_conversations_doctor_id"), table_name="miniapp_chat_conversations")
    op.drop_index(op.f("ix_miniapp_chat_conversations_deleted_at"), table_name="miniapp_chat_conversations")
    op.drop_index(op.f("ix_miniapp_chat_conversations_conversation_type"), table_name="miniapp_chat_conversations")
    op.drop_table("miniapp_chat_conversations")
    op.drop_index(op.f("ix_miniapp_user_memberships_user_id"), table_name="miniapp_user_memberships")
    op.drop_index(op.f("ix_miniapp_user_memberships_status"), table_name="miniapp_user_memberships")
    op.drop_index(op.f("ix_miniapp_user_memberships_product_id"), table_name="miniapp_user_memberships")
    op.drop_index(op.f("ix_miniapp_user_memberships_expires_at"), table_name="miniapp_user_memberships")
    op.drop_index(op.f("ix_miniapp_user_memberships_deleted_at"), table_name="miniapp_user_memberships")
    op.drop_table("miniapp_user_memberships")
    op.drop_index(op.f("ix_miniapp_users_unionid"), table_name="miniapp_users")
    op.drop_index(op.f("ix_miniapp_users_status"), table_name="miniapp_users")
    op.drop_index(op.f("ix_miniapp_users_phone"), table_name="miniapp_users")
    op.drop_index(op.f("ix_miniapp_users_openid"), table_name="miniapp_users")
    op.drop_index(op.f("ix_miniapp_users_deleted_at"), table_name="miniapp_users")
    op.drop_table("miniapp_users")
