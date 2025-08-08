
import asyncio
from sqlalchemy import select
from loguru import logger

from core.database.database import async_session_maker
from core.database.models import User

# --- Configuration ---
TELEGRAM_ID_TO_DELETE = 218265585
# -------------------

async def delete_user():
    logger.info(f"Attempting to delete user with telegram_id {TELEGRAM_ID_TO_DELETE}")
    async with async_session_maker() as session:
        try:
            stmt = select(User).where(User.telegram_id == TELEGRAM_ID_TO_DELETE)
            user = (await session.execute(stmt)).scalars().first()

            if user:
                logger.info(f"Found user. Deleting...")
                await session.delete(user)
                await session.commit()
                logger.success(f"Successfully deleted user with telegram_id {TELEGRAM_ID_TO_DELETE}")
            else:
                logger.error(f"User with telegram_id {TELEGRAM_ID_TO_DELETE} not found.")
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            await session.rollback()

if __name__ == "__main__":
    asyncio.run(delete_user())
