"""Scope portfolio and auction/watch records to authenticated users.

Existing rows are migrated only when ownership is unambiguous: if exactly one user
exists, legacy rows are assigned to that user. If multiple users exist while legacy
rows are present, the migration aborts rather than guessing ownership.
"""
from alembic import op
import sqlalchemy as sa

revision = "0005_scope_user_records"
down_revision = "0004"
branch_labels = None
depends_on = None


def _scope_table(table_name: str) -> None:
    op.add_column(table_name, sa.Column("user_id", sa.Integer(), nullable=True))
    op.create_index(f"ix_{table_name}_user_id", table_name, ["user_id"])
    op.create_foreign_key(
        f"fk_{table_name}_user_id_users",
        table_name,
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    bind = op.get_bind()
    users = bind.execute(sa.text("SELECT id FROM users ORDER BY id")).fetchall()
    legacy_count = bind.execute(sa.text(f"SELECT COUNT(*) FROM {table_name}")).scalar_one()
    if legacy_count:
        if len(users) != 1:
            raise RuntimeError(
                f"Cannot safely migrate {table_name}: legacy rows exist but ownership is ambiguous"
            )
        bind.execute(
            sa.text(f"UPDATE {table_name} SET user_id = :user_id WHERE user_id IS NULL"),
            {"user_id": users[0][0]},
        )

    if bind.dialect.name == "sqlite":
        with op.batch_alter_table(table_name) as batch:
            batch.alter_column("user_id", existing_type=sa.Integer(), nullable=False)
    else:
        op.alter_column(table_name, "user_id", existing_type=sa.Integer(), nullable=False)


def upgrade() -> None:
    _scope_table("portfolio")
    _scope_table("snipe_targets")


def downgrade() -> None:
    for table_name in ("snipe_targets", "portfolio"):
        if op.get_bind().dialect.name == "sqlite":
            with op.batch_alter_table(table_name) as batch:
                batch.drop_constraint(f"fk_{table_name}_user_id_users", type_="foreignkey")
                batch.drop_index(f"ix_{table_name}_user_id")
                batch.drop_column("user_id")
        else:
            op.drop_constraint(f"fk_{table_name}_user_id_users", table_name, type_="foreignkey")
            op.drop_index(f"ix_{table_name}_user_id", table_name=table_name)
            op.drop_column(table_name, "user_id")
