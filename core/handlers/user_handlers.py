import loguru
from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, LabeledPrice, PreCheckoutQuery, SuccessfulPayment, User as AiogramUser
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from yookassa import Configuration, Payment
from core.database.models import Server, Subscription, User, Tariff, GiftCode, Transaction
from core.services.xui_client import get_client, XUIClientError
from core.config import settings
import uuid
import secrets
import string
from datetime import datetime, timedelta
from urllib.parse import urlparse
from core import constants
from core.locales.translations import get_text, get_db_text

router = Router()

# --- UTILITY FUNCTIONS ---

def generate_unique_code(length=constants.GIFT_CODE_LENGTH):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(length))

async def _get_user_and_lang(session: AsyncSession, user_id: int) -> tuple[User | None, str]:
    """Fetches user from DB and determines their language code."""
    user = (await session.execute(select(User).where(User.telegram_id == user_id))).scalars().first()
    # Ensure lang is always a valid string, defaulting to 'ru'
    lang = 'ru' # Default language
    if user and user.language_code:
        lang = user.language_code
    return user, lang

async def _generate_vless_link(server: Server, user_uuid: str, lang: str) -> str:
    """Generates a VLESS link for a given server and user UUID."""
    try:
        xui_client = get_client(server)
        inbound = await xui_client.get_inbound(server.inbound_id)
        if not inbound:
            raise XUIClientError("Inbound not found for link generation")

        settings_data = inbound.get("settings", {})
        params_list = []
        if "security" in settings_data:
            params_list.append(f"security={settings_data['security']}")
        if "encryption" in settings_data:
            params_list.append(f"encryption={settings_data['encryption']}")
        if "type" in settings_data:
            params_list.append(f"type={settings_data['type']}")
        params = "&".join(params_list) if params_list else "security=tls&encryption=none&type=tcp"

        parsed_url = urlparse(server.api_url)
        host = parsed_url.hostname
        port = parsed_url.port or 443
        # Use server.name JSON field directly for localized server name
        server_name_localized = server.name.get(lang) or server.name.get('ru') or ''
        vless_link = f"vless://{user_uuid}@{host}:{port}?{params}#VPN_{server_name_localized}"
        
        return vless_link
    except XUIClientError as e:
        logger.error(f"Could not generate VLESS link for UUID {user_uuid} on server {server.name}: {e}")
        raise

async def _create_or_update_vpn_key(session: AsyncSession, user: User, server: Server, days: int, lang: str):
    logger.info(f"Creating/updating VPN key for user {user.telegram_id} on server {server.name} for {days} days.")
    
    existing_subscription = (await session.execute(
        select(Subscription).where(Subscription.user_id == user.telegram_id, Subscription.server_id == server.id)
    )).scalars().first()

    user_uuid = None
    expire_time = datetime.utcnow() + timedelta(days=days)
    expire_time_ms = int(expire_time.timestamp() * 1000)

    try:
        xui_client = get_client(server)
        if existing_subscription:
            user_uuid = existing_subscription.xui_user_uuid
            logger.info(f"Updating existing client {user_uuid} on XUI for user {user.telegram_id}")
            await xui_client.update_client(server.inbound_id, user_uuid, expire_time_ms)
            existing_subscription.expires_at = expire_time
            existing_subscription.is_active = True
        else:
            user_uuid = str(uuid.uuid4())
            logger.info(f"Creating new client {user_uuid} on XUI for user {user.telegram_id}")
            await xui_client.create_user(
                inbound_id=server.inbound_id,
                uuid=user_uuid,
                email=str(user.telegram_id),
                expire_time_ms=expire_time_ms,
                telegram_id=str(user.telegram_id)
            )
            new_subscription = Subscription(
                user_id=user.telegram_id,
                server_id=server.id,
                xui_user_uuid=user_uuid,
                expires_at=expire_time,
                is_active=True
            )
            session.add(new_subscription)
            
            if user.referrer_id and not user.activated_first_vpn:
                logger.info(f"User {user.telegram_id} is a referral and activated first VPN. Awarding bonus to referrer.")
                referrer_stmt = select(User).where(User.telegram_id == user.referrer_id)
                referrer = (await session.execute(referrer_stmt)).scalars().first()
                if referrer:
                    referrer.bonus_days += constants.REFERRAL_ACTIVATION_BONUS_DAYS
                    user.activated_first_vpn = True
                    logger.info(f"Awarded {constants.REFERRAL_ACTIVATION_BONUS_DAYS} bonus days to referrer {referrer.telegram_id}.")
                else:
                    logger.warning(f"Referrer with ID {user.referrer_id} not found for user {user.telegram_id}.")

        await session.commit()
        logger.info(f"Subscription for user {user.telegram_id} on server {server.name} created/updated in DB.")

        vless_link = await _generate_vless_link(server, user_uuid, lang)

        # Формируем сообщение с ключом и кнопкой помощи
        message_text = get_text('key_created_or_updated', lang).format(
            server_name=get_db_text(server.name, lang),
            vless_link=vless_link,
            expires_at=expire_time.strftime("%d.%m.%Y")
        )
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text('btn_how_to_connect', lang), callback_data="how_to_connect")]
        ])

        # Отправляем сообщение
        await bot.send_message(user.telegram_id, message_text, reply_markup=keyboard, parse_mode='HTML')

        return vless_link

    except XUIClientError as e:
        logger.error(f"XUIClientError while creating/updating key for user {user.telegram_id}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while creating/updating key for user {user.telegram_id}: {e}")
        raise

