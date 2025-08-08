

import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import Message
from loguru import logger

# --- Configuration ---
load_dotenv()
BOT_TOKEN = os.getenv("SUPPORT_BOT_TOKEN")
SUPPORT_CHAT_ID = os.getenv("SUPPORT_CHAT_ID")

if not BOT_TOKEN or not SUPPORT_CHAT_ID:
    raise ValueError("SUPPORT_BOT_TOKEN and SUPPORT_CHAT_ID must be set in the .env file")

try:
    SUPPORT_CHAT_ID = int(SUPPORT_CHAT_ID)
except ValueError:
    raise ValueError("SUPPORT_CHAT_ID must be a valid integer")

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()

# --- Text Messages ---
WELCOME_MESSAGE = """
Здравствуйте! 
Это бот технической поддержки.

Опишите вашу проблему одним сообщением. Пожалуйста, приложите скриншоты, если это возможно.
Ваше сообщение будет передано первому освободившемуся оператору.
"""

# --- Handlers ---

@dp.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    """Handles the /start command."""
    await message.answer(WELCOME_MESSAGE)

@dp.message(F.chat.type == "private")
async def handle_private_message(message: Message):
    """Handles messages sent by users to the bot."""
    logger.info(f"User {message.from_user.id} sent a message. Forwarding to support chat.")
    
    # Forward the user's message to the support chat
    await bot.forward_message(
        chat_id=SUPPORT_CHAT_ID,
        from_chat_id=message.chat.id,
        message_id=message.message_id
    )
    
    # Add a caption with user info to the forwarded message
    await bot.send_message(
        chat_id=SUPPORT_CHAT_ID,
        text=f"☝️ Новое обращение от:\nUser ID: <code>{message.from_user.id}</code>\nUsername: @{message.from_user.username or 'N/A'}"
    )
    
    await message.answer("Спасибо! Ваше сообщение передано оператору. Ожидайте ответа.")

@dp.message(F.chat.id == SUPPORT_CHAT_ID, F.reply_to_message)
async def handle_support_reply(message: Message):
    """Handles replies from support operators in the support chat."""
    
    # Check if the message is a reply to a forwarded message
    if not message.reply_to_message.forward_from:
        return

    user_id = message.reply_to_message.forward_from.id
    logger.info(f"Operator {message.from_user.id} is replying to user {user_id}.")

    try:
        # Send the operator's reply to the user
        await bot.copy_message(
            chat_id=user_id,
            from_chat_id=SUPPORT_CHAT_ID,
            message_id=message.message_id
        )
        logger.info(f"Successfully sent reply to user {user_id}.")
    except Exception as e:
        logger.error(f"Failed to send message to user {user_id}. Error: {e}")
        await message.reply(f"Не удалось отправить сообщение пользователю {user_id}. Ошибка: {e}")


# --- Main Function ---
async def main() -> None:
    logger.add("support_bot.log", rotation="1 week", retention="1 month")
    logger.info("Starting support bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

