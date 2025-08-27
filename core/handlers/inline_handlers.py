from aiogram import Router, Bot
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from core.handlers.user_handlers import _get_user_and_lang
from core.locales.translations import get_text

router = Router()

@router.inline_query()
async def inline_query_handler(inline_query: InlineQuery, bot: Bot, session: AsyncSession):
    logger.info("--- INLINE QUERY HANDLER START ---")
    try:
        query_text = inline_query.query
        user_id = inline_query.from_user.id
        logger.info(f"Received inline query from {user_id} with query: '{query_text}'")

        if not query_text or not query_text.startswith("R_"):
            logger.warning("Query is empty or does not start with 'R_'. Answering with empty list.")
            await inline_query.answer([], cache_time=1)
            logger.info("--- INLINE QUERY HANDLER END (EARLY EXIT) ---")
            return

        logger.info("Fetching user and language...")
        user, lang = await _get_user_and_lang(session, user_id)
        if not user:
            logger.warning(f"User {user_id} not found in DB. Offering to start the bot.")
            title = "Отправить приглашение"
            await inline_query.answer([], cache_time=1, switch_pm_text=title, switch_pm_parameter="start")
            logger.info("--- INLINE QUERY HANDLER END (USER NOT FOUND) ---")
            return
        logger.info(f"User found. Language is '{lang}'.")

        logger.info("Getting bot info...")
        bot_user = await bot.get_me()
        ref_link = f"https://t.me/{bot_user.username}?start={query_text}"
        logger.info(f"Generated referral link: {ref_link}")

        logger.info("Fetching text for the invitation message...")
        message_text = get_text('ref_inline_invite_text', lang).format(ref_link=ref_link)
        logger.info(f"Invitation message text: '{message_text}'")

        logger.info("Creating InlineQueryResultArticle...")
        result = InlineQueryResultArticle(
            id=str(uuid.uuid4()),
            title=get_text('btn_create_invitation', lang),
            input_message_content=InputTextMessageContent(
                message_text=message_text,
                disable_web_page_preview=False
            ),
            description=get_text('ref_inline_invite_text', lang).format(ref_link=ref_link)
        )
        logger.info("Article created. Answering inline query...")
        
        await inline_query.answer([result], cache_time=1, is_personal=True)
        logger.info("--- INLINE QUERY HANDLER END (SUCCESS) ---")

    except Exception as e:
        logger.error(f"--- INLINE QUERY HANDLER FAILED ---")
        logger.error(f"Error handling inline query for user {inline_query.from_user.id}: {e}", exc_info=True)
