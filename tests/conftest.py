"""Shared test fixtures."""

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import event
from sqlalchemy.pool import StaticPool


@pytest.fixture
def sample_icp_criteria() -> dict:
    """Sample ICP criteria for testing."""
    return {
        "name": "Enterprise SaaS",
        "target_industries": ["Technology", "SaaS", "Software"],
        "min_employee_count": 50,
        "max_employee_count": 5000,
        "target_titles": ["VP of Sales", "CRO", "Head of Revenue"],
        "target_seniority": ["C-Suite", "VP", "Director"],
        "target_geography": ["US", "Canada"],
        "required_tech_stack": ["Salesforce", "Python"],
    }


@pytest.fixture
def sample_scoring_weights() -> dict:
    """Sample scoring weights."""
    return {
        "industry": 25,
        "company_size": 20,
        "seniority": 20,
        "title": 15,
        "geography": 10,
        "tech_stack": 10,
    }


@pytest.fixture
async def db_session():
    """In-memory SQLite async session for unit tests.

    Uses StaticPool + check_same_thread=False to support asyncio and aiosqlite.
    Note: Models using PostgreSQL-specific UUID columns fall back to String on SQLite.
    """
    from ai_sdr.db.base import Base
    # Import all models so metadata is populated
    import ai_sdr.models  # noqa: F401

    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # SQLite doesn't support UUID natively — patch dialect for tests
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with factory() as session:
        yield session

    await engine.dispose()


@pytest.fixture
async def api_client():
    """ASGI test client for integration tests."""
    from ai_sdr.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
