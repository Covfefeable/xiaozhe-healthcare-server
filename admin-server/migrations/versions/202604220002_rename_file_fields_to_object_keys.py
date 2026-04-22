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
    op.alter_column("admin_products", "image_url", new_column_name="image_object_key")
    op.alter_column("admin_banners", "image_url", new_column_name="image_object_key")
    op.alter_column("admin_news", "cover_image_url", new_column_name="cover_image_object_key")
    op.alter_column("admin_doctors", "avatar_url", new_column_name="avatar_object_key")
    op.alter_column("admin_assistants", "avatar_url", new_column_name="avatar_object_key")
    op.alter_column("admin_customer_services", "avatar_url", new_column_name="avatar_object_key")


def downgrade():
    op.alter_column("admin_customer_services", "avatar_object_key", new_column_name="avatar_url")
    op.alter_column("admin_assistants", "avatar_object_key", new_column_name="avatar_url")
    op.alter_column("admin_doctors", "avatar_object_key", new_column_name="avatar_url")
    op.alter_column("admin_news", "cover_image_object_key", new_column_name="cover_image_url")
    op.alter_column("admin_banners", "image_object_key", new_column_name="image_url")
    op.alter_column("admin_products", "image_object_key", new_column_name="image_url")