async def _get_main_menu_content(user: User, from_user: AiogramUser, session: AsyncSession) -> tuple[str, InlineKeyboardMarkup]:
    """Prepares the text and keyboard for the main menu."""
    import logging
    try:
        lang = user.language_code
        
        welcome_message = get_text('welcome', lang).format(full_name=from_user.full_name)

        now = datetime.utcnow()
        active_subscriptions = (await session.execute(
            select(Subscription).where(Subscription.user_id == user.telegram_id, Subscription.expires_at > now, Subscription.is_active == True)
        )).scalars().all()

        if active_subscriptions:
            latest_expiry = max([sub.expires_at for sub in active_subscriptions])
            welcome_message += get_text('subscription_active_until', lang).format(expiry_date=latest_expiry.strftime('%Y-%m-%d %H:%M'))
        else:
            welcome_message += get_text('no_active_subscription', lang)

        if user.unassigned_days > 0:
            welcome_message += get_text('unassigned_days', lang).format(days=user.unassigned_days)
        
        total_referrals = (await session.execute(select(func.count(User.id)).where(User.referrer_id == user.telegram_id))).scalar_one()
        total_earnings = (user.referral_balance + user.l2_referral_balance) / 100
        
        if total_referrals > 0:
            welcome_message += get_text('referral_stats', lang).format(referrals=total_referrals, earnings=total_earnings)

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text('btn_setup_vpn', lang), callback_data="setup_vpn")],
            [InlineKeyboardButton(text=get_text('btn_pay_subscription', lang), callback_data="pay_subscription_main_menu")],
            [InlineKeyboardButton(text=get_text('btn_how_to_connect', lang), callback_data="how_to_connect")],
            [InlineKeyboardButton(text=get_text('btn_referral_program', lang), callback_data="referral_program")],
            [InlineKeyboardButton(text=get_text('btn_why_vpn', lang), callback_data="why_vpn")],
            [InlineKeyboardButton(text=get_text('btn_get_free_vpn', lang), callback_data="get_free_vpn")],
            [InlineKeyboardButton(text=get_text('btn_help', lang), callback_data="help")],
            [InlineKeyboardButton(text=get_text('btn_terms_of_use', lang), callback_data="terms_of_use")]
        ])
    except Exception as e:
        logging.error(f"Error generating main menu content for user {user.telegram_id}: {e}", exc_info=True)
        welcome_message = get_text('error_generic', lang)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    return welcome_message, keyboard

# --- COMMAND HANDLERS ---

@router.message(Command("start"))
async def command_start_handler(message: Message, command: CommandObject, session: AsyncSession, bot: Bot) -> None:
    logger.info(f"User {message.from_user.id} sent /start with args: {command.args}")
    
    args = command.args
    user_id = message.from_user.id
    
    user, lang = await _get_user_and_lang(session, user_id)
    if not user:
        logger.info(f"User {user_id} not found in DB, adding new user.")
        user = User(
            telegram_id=user_id,
            username=message.from_user.username,
            language_code=message.from_user.language_code or 'ru', # Fallback to 'ru'
            unassigned_days=0,
            referral_balance=0,
            l2_referral_balance=0
        )
        session.add(user)
        await session.commit()
        await session.refresh(user) # Load default values from the DB
        logger.info(f"New user {user_id} added to the database with lang_code: {user.language_code}")
        lang = user.language_code

        # Send new welcome message for new users
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text('btn_start_bot', lang), callback_data="show_main_menu_after_welcome")]
        ])
        await message.answer(get_text('welcome_new_user', lang), reply_markup=keyboard)
        return # Exit here for new users, they will click the button to proceed

    if args:
        if args.startswith("R_"):
            if not user.referrer_id:
                referral_code = args.split("R_")[1]
                logger.info(f"User {user_id} joined with referral code: {referral_code}")
                referrer = (await session.execute(select(User).where(User.referral_code == referral_code))).scalars().first()
                if referrer and referrer.telegram_id != user_id:
                    user.referrer_id = referrer.telegram_id
                    user.referral_balance = constants.REFERRAL_BONUS_RUPEES * 100
                    await message.answer(get_text('referral_bonus_applied', lang))
                    logger.info(f"User {user_id} is now a referral of {referrer.telegram_id}. Awarded {constants.REFERRAL_BONUS_RUPEES} RUB bonus.")
                else:
                    logger.warning(constants.MSG_REFERRAL_CODE_NOT_FOUND.format(code=referral_code, user_id=user_id))
        
        elif args.startswith("G_"):
            gift_code_str = args.split("G_")[1]
            logger.info(f"User {user_id} trying to activate gift code: {gift_code_str}")
            gift_code = (await session.execute(select(GiftCode).where(GiftCode.code == gift_code_str, GiftCode.is_activated == False))).scalars().first()
            if gift_code:
                tariff = await session.get(Tariff, gift_code.tariff_id)
                if tariff:
                    user.unassigned_days += tariff.duration_days
                    gift_code.is_activated = True
                    gift_code.activated_by_user_id = user_id
                    gift_code.activated_at = datetime.utcnow()
                    await message.answer(get_text('gift_activated', lang).format(days=tariff.duration_days))
                    logger.info(f"Gift code {gift_code_str} activated by user {user_id}.")
                else:
                    await message.answer(get_text('gift_activation_error', lang))
                    logger.warning(f"Gift code {gift_code_str} activated by user {user_id}, but tariff {gift_code.tariff_id} not found.")
            else:
                await message.answer(get_text('gift_not_found_or_used', lang))
                logger.warning(f"User {user_id} failed to activate gift code {gift_code_str}.")

    await session.commit()

    text, keyboard = await _get_main_menu_content(user, message.from_user, session)
    logger.debug(f"Sending message text: {text}")
    await message.answer(text, reply_markup=keyboard)

