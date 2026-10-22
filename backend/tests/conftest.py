import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import pytest_asyncio
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from backend.app.core.database import Base, get_session
from backend.app.main import app
from backend.app.models.issue import Issue, Analysis, TestCase
from httpx import AsyncClient, ASGITransport


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def test_engine():
    """Create a test engine synchronously - use aiosqlite in-memory."""
    # Create engine in a way that can be used synchronously
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    # Create tables
    import asyncio
    loop = asyncio.new_event_loop()
    async def create_tables():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    loop.run_until_complete(create_tables())
    loop.close()
    yield engine
    # Cleanup
    loop = asyncio.new_event_loop()
    loop.run_until_complete(engine.dispose())
    loop.close()


@pytest.fixture(scope="function")
def test_session_factory(test_engine):
    """Create a session factory for the test engine."""
    return async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function")
async def client(test_session_factory):
    """Create a test client with overridden session dependency."""
    async def _override():
        async with test_session_factory() as session:
            yield session
    
    app.dependency_overrides[get_session] = _override
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()