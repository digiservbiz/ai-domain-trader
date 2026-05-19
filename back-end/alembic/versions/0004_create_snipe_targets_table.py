"""create snipe_targets table

Revision ID: 0004
Revises: 0003
Create Date: 2026-05-19
"""
from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "snipe_targets",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("domain", sa.String(), nullable=False, index=True),
        sa.Column("max_bid", sa.Float(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="watching"),
        sa.Column("current_bid", sa.Float(), nullable=True),
        sa.Column("last_checked", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("snipe_targets")