@router.message(Command("ref"))
@router.callback_query(F.data == "referral_program")
async def referral_program_handler(message: Message | CallbackQuery, session: AsyncSession, bot: Bot):
    if isinstance(message, CallbackQuery):
        await message.answer()
        user_id = message.from_user.id
        user_message = message.message
    else:
        user_id = message.from_user.id
        user_message = message

    user, lang = await _get_user_and_lang(session, user_id)
    if not user:
        await user_message.answer(get_text('user_not_found_error', 'ru'))
        return

    if not user.referral_code:
        user.referral_code = generate_unique_code()
        await session.commit()

    l1_referrals = (await session.execute(select(User).where(User.referrer_id == user.telegram_id).order_by(User.created_at.desc()).limit(10))).scalars().all()
    total_l1_referrals = (await session.execute(select(func.count(User.id)).where(User.referrer_id == user.telegram_id))).scalar_one()
    not_activated_referrals = (await session.execute(select(User).where(User.referrer_id == user.telegram_id, User.activated_first_vpn == False).order_by(User.created_at.desc()).limit(10))).scalars().all()

    text_parts = [
        get_text('ref_program_title', lang),
        get_text('ref_program_conditions', lang),
        get_text('ref_program_withdrawal', lang),
        "",
        get_text('ref_total_referrals', lang).format(count=total_l1_referrals)
    ]

    if l1_referrals:
        last_10_logins = ", ".join([f"@{r.username}" if r.username else f"ID: {r.telegram_id}" for r in l1_referrals])
        text_parts.append(get_text('ref_last_10', lang).format(logins=last_10_logins))
    
    text_parts.append("\n" + get_text('ref_not_activated', lang))
    if not_activated_referrals:
        not_activated_logins = ", ".join([f"@{r.username}" if r.username else f"ID: {r.telegram_id}" for r in not_activated_referrals])
        text_parts.append(get_text('ref_last_10', lang).format(logins=not_activated_logins))
    else:
        text_parts.append(get_text('ref_no_inactive_referrals', lang))

    text_parts.extend([
        "\n" + get_text('ref_activation_info', lang),
        "\n" + get_text('ref_friend_bonus_info', lang),
        ""
    ])

    total_balance = (user.referral_balance + user.l2_referral_balance) / 100
    l2_balance = user.l2_referral_balance / 100
    text_parts.extend([
        get_text('ref_balance_info', lang).format(total_balance=total_balance, l2_balance=l2_balance),
        get_text('ref_bonus_days_info', lang).format(days=user.bonus_days),
        get_text('ref_paid_out_info', lang).format(total_paid_out=user.total_paid_out / 100),
        ""
    ])

    bot_user = await bot.get_me()
    ref_link = f"https://t.me/{bot_user.username}?start=R_{user.referral_code}"
    text_parts.extend([
        get_text('ref_copy_link_info', lang),
        f"<a href=\"{ref_link}\">{ref_link}</a>",
        "",
        get_text('ref_create_invite_info', lang)
    ])

    text = "\n".join(text_parts)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text('btn_gift_subscription', lang), callback_data="gift_subscription")],
        [InlineKeyboardButton(text=get_text('btn_create_invitation', lang), switch_inline_query=f"R_{user.referral_code}")],
        [InlineKeyboardButton(text=get_text('btn_help', lang), callback_data="help")],
        [InlineKeyboardButton(text=get_text('btn_main_menu', lang), callback_data="main_menu")]
    ])

    if isinstance(message, CallbackQuery):
        await user_message.edit_text(text, reply_markup=keyboard, disable_web_page_preview=True)
    else:
        await user_message.answer(text, reply_markup=keyboard, disable_web_page_preview=True)

@router.message(Command("setlanguage"))
async def command_set_language_handler(message: Message, session: AsyncSession):
    user, lang = await _get_user_and_lang(session, message.from_user.id)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Русский 🇷🇺", callback_data="set_lang_ru")],
        [InlineKeyboardButton(text="English 🇬🇧", callback_data="set_lang_en")],
        [InlineKeyboardButton(text="فارسی 🇮🇷", callback_data="set_lang_fa")]
    ])
    await message.answer(get_text('select_language', lang), reply_markup=keyboard)

# --- CALLBACK HANDLERS ---

