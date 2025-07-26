# tests/conftest.py

import asyncio
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from core.database.models import Base

# Используем SQLite в памяти для тестов
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    """Создает асинхронный движок для тестовой БД."""
    engine = create_async_engine(TEST_DB_URL, echo=False)
    return engine

@pytest.fixture(scope="function")
async def setup_database(test_engine):
    """
    Для каждого теста создает все таблицы в чистой БД в памяти.
    После теста удаляет все таблицы.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
async def db_session(setup_database, test_engine):
    """
    Создает и предоставляет сессию для взаимодействия с тестовой БД в рамках одного теста.
    Гарантирует, что сессия будет закрыта после выполнения теста.
    """
    async_session_factory = async_sessionmaker(test_engine, expire_on_commit=False)
    async with async_session_factory() as session:
        yield session