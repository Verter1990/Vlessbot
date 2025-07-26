import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from core.database.models import User, Base
from loguru import logger

TEST_DATABASE_URL = "postgresql+asyncpg://vlessbot_user:vlessbot_password@db/vlessbot_db"

async def update_user_language(user_id: int, new_lang_code: str):
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        user = (await session.execute(select(User).where(User.telegram_id == user_id))).scalars().first()

        if user:
            logger.info(f"Updating user {user_id} language from {user.language_code} to {new_lang_code}")
            user.language_code = new_lang_code
            await session.commit()
            logger.info(f"User {user_id} language updated successfully to {user.language_code}")
        else:
            logger.info(f"User {user_id} not found. Creating new user with language {new_lang_code}")
            new_user = User(
                telegram_id=user_id,
                username=f"test_user_{user_id}", # Placeholder username
                language_code=new_lang_code,
                unassigned_days=0,
                referral_balance=0,
                l2_referral_balance=0,
                trial_used=False,
                activated_first_vpn=False,
                bonus_days=0,
                total_paid_out=0
            )
            session.add(new_user)
            await session.commit()
            logger.info(f"New user {user_id} created with language {new_user.language_code}")

    await engine.dispose()

if __name__ == "__main__":
    logger.add("update_user_lang.log", rotation="1 week", retention="1 month", level="DEBUG")
    asyncio.run(update_user_language(218265585, "fa"))