@router.callback_query(F.data == "main_menu")
async def callback_main_menu(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    await callback.answer()
    user, lang = await _get_user_and_lang(session, callback.from_user.id)
    if not user:
        await callback.message.edit_text(get_text('user_not_found_error', 'ru'))
        return
    
    text, keyboard = await _get_main_menu_content(user, callback.from_user, session)
    await callback.message.edit_text(text, reply_markup=keyboard)

@router.callback_query(F.data == "show_main_menu_after_welcome")
async def callback_show_main_menu_after_welcome(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    await callback.answer()
    user, lang = await _get_user_and_lang(session, callback.from_user.id)
    if not user:
        await callback.message.edit_text(get_text('user_not_found_error', 'ru'))
        return
    
    text, keyboard = await _get_main_menu_content(user, callback.from_user, session)
    await callback.message.edit_text(text, reply_markup=keyboard)

@router.callback_query(F.data.startswith("set_lang_"))
async def set_language_callback(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    """
    Handles the language selection callback.
    Updates the user's language in the database and refreshes the main menu.
    """
    try:
        # 1. Extract language code from callback data
        lang_code = callback.data.split("_")[-1]
        user_id = callback.from_user.id
        logger.info(f"Step 1: User {user_id} selected language '{lang_code}'.")

        # 2. Find the user in the database by their telegram_id
        user_query = select(User).where(User.telegram_id == user_id)
        result = await session.execute(user_query)
        user = result.scalars().first()

        if not user:
            logger.warning(f"Step 2: User {user_id} not found in DB. Aborting language change.")
            await callback.answer("Please /start the bot first.", show_alert=True)
            return
        
        logger.info(f"Step 2: Found user {user_id} with current language '{user.language_code}'.")

        # 3. Update user's language and save to DB
        user.language_code = lang_code
        session.add(user)
        await session.commit()
        logger.info(f"Step 3: Successfully committed language '{lang_code}' for user {user_id} to DB.")

        # 4. Inform the user about the successful change in their new language
        language_names = {'ru': 'Русский', 'en': 'English', 'fa': 'فارسی'}
        language_name = language_names.get(lang_code, lang_code)
        
        response_text = get_text('language_changed', lang_code).format(language=language_name)
        logger.info(f"Step 4: Answering callback with text: '{response_text}' in language '{lang_code}'.")
        await callback.answer(text=response_text, show_alert=False)

        # 5. Refresh the main menu with the new language
        await session.refresh(user)
        logger.info(f"Step 5: Refreshed user object. Language is now '{user.language_code}'. Generating main menu.")
        text, keyboard = await _get_main_menu_content(user, callback.from_user, session)
        await callback.message.edit_text(text, reply_markup=keyboard)
        logger.info(f"Step 6: Successfully sent new main menu to user {user_id}.")

    except Exception as e:
        logger.error(f"CRITICAL ERROR in set_language_callback for user {callback.from_user.id}: {e}", exc_info=True)
        await callback.answer("An error occurred. Please try again.", show_alert=True)

@router.callback_query(F.data == "setup_vpn")
async def callback_setup_vpn(callback: CallbackQuery, session: AsyncSession) -> None:
    logger.info(f"User {callback.from_user.id} clicked setup_vpn")
    user, lang = await _get_user_and_lang(session, callback.from_user.id)
    await callback.answer()

    try:
        stmt = select(Server).where(Server.is_active == True)
        result = await session.execute(stmt)
        servers = result.scalars().all()
    except Exception as e:
        logger.error(f"Error querying servers: {e}")
        await callback.message.answer(get_text('error_generic', lang))
        return

    if not servers:
        await callback.message.answer(get_text('no_servers_available', lang))
        return

    buttons = []
    for server in servers:
        server_name_localized = server.name.get(lang) or server.name.get('ru') or ''
        flag_emoji = constants.COUNTRY_EMOJIS.get(server_name_localized, "")
        lock_emoji = constants.UNLOCK_EMOJI if server.is_active else constants.LOCK_EMOJI
        button_text = f"{flag_emoji} {server_name_localized} {lock_emoji}".strip()
        buttons.append([InlineKeyboardButton(text=button_text, callback_data=f"select_server_{server.id}")])
    buttons.append([InlineKeyboardButton(text=get_text('btn_main_menu', lang), callback_data="main_menu")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback.message.edit_text(
        get_text('vpn_setup_instructions', lang).format(support_chat_link=settings.SUPPORT_CHAT_LINK) + "\n\n" + \
        get_text('select_server_for_setup', lang),
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("select_server_"))
async def callback_select_server(callback: CallbackQuery, session: AsyncSession) -> None:
    # Ensure lang is always defined, even if _get_user_and_lang fails
    current_lang = 'ru'
    logger.info(f"User {callback.from_user.id} selected server via callback: {callback.data}")
    await callback.answer()

    server_id = int(callback.data.split("_")[-1])

    user, fetched_lang = await _get_user_and_lang(session, callback.from_user.id)
    if user:
        current_lang = fetched_lang # Update lang if user is found

    selected_server = await session.get(Server, server_id)

    if not user or not selected_server:
        await callback.message.answer(get_text('server_or_user_not_found', current_lang))
        return

    now = datetime.utcnow()
    existing_subscription = (await session.execute(
        select(Subscription).where(
            Subscription.user_id == user.telegram_id,
            Subscription.server_id == selected_server.id,
            Subscription.expires_at > now,
            Subscription.is_active == True
        )
    )).scalars().first()

    if existing_subscription:
        logger.info(f"Active subscription found for user {user.telegram_id} on server {selected_server.name}. Showing key.")
        try:
            vless_link = await _generate_vless_link(selected_server, existing_subscription.xui_user_uuid, current_lang)
            await callback.message.answer(get_text('vpn_key_info', current_lang).format(
                server_name=get_db_text(selected_server.name, current_lang),
                vless_link=vless_link,
                expiry_date=existing_subscription.expires_at.strftime('%Y-%m-%d %H:%M')
            ), parse_mode='HTML')
        except Exception as e:
            logger.error(f"Unexpected error showing subscription: {e}")
            await callback.message.answer(get_text('show_subscription_error', current_lang))
        return

    buttons = []
    if user.unassigned_days > 0:
        buttons.append([InlineKeyboardButton(text=get_text('btn_activate_unassigned_days', current_lang).format(days=user.unassigned_days), callback_data=f"activate_unassigned_days_{selected_server.id}")])
    
    total_referral_balance = user.referral_balance + user.l2_referral_balance
    if total_referral_balance > 0:
        buttons.append([InlineKeyboardButton(text=get_text('btn_pay_from_referral_balance', current_lang).format(balance=total_referral_balance / 100), callback_data=f"pay_with_referral_balance_{selected_server.id}")])
    
    buttons.append([InlineKeyboardButton(text=get_text('btn_select_tariff_for_payment', current_lang), callback_data=f"pay_subscription_for_server_{selected_server.id}")])
    buttons.append([InlineKeyboardButton(text=get_text('btn_main_menu', current_lang), callback_data="main_menu")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback.message.edit_text(
        get_text('no_active_subscription_for_server', current_lang).format(server_name=selected_server.name.get(current_lang) or selected_server.name.get('ru') or ''),
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("pay_with_referral_balance_"))
async def callback_pay_with_referral_balance(callback: CallbackQuery, session: AsyncSession):
    logger.info(f"User {callback.from_user.id} chose to pay with referral balance.")
    await callback.answer()

    server_id = int(callback.data.split("_")[-1])
    user, lang = await _get_user_and_lang(session, callback.from_user.id)

    if not user:
        await callback.message.answer(get_text('user_not_found_error', lang))
        return

    tariffs = (await session.execute(select(Tariff).where(Tariff.is_active == True).order_by(Tariff.duration_days))).scalars().all()
    if not tariffs:
        await callback.message.answer(get_text('no_tariffs_available', lang))
        return

    buttons = []
    total_balance = user.referral_balance + user.l2_referral_balance

    for tariff in tariffs:
        if total_balance >= tariff.price_rub:
            buttons.append([InlineKeyboardButton(text=f"{get_db_text(tariff.name, lang)} ({tariff.duration_days} дней) - {tariff.price_rub / 100:.2f} руб.", callback_data=f"confirm_referral_payment_{tariff.id}_{server_id}")])
    
    if not buttons:
        await callback.message.answer(get_text('referral_payment_insufficient_funds', lang).format(balance=total_balance / 100))
        return

    buttons.append([InlineKeyboardButton(text=get_text('btn_back_to_server_selection', lang), callback_data=f"select_server_{server_id}")])
    buttons.append([InlineKeyboardButton(text=get_text('btn_main_menu', lang), callback_data="main_menu")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text(get_text('referral_balance_menu_title', lang).format(balance=total_balance / 100), reply_markup=keyboard)

@router.callback_query(F.data.startswith("confirm_referral_payment_"))
async def confirm_referral_payment(callback: CallbackQuery, session: AsyncSession):
    logger.info(f"User {callback.from_user.id} confirmed referral payment.")
    await callback.answer()

    parts = callback.data.split("_")
    tariff_id = int(parts[3])
    server_id = int(parts[4])

    user, lang = await _get_user_and_lang(session, callback.from_user.id)
    tariff = await session.get(Tariff, tariff_id)
    selected_server = await session.get(Server, server_id)

    if not all([user, tariff, selected_server]):
        await callback.message.answer(get_text('referral_payment_error', lang))
        return

    total_balance = user.referral_balance + user.l2_referral_balance
    if total_balance < tariff.price_rub and user.telegram_id not in settings.ADMIN_IDS_LIST:
        await callback.message.answer(get_text('referral_payment_insufficient_funds_for_tariff', lang))
        return

    try:
        if user.referral_balance >= tariff.price_rub:
            user.referral_balance -= tariff.price_rub
        else:
            remaining_cost = tariff.price_rub - user.referral_balance
            user.referral_balance = 0
            user.l2_referral_balance -= remaining_cost
        
        vless_link = await _create_or_update_vpn_key(session, user, selected_server, tariff.duration_days, lang)
        await session.commit()

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text('btn_how_to_connect', lang), callback_data="how_to_connect")]
        ])

        await callback.message.answer(
            get_text('referral_payment_success', lang).format(
                tariff_name=get_db_text(tariff.name, lang),
                server_name=selected_server.name.get(lang) or selected_server.name.get('ru') or '',
                vless_link=vless_link,
                days=tariff.duration_days
            ), parse_mode='HTML', reply_markup=keyboard
        )
    except Exception as e:
        logger.error(f"Error activating subscription with referral balance for user {user.telegram_id}: {e}")
        await callback.message.answer(get_text('referral_payment_activation_error', lang))

@router.callback_query(F.data.startswith("activate_unassigned_days_"))
async def activate_unassigned_days(callback: CallbackQuery, session: AsyncSession):
    logger.info(f"User {callback.from_user.id} chose to activate unassigned days.")
    await callback.answer()

    server_id = int(callback.data.split("_")[-1])

    user, lang = await _get_user_and_lang(session, callback.from_user.id)
    selected_server = await session.get(Server, server_id)

    if not user or not selected_server:
        await callback.message.answer(get_text('server_or_user_not_found', lang))
        return

    if user.unassigned_days <= 0 and user.telegram_id not in settings.ADMIN_IDS_LIST:
        await callback.message.answer(get_text('no_unassigned_days', lang))
        return

    try:
        vless_link = await _create_or_update_vpn_key(session, user, selected_server, user.unassigned_days, lang)
        user.unassigned_days = 0
        await session.commit()

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text('btn_how_to_connect', lang), callback_data="how_to_connect")]
        ])

        await callback.message.answer(
            get_text('unassigned_days_activation_success', lang).format(
                server_name=get_db_text(selected_server.name, lang),
                vless_link=vless_link
            ), parse_mode='HTML', reply_markup=keyboard
        )
    except Exception as e:
        logger.error(f"Error activating unassigned days for user {user.telegram_id}: {e}")
        await callback.message.answer(get_text('unassigned_days_activation_error', lang))

@router.callback_query(F.data == "pay_subscription_main_menu")
@router.callback_query(F.data.startswith("pay_subscription_for_server_"))
async def callback_pay_subscription(callback: CallbackQuery, session: AsyncSession):
    logger.info(f"User {callback.from_user.id} clicked pay_subscription")
    await callback.answer()
    
    user, lang = await _get_user_and_lang(session, callback.from_user.id)
    server_id = None
    if callback.data.startswith("pay_subscription_for_server_"):
        server_id = int(callback.data.split("_")[-1])

    try:
        stmt = select(Tariff).where(Tariff.is_active == True).order_by(Tariff.duration_days)
        result = await session.execute(stmt)
        tariffs = result.scalars().all()
    except Exception as e:
        logger.error(f"Error querying tariffs: {e}")
        await callback.message.answer(get_text('error_generic', lang))
        return

    if not tariffs:
        await callback.message.answer(get_text('no_tariffs_available', lang))
        return

    buttons = [[InlineKeyboardButton(text=f"{get_db_text(tariff.name, lang)} - {tariff.price_rub/100}₽ / {tariff.price_stars}*", callback_data=f"select_tariff_{tariff.id}_{server_id if server_id else 'none'}")] for tariff in tariffs]
    buttons.append([InlineKeyboardButton(text=get_text('btn_main_menu', lang), callback_data="main_menu")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback.message.edit_text(get_text('choose_tariff', lang), reply_markup=keyboard)

@router.callback_query(F.data.startswith("select_tariff_"))
async def process_tariff_selection(callback: CallbackQuery, session: AsyncSession):
    parts = callback.data.split("_")
    tariff_id = int(parts[2])
    server_id = int(parts[3]) if len(parts) > 3 and parts[3] != 'none' else None
    user, lang = await _get_user_and_lang(session, callback.from_user.id)
    
    logger.info(f"User {callback.from_user.id} selected tariff {tariff_id} for server {server_id}. Showing payment options.")

    tariff = await session.get(Tariff, tariff_id)
    if not tariff:
        await callback.message.answer(get_text('tariff_not_found', lang))
        await callback.answer()
        return

    buttons = [
        [InlineKeyboardButton(text=get_text('btn_pay_card', lang).format(price=tariff.price_rub/100), callback_data=f"pay_card_{tariff.id}_{server_id if server_id else 'none'}")],
        [InlineKeyboardButton(text=get_text('btn_pay_stars', lang).format(stars=tariff.price_stars), callback_data=f"pay_stars_{tariff.id}_{server_id if server_id else 'none'}")],
        [InlineKeyboardButton(text=get_text('btn_pay_transfer', lang), callback_data=f"pay_transfer_{tariff.id}_{server_id if server_id else 'none'}")],
    ]
    if tariff.duration_days >= 365:
        buttons.append([InlineKeyboardButton(text=get_text('btn_pay_crypto', lang), callback_data=f"pay_crypto_{tariff.id}_{server_id if server_id else 'none'}")])
    
    buttons.append([InlineKeyboardButton(text=get_text('btn_back_to_tariffs', lang), callback_data=f"pay_subscription_for_server_{server_id}")])
    buttons.append([InlineKeyboardButton(text=get_text('btn_main_menu', lang), callback_data="main_menu")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await callback.message.edit_text(
        get_text('tariff_selection_title', lang).format(tariff_name=get_db_text(tariff.name, lang), price=tariff.price_rub/100, days=tariff.duration_days),
        reply_markup=keyboard
    )
    await callback.answer()

@router.callback_query(F.data.startswith("pay_crypto_"))
async def callback_pay_crypto(callback: CallbackQuery, session: AsyncSession):
    parts = callback.data.split("_")
    tariff_id = int(parts[2])
    server_id = int(parts[3]) if len(parts) > 3 and parts[3] != 'none' else None
    user, lang = await _get_user_and_lang(session, callback.from_user.id)

    tariff = await session.get(Tariff, tariff_id)
    if not tariff:
        await callback.message.answer(get_text('tariff_not_found', lang))
        await callback.answer()
        return

    text = get_text('crypto_payment_info', lang).format(
        price_usd=settings.CRYPTO_YEARLY_PRICE_USD,
        btc_address=settings.CRYPTO_BTC_ADDRESS,
        eth_address=settings.CRYPTO_ETH_ADDRESS,
        usdt_address=settings.CRYPTO_USDT_TRC20_ADDRESS
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text('btn_send_check_to_support', lang), url=settings.SUPPORT_CHAT_LINK)],
        [InlineKeyboardButton(text=get_text('btn_back', lang), callback_data=f"select_tariff_{tariff_id}_{server_id if server_id else 'none'}")]
    ])
    await callback.message.edit_text(text, reply_markup=keyboard, disable_web_page_preview=True)
    await callback.answer()

@router.callback_query(F.data.startswith("pay_stars_"))
async def callback_pay_stars(callback: CallbackQuery, session: AsyncSession):
    parts = callback.data.split("_")
    tariff_id = int(parts[2])
    server_id = int(parts[3]) if len(parts) > 3 and parts[3] != 'none' else None
    user, lang = await _get_user_and_lang(session, callback.from_user.id)
    
    logger.info(f"User {callback.from_user.id} selected tariff {tariff_id} for server {server_id} for Stars payment.")

    tariff = await session.get(Tariff, tariff_id)
    if not tariff:
        await callback.message.answer(get_text('tariff_not_found', lang))
        await callback.answer()
        return

    if not settings.TELEGRAM_PAYMENT_PROVIDER_TOKEN or settings.TELEGRAM_PAYMENT_PROVIDER_TOKEN == "YOUR_TELEGRAM_PAYMENT_PROVIDER_TOKEN":
        await callback.message.answer(get_text('stars_payment_unavailable', lang))
        logger.warning("Telegram Stars payment attempted but no provider token is set.")
        await callback.answer()
        return

    payload = f"stars_{callback.from_user.id}_{tariff.id}_{server_id if server_id else 'none'}"
    
    await callback.bot.send_invoice(
        chat_id=callback.from_user.id,
        title=get_text('invoice_title_subscription', lang).format(tariff_name=get_db_text(tariff.name, lang)),
        description=get_text('invoice_description_subscription', lang).format(days=tariff.duration_days),
        payload=payload,
        provider_token=settings.TELEGRAM_PAYMENT_PROVIDER_TOKEN,
        currency="XTR",
        prices=[LabeledPrice(label=get_text('invoice_label_subscription', lang).format(tariff_name=get_db_text(tariff.name, lang), days=tariff.duration_days), amount=tariff.price_stars)],
    )
    await callback.answer()

@router.pre_checkout_query()
async def pre_checkout_query_handler(pre_checkout_query: PreCheckoutQuery, session: AsyncSession):
    logger.info(f"Received pre-checkout query from {pre_checkout_query.from_user.id} with payload {pre_checkout_query.invoice_payload}")
    await pre_checkout_query.answer(ok=True)

@router.message(F.successful_payment)
async def successful_payment_handler(message: Message, session: AsyncSession, bot: Bot):
    logger.info(f"Received successful payment from {message.from_user.id}. Payload: {message.successful_payment.invoice_payload}")
    
    payload = message.successful_payment.invoice_payload
    parts = payload.split('_')
    payment_type = parts[0]
    user_telegram_id = int(parts[1])
    user, lang = await _get_user_and_lang(session, user_telegram_id)

    try:
        if payment_type == 'stars':
            if not (len(parts) == 4):
                raise ValueError(f"Invalid payload for stars payment: {payload}")
            tariff_id = int(parts[2])
            server_id = int(parts[3]) if parts[3] != 'none' else None
            
            tariff = await session.get(Tariff, tariff_id)

            if not all([user, tariff]):
                raise ValueError(f"User or Tariff not found for stars payment: user={user_telegram_id}, tariff={tariff_id}")

            logger.info(f"Processing successful payment for user {user.telegram_id}, tariff {get_db_text(tariff.name, lang)}")

        elif payment_type == 'gift':
            if not (len(parts) == 3):
                raise ValueError(f"Invalid payload for gift payment: {payload}")
            tariff_id = int(parts[2])
            buyer = user

            tariff = await session.get(Tariff, tariff_id)

            if not all([buyer, tariff]):
                raise ValueError(f"Buyer or Tariff not found for gift payment: buyer={user_telegram_id}, tariff={tariff_id}")

            gift_code_str = generate_unique_code()
            new_gift = GiftCode(code=gift_code_str, tariff_id=tariff.id, buyer_user_id=buyer.telegram_id)
            session.add(new_gift)
            await session.commit()
            logger.info(f"User {buyer.telegram_id} purchased a gift subscription (Tariff ID: {tariff.id}). Code: {gift_code_str}")

            bot_user = await bot.get_me()
            gift_link = f"https://t.me/{bot_user.username}?start=G_{gift_code_str}"

            await bot.send_message(
                chat_id=buyer.telegram_id,
                text=get_text('gift_purchase_success', lang).format(
                    tariff_name=get_db_text(tariff.name, lang),
                    gift_link=gift_link
                )
            )

    except (ValueError, IndexError) as e:
        logger.error(f"Could not parse payload: {payload}. Error: {e}")
        await message.answer(get_text('payment_payload_parse_error', lang))
    except Exception as e:
        logger.error(f"An unexpected error occurred during successful payment processing: {e}", exc_info=True)
        await message.answer(get_text('payment_unexpected_error', lang))

@router.callback_query(F.data == "get_free_vpn")
async def callback_get_free_vpn(callback: CallbackQuery, session: AsyncSession):
    logger.info(f"User {callback.from_user.id} clicked get_free_vpn")
    await callback.answer()

    user, lang = await _get_user_and_lang(session, callback.from_user.id)

    if user.trial_used and user.telegram_id not in settings.ADMIN_IDS_LIST:
        await callback.message.answer(get_text('trial_already_used', lang))
        return

    if not settings.TRIAL_SERVER_ID:
        await callback.message.answer(get_text('trial_unavailable', lang))
        return

    trial_server = await session.get(Server, settings.TRIAL_SERVER_ID)
    if not trial_server or not trial_server.is_active:
        await callback.message.answer(get_text('trial_server_unavailable', lang))
        return

    await callback.message.edit_text(get_text('trial_key_creation_wait', lang))

    try:
        vless_link = await _create_or_update_vpn_key(session, user, trial_server, constants.TRIAL_PERIOD_DAYS, lang)
        user.trial_used = True
        await session.commit()

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text('btn_how_to_connect', lang), callback_data="how_to_connect")]
        ])

        await callback.message.answer(get_text('trial_key_creation_success', lang).format(vless_link=vless_link), parse_mode='HTML', reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error creating trial VPN key: {e}")
        await callback.message.answer(get_text('trial_key_creation_error', lang))

@router.callback_query(F.data == "gift_subscription")
async def callback_gift_subscription(callback: CallbackQuery, session: AsyncSession):
    await callback.answer()
    logger.info(f"User {callback.from_user.id} initiated gift subscription purchase.")
    user, lang = await _get_user_and_lang(session, callback.from_user.id)

    yearly_tariff = (await session.execute(select(Tariff).where(Tariff.duration_days >= 365, Tariff.is_active == True))).scalars().first()

    if not yearly_tariff:
        await callback.message.edit_text(get_text('gift_subscription_unavailable', lang))
        return

    text = "\n\n".join([
        get_text('gift_purchase_title', lang),
        get_text('gift_purchase_instructions', lang).format(price=yearly_tariff.price_rub / 100, days=yearly_tariff.duration_days)
    ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text('btn_pay_gift_card', lang).format(price=yearly_tariff.price_rub/100), callback_data=f"pay_gift_card_{yearly_tariff.id}")],
        [InlineKeyboardButton(text=get_text('btn_pay_gift_stars', lang).format(stars=yearly_tariff.price_stars), callback_data=f"pay_gift_stars_{yearly_tariff.id}")],
        [InlineKeyboardButton(text=get_text('btn_contact_support_for_gift', lang), url=settings.SUPPORT_CHAT_LINK)],
        [InlineKeyboardButton(text=get_text('btn_back_to_referral_menu', lang), callback_data="referral_program")]
    ])

    await callback.message.edit_text(text, reply_markup=keyboard)

