"""create domains table

Revision ID: 0001
Revises:
Create Date: 2026-05-17
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "domains",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String(), nullable=False, unique=True, index=True),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("est_value", sa.Float(), nullable=True),
    )


def downgrade():
    op.drop_table("domains")
