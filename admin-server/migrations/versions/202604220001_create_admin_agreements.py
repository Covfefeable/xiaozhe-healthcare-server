"""create admin agreements

Revision ID: 202604220001
Revises: 202604210002
Create Date: 2026-04-22

"""
from alembic import op
import sqlalchemy as sa


revision = "202604220001"
down_revision = "202604210002"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "admin_agreements",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("agreement_type", sa.String(length=30), nullable=False),
        sa.Column("title", sa.String(length=80), nullable=False),
        sa.Column("content_markdown", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_admin_agreements_agreement_type"),
        "admin_agreements",
        ["agreement_type"],
        unique=True,
    )
    op.execute(
        """
        INSERT INTO admin_agreements
            (created_at, updated_at, agreement_type, title, content_markdown)
        VALUES
            (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'user_agreement', '用户协议', '# 用户协议\n\n请在后台维护正式的用户协议内容。'),
            (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'privacy_policy', '隐私政策', '# 隐私政策\n\n请在后台维护正式的隐私政策内容。')
        """
    )


def downgrade():
    op.drop_index(op.f("ix_admin_agreements_agreement_type"), table_name="admin_agreements")
    op.drop_table("admin_agreements")