@router.callback_query(F.data.startswith("pay_gift_stars_"))
async def callback_pay_gift_stars(callback: CallbackQuery, session: AsyncSession):
    tariff_id = int(callback.data.split('_')[-1])
    user, lang = await _get_user_and_lang(session, callback.from_user.id)
    
    tariff = await session.get(Tariff, tariff_id)
    if not tariff: 
        return await callback.answer(get_text('tariff_not_found', lang), show_alert=True)

    payload = f"gift_{callback.from_user.id}_{tariff.id}"
    await callback.bot.send_invoice(
        chat_id=callback.from_user.id,
        title=get_text('invoice_title_gift', lang).format(tariff_name=get_db_text(tariff.name, lang)),
        description=get_text('invoice_description_gift', lang).format(days=tariff.duration_days),
        payload=payload,
        provider_token=settings.TELEGRAM_PAYMENT_PROVIDER_TOKEN,
        currency="XTR",
        prices=[LabeledPrice(label=get_text('invoice_label_gift', lang).format(tariff_name=get_db_text(tariff.name, lang)), amount=tariff.price_stars)],
    )
    await callback.answer()

@router.callback_query(F.data == "why_vpn")
async def callback_why_vpn(callback: CallbackQuery, session: AsyncSession):
    user, lang = await _get_user_and_lang(session, callback.from_user.id)
    await callback.answer(get_text('tbd', lang), show_alert=True)

