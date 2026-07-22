import asyncio
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

# Import your settings and base model blueprints
from src.common.settings import settings
from src.common.database import Base
from src.api.models import Project, Artifact, DocumentChunks, Rules

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    # Reuses your async driver URL property directly
    url = settings.database_url_sync
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "pyformat"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection) -> None:
    """Helper context task to map the sync runner execution."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """Run migrations in 'online' mode using an async engine connection."""
    connectable = create_async_engine(
        settings.database_url_sync,
        poolclass=None,
    )

    async with connectable.connect() as connection:
        # run_sync bridges the synchronous migration runner with async blocks
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    # Safely spin up an event loop runner to execute the migration task
    asyncio.run(run_migrations_online())