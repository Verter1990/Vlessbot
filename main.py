import asyncio
from aiogram import Bot, Dispatcher
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger
import uvicorn

from core.config import settings
from core.handlers import user_handlers, admin_handlers
from core.database.database import init_db, async_session_maker
from core.middlewares.db_middleware import DbSessionMiddleware
from core.services.scheduler_jobs import check_expiring_subscriptions, deactivate_expired_users

# Инициализация бота и диспетчера
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand

bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()
dp.include_router(user_handlers.router)
dp.include_router(admin_handlers.router)
dp.update.middleware(DbSessionMiddleware(session_maker=async_session_maker))

# Инициализация FastAPI приложения
app = FastAPI()

# Инициализация планировщика
scheduler = AsyncIOScheduler(timezone="UTC")

@app.on_event("startup")
async def startup_event():
    logger.info("FastAPI application started!")
    await init_db()
    
    # Добавляем задачи в планировщик
    # Передаем session_maker в задачи, чтобы они могли создавать свои сессии
    scheduler.add_job(check_expiring_subscriptions, 'cron', hour=9, minute=0, args=(bot, async_session_maker()))
    scheduler.add_job(deactivate_expired_users, 'cron', hour=0, minute=5, args=(async_session_maker(),))
    scheduler.start()
    logger.info("Scheduler started.")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("FastAPI application stopped!")
    scheduler.shutdown()
    await bot.session.close()

async def start_bot_polling():
    logger.info("Starting Telegram bot polling...")
    commands = [
        BotCommand(command="start", description="Перезапустить бота"),
        BotCommand(command="setlanguage", description="Сменить язык / Change language"),
    ]
    await bot.set_my_commands(commands)
    await dp.start_polling(bot, skip_updates=True)

async def main():
    # Запуск FastAPI сервера
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    fastapi_task = asyncio.create_task(server.serve())

    # Запуск бота
    bot_task = asyncio.create_task(start_bot_polling())

    await asyncio.gather(fastapi_task, bot_task)

if __name__ == "__main__":
    logger.add("bot.log", rotation="1 week", retention="1 month") # Настройка логирования
    asyncio.run(main())
