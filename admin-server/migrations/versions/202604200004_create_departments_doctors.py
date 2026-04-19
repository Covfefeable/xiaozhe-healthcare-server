"""create departments and doctors

Revision ID: 202604200004
Revises: 202604200003
Create Date: 2026-04-20

"""
from alembic import op
import sqlalchemy as sa


revision = "202604200004"
down_revision = "202604200003"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "admin_departments",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_admin_departments_deleted_at"), "admin_departments", ["deleted_at"])
    op.create_index(op.f("ix_admin_departments_name"), "admin_departments", ["name"])

    op.create_table(
        "admin_doctors",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("department_id", sa.BigInteger(), nullable=False),
        sa.Column("avatar_url", sa.Text(), nullable=True),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=False),
        sa.Column("title", sa.String(length=50), nullable=False),
        sa.Column("hospital", sa.String(length=100), nullable=False),
        sa.Column("summary", sa.String(length=120), nullable=False),
        sa.Column("specialty_tags", sa.JSON(), nullable=False),
        sa.Column("introduction", sa.Text(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["department_id"], ["admin_departments.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_admin_doctors_deleted_at"), "admin_doctors", ["deleted_at"])
    op.create_index(op.f("ix_admin_doctors_department_id"), "admin_doctors", ["department_id"])
    op.create_index(op.f("ix_admin_doctors_name"), "admin_doctors", ["name"])


def downgrade():
    op.drop_index(op.f("ix_admin_doctors_name"), table_name="admin_doctors")
    op.drop_index(op.f("ix_admin_doctors_department_id"), table_name="admin_doctors")
    op.drop_index(op.f("ix_admin_doctors_deleted_at"), table_name="admin_doctors")
    op.drop_table("admin_doctors")
    op.drop_index(op.f("ix_admin_departments_name"), table_name="admin_departments")
    op.drop_index(op.f("ix_admin_departments_deleted_at"), table_name="admin_departments")
    op.drop_table("admin_departments")
