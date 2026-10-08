"""
Database configuration and session management.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker

from services.api.config import get_settings

# Base class for all ORM models
Base = declarative_base()


def get_database_url(settings=None):
    """Convert PostgreSQL URL to async URL."""
    if settings is None:
        settings = get_settings()
    
    # Convert postgresql:// to postgresql+asyncpg://
    url = settings.database_url
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def create_engine():
    """Create async SQLAlchemy engine."""
    settings = get_settings()
    database_url = get_database_url(settings)

    engine_kwargs = {
        "echo": settings.db_echo,
        "future": True,
        "pool_pre_ping": True,
    }

    if not database_url.startswith("sqlite"):
        engine_kwargs["pool_size"] = 20
        engine_kwargs["max_overflow"] = 10

    engine = create_async_engine(
        database_url,
        **engine_kwargs,
    )
    return engine


def create_session_factory(engine):
    """Create session factory."""
    return sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        future=True,
    )


# Global engine and session factory
engine = create_engine()
async_session_factory = create_session_factory(engine)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database session in routes."""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database tables."""
    from services.api.models_phase2_isolated import BasePhase2
    from services.api.seed import seed_learning_content

    settings = get_settings()
    if settings.environment.casefold() in {"development", "test", "testing"}:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            await conn.run_sync(BasePhase2.metadata.create_all)
            if engine.url.get_backend_name() == "sqlite":
                await conn.run_sync(_upgrade_sqlite_progress_uniqueness)
                await conn.run_sync(_upgrade_sqlite_study_session_schema)

        await seed_learning_content(async_session_factory)


def _upgrade_sqlite_progress_uniqueness(connection):
    """Preserve local progress rows while replacing the legacy unique user constraint."""
    from sqlalchemy import MetaData, inspect, select, text
    from services.api.models_phase2_isolated import BasePhase2

    if "learning_user_progress" not in inspect(connection).get_table_names():
        return

    unique_constraints = inspect(connection).get_unique_constraints("learning_user_progress")
    if not any(item.get("column_names") == ["user_id"] for item in unique_constraints):
        return

    source = BasePhase2.metadata.tables["learning_user_progress"]
    target_metadata = MetaData()
    replacement = source.to_metadata(target_metadata, name="learning_user_progress_rebuild")
    replacement.create(connection)
    column_names = [column.name for column in source.columns]
    connection.execute(
        replacement.insert().from_select(
            column_names,
            select(*(source.c[column_name] for column_name in column_names)),
        )
    )
    connection.execute(text("DROP TABLE learning_user_progress"))
    connection.execute(
        text("ALTER TABLE learning_user_progress_rebuild RENAME TO learning_user_progress")
    )


def _upgrade_sqlite_study_session_schema(connection):
    """Add session IDs/indexes to local databases created before session history."""
    from sqlalchemy import inspect, text

    inspector = inspect(connection)
    table_name = "learning_study_sessions"
    if table_name not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns(table_name)}
    if "session_id" not in columns:
        connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN session_id VARCHAR"))

    inspector = inspect(connection)
    unique_constraints = inspector.get_unique_constraints(table_name)
    unique_indexes = inspector.get_indexes(table_name)
    has_session_unique = any(
        item.get("column_names") == ["user_id", "session_id"]
        for item in [*unique_constraints, *unique_indexes]
    )
    if not has_session_unique:
        connection.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS ux_learning_sessions_user_session "
                "ON learning_study_sessions (user_id, session_id)"
            )
        )


async def drop_db():
    """Drop all database tables (use with caution)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def close_db():
    """Close database connection."""
    await engine.dispose()
