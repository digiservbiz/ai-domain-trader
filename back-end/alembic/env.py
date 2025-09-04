from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from app.db.base import Base
from app.config import settings
config = context.config
config.set_main_option('sqlalchemy.url', settings.DATABASE_URL)
target_metadata = Base.metadata
def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
run_migrations_online()