@router.callback_query(F.data == "help")
async def callback_help(callback: CallbackQuery, session: AsyncSession):
    user, lang = await _get_user_and_lang(session, callback.from_user.id)
    await callback.answer() # Acknowledge the callback

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text('btn_go_to_support_chat', lang), url=settings.SUPPORT_CHAT_LINK)],
        [InlineKeyboardButton(text=get_text('btn_main_menu', lang), callback_data="main_menu")]
    ])

    await callback.message.edit_text(
        get_text('support_redirect_message', lang),
        reply_markup=keyboard
    )

@router.callback_query(F.data == "terms_of_use")
async def callback_terms_of_use(callback: CallbackQuery, session: AsyncSession):
    user, lang = await _get_user_and_lang(session, callback.from_user.id)
    await callback.answer() # Answer the callback query to remove the loading state
    # Create HTML links for terms of service and privacy policy
    terms_of_service_html = f"<a href=\"{settings.TERMS_OF_SERVICE_URL}\">{get_text('license_agreement', lang)}</a>"
    privacy_policy_html = f"<a href=\"{settings.PRIVACY_POLICY_URL}\">{get_text('privacy_policy', lang)}</a>"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text('btn_cancel_subscription', lang), callback_data="cancel_subscription")], # Assuming you'll implement this handler
        [InlineKeyboardButton(text=get_text('btn_help', lang), callback_data="help")],
        [InlineKeyboardButton(text=get_text('btn_main_menu', lang), callback_data="main_menu")]
    ])
    await callback.message.edit_text(
        get_text('terms_of_use_full', lang).format(

            support_chat_link=settings.SUPPORT_CHAT_LINK,
            terms_of_service_html=terms_of_service_html,
            privacy_policy_html=privacy_policy_html
        ),
        reply_markup=keyboard,
        disable_web_page_preview=True # Disable preview for links
    )

