import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from core.database.models import User, Base
from loguru import logger

TEST_DATABASE_URL = "postgresql+asyncpg://vlessbot_user:vlessbot_password@db/vlessbot_db"

async def get_user_language(user_id: int):
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        user = (await session.execute(select(User).where(User.telegram_id == user_id))).scalars().first()
        if user:
            logger.info(f"User {user_id} language_code in DB: {user.language_code}")
            return user.language_code
        else:
            logger.info(f"User {user_id} not found in DB.")
            return None

    await engine.dispose()

if __name__ == "__main__":
    logger.add("test_lang_switch.log", rotation="1 week", retention="1 month", level="DEBUG")
    asyncio.run(get_user_language(218265585))