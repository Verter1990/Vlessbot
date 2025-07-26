import asyncio
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand
from loguru import logger

from core.config import settings
from core.handlers import user_handlers, admin_handlers, info_handlers
from core.middlewares.db_middleware import DbSessionMiddleware
from core.database.database import init_db, async_session_maker

async def main():
    # Настройка логирования
    logger.remove()
    logger.add(sys.stderr, level="INFO")
    logger.add("bot.log", rotation="1 week", retention="1 month", level="DEBUG")

    logger.info("Initializing bot...")

    # Инициализация базы данных
    await init_db()

    # Инициализация бота и диспетчера
    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()

    # Подключение middleware
    dp.update.middleware(DbSessionMiddleware(session_maker=async_session_maker))

    # Подключение роутеров
    dp.include_router(user_handlers.router)
    dp.include_router(admin_handlers.router)
    dp.include_router(info_handlers.router)

    # Установка команд бота
    commands = [
        BotCommand(command="start", description="Перезапустить бота"),
        BotCommand(command="setlanguage", description="Сменить язык / Change language"),
    ]
    await bot.set_my_commands(commands)

    logger.info("Starting bot polling...")
    # Запуск поллинга
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())