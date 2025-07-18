import asyncio
from aiogram import Bot, Dispatcher
from fastapi import FastAPI, Request, APIRouter
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger
import uvicorn
from yookassa import Webhook, Payment
from yookassa.domain.notification import WebhookNotification
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


from core.config import settings
from core.handlers import user_handlers, admin_handlers, info_handlers
from core.database.database import init_db, async_session_maker
from core.database.models import User, Tariff, Server, Transaction, GiftCode
from core.middlewares.db_middleware import DbSessionMiddleware
from core.services.scheduler_jobs import check_expiring_subscriptions, deactivate_expired_users
from core.handlers.user_handlers import _create_or_update_vpn_key, _get_user_and_lang, generate_unique_code
from core.locales.translations import get_text, get_db_text


# Инициализация бота и диспетчера
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand

bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()
dp.include_router(user_handlers.router)
dp.include_router(admin_handlers.router)
dp.include_router(info_handlers.router)
dp.update.middleware(DbSessionMiddleware(session_maker=async_session_maker))

# Инициализация FastAPI приложения
app = FastAPI()
webhook_router = APIRouter()

# Инициализация планировщика
scheduler = AsyncIOScheduler(timezone="UTC")

async def process_successful_payment(session: AsyncSession, bot: Bot, transaction: Transaction):
    user = (await session.execute(select(User).where(User.telegram_id == transaction.user_id))).scalars().first()
    tariff = await session.get(Tariff, transaction.tariff_id)
    _, lang = await _get_user_and_lang(session, user.telegram_id)

    if not all([user, tariff]):
        logger.error(f"[YooKassa Webhook] User or Tariff not found for transaction {transaction.id}")
        return

    payment_details = transaction.payment_details or {}
    payment_type = payment_details.get('payment_type', 'subscription') # Default to subscription

    if payment_type == 'subscription':
        server_id = payment_details.get('server_id')
        if server_id:
            server = await session.get(Server, server_id)
            if not server:
                logger.error(f"[YooKassa Webhook] Server {server_id} not found for transaction {transaction.id}")
                user.unassigned_days += tariff.duration_days
                await bot.send_message(user.telegram_id, get_text('payment_success_days_added_server_fail', lang).format(days=tariff.duration_days))
            else:
                try:
                    vless_link = await _create_or_update_vpn_key(session, user, server, tariff.duration_days, lang)
                    await bot.send_message(user.telegram_id, get_text('payment_success_key_created', lang).format(
                        server_name=get_db_text(server.name, lang),
                        vless_link=vless_link,
                        days=tariff.duration_days
                    ), parse_mode='HTML')
                except Exception as e:
                    logger.error(f"[YooKassa Webhook] Error creating VPN key for transaction {transaction.id}: {e}", exc_info=True)
                    user.unassigned_days += tariff.duration_days
                    await bot.send_message(user.telegram_id, get_text('payment_success_key_error_webhook', lang).format(days=tariff.duration_days))
        else:
            user.unassigned_days += tariff.duration_days
            await bot.send_message(user.telegram_id, get_text('payment_success_days_added', lang).format(days=tariff.duration_days))

    elif payment_type == 'gift':
        gift_code_str = generate_unique_code()
        new_gift = GiftCode(code=gift_code_str, tariff_id=tariff.id, buyer_user_id=user.telegram_id)
        session.add(new_gift)
        
        bot_user = await bot.get_me()
        gift_link = f"https://t.me/{bot_user.username}?start=G_{gift_code_str}"
        await bot.send_message(
            chat_id=user.telegram_id,
            text=get_text('gift_purchase_success', lang).format(
                tariff_name=get_db_text(tariff.name, lang),
                gift_link=gift_link
            )
        )
        logger.info(f"[YooKassa Webhook] User {user.telegram_id} purchased a gift subscription. Code: {gift_code_str}")

    transaction.status = 'succeeded'
    await session.commit()
    logger.info(f"[YooKassa Webhook] Transaction {transaction.id} processed successfully.")


@webhook_router.post("/webhooks/yookassa")
async def yookassa_webhook(request: Request):
    payload = await request.json()
    logger.info(f"Received YooKassa webhook: {payload}")

    try:
        notification_object = WebhookNotification(payload)
        payment_id = notification_object.object.id
        
        async with async_session_maker() as session:
            transaction = await session.get(Transaction, payment_id)
            if not transaction:
                logger.warning(f"Transaction with id {payment_id} not found in DB.")
                return {"status": "ok"} # Respond 200 to avoid retries

            if notification_object.event == 'payment.succeeded':
                if transaction.status != 'succeeded':
                    await process_successful_payment(session, bot, transaction)
                else:
                    logger.info(f"Transaction {payment_id} already processed.")
            
            elif notification_object.event == 'payment.canceled':
                transaction.status = 'canceled'
                await session.commit()
                logger.info(f"Transaction {payment_id} was canceled.")

        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error processing YooKassa webhook: {e}", exc_info=True)
        return {"status": "error"}

app.include_router(webhook_router)


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
