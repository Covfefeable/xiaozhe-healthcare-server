"""add product image url

Revision ID: 202604190003
Revises: 202604190002
Create Date: 2026-04-19

"""
from alembic import op
import sqlalchemy as sa


revision = "202604190003"
down_revision = "202604190002"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("admin_products", sa.Column("image_url", sa.Text(), nullable=True))


def downgrade():
    op.drop_column("admin_products", "image_url")
