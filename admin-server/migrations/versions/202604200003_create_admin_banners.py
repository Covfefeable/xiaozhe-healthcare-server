"""create admin banners

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
    op.create_table(
        "admin_banners",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("title", sa.String(length=80), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_admin_banners_deleted_at"), "admin_banners", ["deleted_at"])
    op.create_index(op.f("ix_admin_banners_title"), "admin_banners", ["title"])


def downgrade():
    op.drop_index(op.f("ix_admin_banners_title"), table_name="admin_banners")
    op.drop_index(op.f("ix_admin_banners_deleted_at"), table_name="admin_banners")
    op.drop_table("admin_banners")