@router.callback_query(F.data.startswith("pay_card_"))
async def callback_pay_card(callback: CallbackQuery, session: AsyncSession):
    user, lang = await _get_user_and_lang(session, callback.from_user.id)
    await callback.answer()

    if not settings.YOOKASSA_SHOP_ID or not settings.YOOKASSA_SECRET_KEY:
        logger.warning("YooKassa credentials are not set.")
        await callback.message.answer(get_text('payment_card_unavailable', lang))
        return

    parts = callback.data.split("_")
    tariff_id = int(parts[2])
    server_id = int(parts[3]) if len(parts) > 3 and parts[3] != 'none' else None

    tariff = await session.get(Tariff, tariff_id)
    if not tariff:
        await callback.message.answer(get_text('tariff_not_found', lang))
        return

    Configuration.account_id = settings.YOOKASSA_SHOP_ID
    Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

    transaction_id = str(uuid.uuid4())
    payment = Payment.create({
        "amount": {
            "value": f"{tariff.price_rub / 100:.2f}",
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": f"https://t.me/{(await callback.bot.get_me()).username}"
        },
        "capture": True,
        "description": f"Оплата тарифа '{get_db_text(tariff.name, lang)}'",
        "metadata": {
            'telegram_user_id': callback.from_user.id,
            'tariff_id': tariff_id,
            'server_id': server_id,
            'payment_type': 'subscription'
        }
    }, transaction_id)

    new_transaction = Transaction(
        id=payment.id,
        user_id=callback.from_user.id,
        tariff_id=tariff_id,
        amount=tariff.price_rub,
        currency="RUB",
        payment_system="YooKassa",
        status="pending",
        payment_details=payment.metadata
    )
    session.add(new_transaction)
    await session.commit()

    payment_url = payment.confirmation.confirmation_url
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text('btn_go_to_payment', lang), url=payment_url)],
        [InlineKeyboardButton(text=get_text('btn_back', lang), callback_data=f"select_tariff_{tariff_id}_{server_id if server_id else 'none'}")]
    ])
    await callback.message.edit_text(get_text('payment_redirect_info', lang), reply_markup=keyboard)


