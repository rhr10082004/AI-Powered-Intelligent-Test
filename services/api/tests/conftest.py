"""Test fixtures and configuration."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from services.api.main import create_app
from services.api.database import Base, get_db_session
from services.api.config import Settings


@pytest.fixture
async def test_settings():
    """Get test settings."""
    return Settings(
        database_url="sqlite+aiosqlite:///:memory:",
        jwt_secret_key="test_secret_key",
        jwt_algorithm="HS256",
    )


@pytest.fixture
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest.fixture
async def test_session_factory(test_engine):
    """Create test session factory."""
    return sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        future=True,
    )


@pytest.fixture
async def test_db_session(test_session_factory):
    """Create test database session."""
    async with test_session_factory() as session:
        yield session


@pytest.fixture
async def client(test_engine, test_session_factory):
    """Create test client."""
    app = create_app()
    
    # Override get_db_session dependency
    async def override_get_db():
        async with test_session_factory() as session:
            yield session
    
    app.dependency_overrides[get_db_session] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()
