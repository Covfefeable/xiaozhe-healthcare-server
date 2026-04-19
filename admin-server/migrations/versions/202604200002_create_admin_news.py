"""create admin news

Revision ID: 202604200002
Revises: 202604200001
Create Date: 2026-04-20

"""
from alembic import op
import sqlalchemy as sa


revision = "202604200002"
down_revision = "202604200001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "admin_news",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("cover_image_url", sa.Text(), nullable=True),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("published_at", sa.DateTime(), nullable=False),
        sa.Column("content_markdown", sa.Text(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_admin_news_deleted_at"), "admin_news", ["deleted_at"])
    op.create_index(op.f("ix_admin_news_published_at"), "admin_news", ["published_at"])
    op.create_index(op.f("ix_admin_news_title"), "admin_news", ["title"])


def downgrade():
    op.drop_index(op.f("ix_admin_news_title"), table_name="admin_news")
    op.drop_index(op.f("ix_admin_news_published_at"), table_name="admin_news")
    op.drop_index(op.f("ix_admin_news_deleted_at"), table_name="admin_news")
    op.drop_table("admin_news")
