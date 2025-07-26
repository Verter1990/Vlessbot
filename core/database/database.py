from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from core.config import settings
from core.database.models import Base # Import Base from models.py

DATABASE_URL = settings.DB_URL

import logging

async_engine = create_async_engine(DATABASE_URL, echo=True)

# Enable detailed SQL logging for debugging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
async_session_maker = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)