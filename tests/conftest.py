import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from core.database.models import Base
from core.database.database import async_session_maker

# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def engine():
    """Create an async engine for the in-memory SQLite database."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture(scope="function")
async def session(engine):
    """Create a new database session for each test function."""
    async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_maker() as session:
        yield session

@pytest.fixture(scope="function")
async def client(session):
    """Mock the FastAPI app and provide a test client."""
    # This fixture is a placeholder. Actual FastAPI app mocking would go here.
    # For now, it just provides a session.
    yield session

@pytest.fixture(autouse=True)
async def clear_database(session):
    """Clear all data from tables after each test to ensure isolation."""
    for table in reversed(Base.metadata.sorted_tables):
        await session.execute(table.delete())
    await session.commit()
