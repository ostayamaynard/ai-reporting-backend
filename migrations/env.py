from sqlalchemy import engine_from_config, pool
from alembic import context
import os

config = context.config
target_metadata = None  # we use SQL files (no autogenerate here)

def run_migrations_offline():
    url = os.getenv("DATABASE_URL")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    # Option A: give "url" with empty prefix
    connectable = engine_from_config({"url": os.getenv("DATABASE_URL")},
                                     prefix="",
                                     poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()


