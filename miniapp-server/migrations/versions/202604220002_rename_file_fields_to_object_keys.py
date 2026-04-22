"""rename file fields to object keys

Revision ID: 202604220002
Revises: 202604220001
Create Date: 2026-04-22

"""
from alembic import op


revision = "202604220002"
down_revision = "202604220001"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("miniapp_users", "avatar_url", new_column_name="avatar_object_key")
    op.alter_column("miniapp_health_records", "image_urls", new_column_name="image_object_keys")
    op.alter_column("miniapp_orders", "refund_image_urls", new_column_name="refund_image_object_keys")
    op.alter_column("miniapp_order_items", "image_url_snapshot", new_column_name="image_object_key_snapshot")
    op.alter_column("miniapp_chat_conversation_members", "avatar_url", new_column_name="avatar_object_key")
    op.alter_column("miniapp_chat_message_attachments", "file_url", new_column_name="file_object_key")
    op.alter_column("miniapp_chat_message_attachments", "thumbnail_url", new_column_name="thumbnail_object_key")


def downgrade():
    op.alter_column("miniapp_chat_message_attachments", "thumbnail_object_key", new_column_name="thumbnail_url")
    op.alter_column("miniapp_chat_message_attachments", "file_object_key", new_column_name="file_url")
    op.alter_column("miniapp_chat_conversation_members", "avatar_object_key", new_column_name="avatar_url")
    op.alter_column("miniapp_order_items", "image_object_key_snapshot", new_column_name="image_url_snapshot")
    op.alter_column("miniapp_orders", "refund_image_object_keys", new_column_name="refund_image_urls")
    op.alter_column("miniapp_health_records", "image_object_keys", new_column_name="image_urls")
    op.alter_column("miniapp_users", "avatar_object_key", new_column_name="avatar_url")