@router.callback_query(F.data.startswith("pay_transfer_"))
async def callback_pay_transfer(callback: CallbackQuery, session: AsyncSession):
    user, lang = await _get_user_and_lang(session, callback.from_user.id)
    await callback.answer(get_text('payment_transfer_unavailable', lang), show_alert=True)


@router.callback_query(F.data.startswith("pay_gift_card_"))
async def callback_pay_gift_card(callback: CallbackQuery, session: AsyncSession):
    user, lang = await _get_user_and_lang(session, callback.from_user.id)
    await callback.answer()

    if not settings.YOOKASSA_SHOP_ID or not settings.YOOKASSA_SECRET_KEY:
        logger.warning("YooKassa credentials are not set.")
        await callback.message.answer(get_text('payment_gift_card_unavailable', lang))
        return

    tariff_id = int(callback.data.split('_')[-1])
    tariff = await session.get(Tariff, tariff_id)
    if not tariff:
        await callback.message.answer(get_text('tariff_not_found', lang))
        return

    Configuration.account_id = settings.YOOKASSA_SHOP_ID
    Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

    transaction_id = str(uuid.uuid4())
    payment = Payment.create({
        "amount": {
            "value": f"{tariff.price_rub / 100:.2f}",
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": f"https://t.me/{(await callback.bot.get_me()).username}"
        },
        "capture": True,
        "description": f"Покупка подарочного кода для тарифа '{get_db_text(tariff.name, lang)}'",
        "metadata": {
            'telegram_user_id': callback.from_user.id,
            'tariff_id': tariff_id,
            'payment_type': 'gift'
        }
    }, transaction_id)

    new_transaction = Transaction(
        id=payment.id,
        user_id=callback.from_user.id,
        tariff_id=tariff_id,
        amount=tariff.price_rub,
        currency="RUB",
        payment_system="YooKassa",
        status="pending",
        payment_details=payment.metadata
    )
    session.add(new_transaction)
    await session.commit()

    payment_url = payment.confirmation.confirmation_url
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text('btn_go_to_payment', lang), url=payment_url)],
        [InlineKeyboardButton(text=get_text('btn_back_to_gift_menu', lang), callback_data="gift_subscription")]
    ])
    await callback.message.edit_text(get_text('payment_redirect_info', lang), reply_markup=keyboard)