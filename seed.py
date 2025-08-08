import asyncio
from core.database.database import init_db, async_session_maker, async_engine
from core.database.models import Server, Tariff
from core.utils.security import encrypt_password
from sqlalchemy import select
from loguru import logger

async def wait_for_db():
    MAX_RETRIES = 10
    RETRY_DELAY = 3 # seconds
    for i in range(MAX_RETRIES):
        try:
            logger.info(f"Attempt {i+1}/{MAX_RETRIES}: Connecting to database...")
            async with async_engine.connect() as conn:
                await conn.execute(select(1))
            logger.info("Database connection successful!")
            return
        except Exception as e:
            logger.warning(f"Database connection failed: {e}. Retrying in {RETRY_DELAY} seconds...")
            await asyncio.sleep(RETRY_DELAY)
    logger.error("Failed to connect to database after multiple retries.")
    raise ConnectionError("Could not connect to database.")

async def seed_db():
    logger.info("Initializing database and seeding default data...")
    await wait_for_db()
    await init_db() # Ensure tables are created if not already

    async with async_session_maker() as session:
        # Seed Servers
        stmt = select(Server)
        existing_servers = (await session.execute(stmt)).scalars().all()

        if not existing_servers:
            logger.info("No servers found. Adding default servers.")
            default_server = Server(
                name="Нидерланды",
                api_url="https://vpn.myvless.fun:2053/",
                api_user="admin",
                api_password=encrypt_password("9M1u3vX4tp7upPXE"),
                inbound_id=2,
                is_active=True
            )
            session.add(default_server)
            await session.commit()
            logger.info("Default server 'Нидерланды' added.")
        else:
            logger.info("Servers already exist. Skipping default server addition.")
            for server in existing_servers:
                logger.info(f"  ID: {server.id}, Name: {server.name}, Active: {server.is_active}")

        # Seed Tariffs
        stmt = select(Tariff)
        existing_tariffs = (await session.execute(stmt)).scalars().all()

        if not existing_tariffs:
            logger.info("No tariffs found. Adding default tariffs.")
            tariffs_to_add = [
                Tariff(name={"ru": "Неделя", "en": "Week"}, duration_days=7, price_rub=3000, price_stars=20),
                Tariff(name={"ru": "Месяц", "en": "Month"}, duration_days=30, price_rub=9900, price_stars=66),
                Tariff(name={"ru": "Год", "en": "Year"}, duration_days=365, price_rub=100000, price_stars=666) # Assuming 1000 rub for year
            ]
            session.add_all(tariffs_to_add)
            await session.commit()
            logger.info("Default tariffs added.")
        else:
            logger.info("Tariffs already exist. Skipping default tariff addition.")
            for tariff in existing_tariffs:
                logger.info(f"  ID: {tariff.id}, Name: {tariff.name}, Price RUB: {tariff.price_rub}, Price Stars: {tariff.price_stars}")

if __name__ == "__main__":
    asyncio.run(seed_db())