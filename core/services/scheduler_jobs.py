# core/services/scheduler_jobs.py

from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger
from datetime import datetime, timedelta

from core.database.models import Subscription, User, Server, Tariff
from core.services.xui_client import get_client, XUIClientError

async def check_expiring_subscriptions(bot: Bot, session: AsyncSession):
    logger.info("Scheduler job: Checking for expiring subscriptions...")
    three_days_from_now = datetime.utcnow() + timedelta(days=3)

    stmt = select(Subscription).where(
        Subscription.is_active == True,
        Subscription.expires_at >= datetime.utcnow() + timedelta(days=2, hours=23),
        Subscription.expires_at < three_days_from_now
    )
    result = await session.execute(stmt)
    expiring_subscriptions = await (await result.scalars()).all()

    logger.info(f"Found {len(expiring_subscriptions)} subscriptions expiring soon.")

    for sub in expiring_subscriptions:
        user = await session.get(User, sub.user_id)
        server = await session.get(Server, sub.server_id)
        if user and server:
            try:
                # TODO: Add a renewal button
                await bot.send_message(
                    chat_id=user.telegram_id,
                    text=f"Здравствуйте, {user.username or 'пользователь'}!\n\n"
                         f"Ваша подписка на сервер \"{server.name}\" истекает через 3 дня.\n\n"
                         f"Чтобы продлить ее и не потерять доступ, пожалуйста, оплатите подписку."
                )
                logger.info(f"Sent renewal reminder to user {user.telegram_id} for server {server.name}")
            except Exception as e:
                logger.error(f"Failed to send renewal reminder to {user.telegram_id}: {e}")

async def deactivate_expired_users(session: AsyncSession):
    logger.info("Scheduler job: Deactivating expired users...")
    now = datetime.utcnow()

    stmt = select(Subscription).where(
        Subscription.is_active == True,
        Subscription.expires_at < now
    )
    result = await session.execute(stmt)
    expired_subscriptions = await (await result.scalars()).all()

    logger.info(f"Found {len(expired_subscriptions)} expired subscriptions to deactivate.")

    for sub in expired_subscriptions:
        user = await session.get(User, sub.user_id)
        server = await session.get(Server, sub.server_id)
        if not (user and server):
            continue

        try:
            logger.info(f"Deactivating client {sub.xui_user_uuid} on server {server.name} for user {user.telegram_id}")
            xui_client = get_client(server)
            await xui_client.delete_user(server.inbound_id, sub.xui_user_uuid)
            sub.is_active = False
            # We don't notify the user upon deactivation to avoid being spammy
            # They will find out when they try to use the VPN or check the bot
            logger.info(f"Successfully deactivated user {user.telegram_id} from server {server.name}")
        except XUIClientError as e:
            if "Client not found" in str(e): # Handle cases where client is already deleted in X-UI
                sub.is_active = False
                logger.warning(f"Client {sub.xui_user_uuid} was already deleted in X-UI. Marking as inactive in DB.")
            else:
                logger.error(f"XUI error deactivating {user.telegram_id} from server {server.name}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error deactivating {user.telegram_id} from server {server.name}: {e}")
    
    await session.commit()
