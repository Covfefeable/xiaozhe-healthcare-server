"""update product validity from 360 to 365

Revision ID: 202604200007
Revises: 202604200006
Create Date: 2026-04-20 00:00:00.000000
"""

from alembic import op


revision = "202604200007"
down_revision = "202604200006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE admin_products SET validity_days = 365 WHERE validity_days = 360")


def downgrade() -> None:
    op.execute("UPDATE admin_products SET validity_days = 360 WHERE validity_days = 365")
