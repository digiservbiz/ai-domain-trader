"""Persist tamper-evident decision audit snapshots.

Revision ID: 0006_persist_decision_audits
Revises: 0005_scope_user_records
"""
from alembic import op
import sqlalchemy as sa

revision = "0006_persist_decision_audits"
down_revision = "0005_scope_user_records"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "decision_audits",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("audit_id", sa.String(length=64), nullable=False),
        sa.Column("domain", sa.String(length=253), nullable=False),
        sa.Column("recommendation", sa.String(length=64), nullable=False),
        sa.Column("hash_algorithm", sa.String(length=16), nullable=False, server_default="sha256"),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", "audit_id", name="uq_decision_audits_user_hash"),
    )
    op.create_index("ix_decision_audits_user_id", "decision_audits", ["user_id"])
    op.create_index("ix_decision_audits_audit_id", "decision_audits", ["audit_id"])
    op.create_index("ix_decision_audits_domain", "decision_audits", ["domain"])
    op.create_index("ix_decision_audits_recommendation", "decision_audits", ["recommendation"])
    op.create_index("ix_decision_audits_created_at", "decision_audits", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_decision_audits_created_at", table_name="decision_audits")
    op.drop_index("ix_decision_audits_recommendation", table_name="decision_audits")
    op.drop_index("ix_decision_audits_domain", table_name="decision_audits")
    op.drop_index("ix_decision_audits_audit_id", table_name="decision_audits")
    op.drop_index("ix_decision_audits_user_id", table_name="decision_audits")
    op.drop_table("decision_audits")
