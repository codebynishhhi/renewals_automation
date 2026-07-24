import asyncio
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
from sqlalchemy import pool
# Import your settings and base model blueprints
from src.common.settings import settings
from src.common.database import Base
from src.api.models import Project, Artifact, DocumentChunks, Rules

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

async def run_migrations_online() -> None:
    """Run migrations in 'online' mode using standard async engine setup."""
    url = f"postgresql+asyncpg://{settings.db_username}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"
    
    # Debug print line to confirm your runtime details
    print(f"\n🚀 FORCING MIGRATION RUN AGAINST URL: {url}\n")
    
    connectable = create_async_engine(url)

    async with connectable.connect() as connection:
        # CRUCIAL FIX: Changing "await connection.begin()" to an "async with" context blocker
        # This guarantees an explicit SQL COMMIT is sent to Postgres when the block finishes cleanly
        async with connection.begin():
            await connection.run_sync(do_run_migrations)

    await connectable.dispose()



def do_run_migrations(connection) -> None:
    """Helper context task to map the sync runner execution."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """Run migrations in 'online' mode using standard async engine setup."""
    # Bypasses the missing alembic.ini URL string error completely
    url = settings.database_url_sync 
    
    connectable = create_async_engine(url)

    async with connectable.connect() as connection:
        await connection.begin() 
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    # Safely spin up an event loop runner to execute the migration task
    asyncio.run(run_migrations_online())