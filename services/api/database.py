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
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def create_engine():
    """Create async SQLAlchemy engine."""
    settings = get_settings()
    database_url = get_database_url(settings)
    
    engine = create_async_engine(
        database_url,
        echo=settings.db_echo,
        future=True,
        pool_pre_ping=True,
        pool_size=20,
        max_overflow=10,
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
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    """Drop all database tables (use with caution)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def close_db():
    """Close database connection."""
    await engine.dispose()
