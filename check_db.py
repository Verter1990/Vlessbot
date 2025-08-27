
import asyncio
from sqlalchemy import select
from core.database.database import async_session_maker, init_db
from core.database.models import Server
from loguru import logger

async def check_servers():
    logger.info("Attempting to connect to DB and fetch servers...")
    try:
        await init_db() # Ensure tables are created if not already
        async with async_session_maker() as session:
            stmt = select(Server)
            servers = (await session.execute(stmt)).scalars().all()
            if servers:
                logger.info("Servers found in DB:")
                for server in servers:
                    logger.info(f"  ID: {server.id}, Name: {server.name}, Active: {server.is_active}, API URL: {server.api_url}")
            else:
                logger.warning("No servers found in the database.")
    except Exception as e:
        logger.error(f"Error connecting to DB or fetching servers: {e}")

if __name__ == "__main__":
    asyncio.run(check_servers())
