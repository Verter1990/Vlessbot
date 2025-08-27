import asyncio
from core.database.database import init_db, async_session_maker
from core.database.models import Server, Tariff
from core.utils.security import encrypt_password
from sqlalchemy import select
from loguru import logger
from core.config import settings

async def seed_db():
    logger.info("Initializing database and seeding default data...")
    # init_db will create tables if they don't exist.
    await init_db()

    async with async_session_maker() as session:
        # Seed Servers
        stmt = select(Server)
        existing_servers = (await session.execute(stmt)).scalars().all()

        if not existing_servers:
            logger.info("No servers found. Adding default servers.")
            
            # Check if essential XUI settings are present
            if not all([settings.XUI_API_URL, settings.XUI_API_USER, settings.XUI_API_PASSWORD]):
                logger.error("XUI_API_URL, XUI_API_USER, and XUI_API_PASSWORD must be set in the .env file.")
                return

            default_server = Server(
                name="Нидерланды", # You can change this default name
                api_url=settings.XUI_API_URL,
                api_user=settings.XUI_API_USER,
                api_password=encrypt_password(settings.XUI_API_PASSWORD),
                inbound_id=2, # Make sure this inbound ID is correct for your setup
                is_active=True
            )
            session.add(default_server)
            await session.commit()
            logger.info("Default server 'Нидерланды' added using settings from .env file.")
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