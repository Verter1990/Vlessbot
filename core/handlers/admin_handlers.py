from aiogram import Router, F, Bot
from aiogram.filters import Command, BaseFilter, CommandObject
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from sqlalchemy.orm import selectinload
from loguru import logger
from datetime import datetime, timedelta

from core.database.models import Server, Tariff, User, Subscription, Transaction, GiftCode
from core.config import settings
from core.utils.security import encrypt_password
from core.services.xui_client import get_client, XUIClientError

router = Router()

# --- Фильтр администратора ---
class IsAdmin(BaseFilter):
    async def __call__(self, message: Message | CallbackQuery) -> bool:
        admin_ids = [int(admin_id.strip()) for admin_id in settings.ADMIN_IDS.split(',')]
        return message.from_user.id in admin_ids

# --- FSM для админки ---
class AdminFSM(StatesGroup):
    # Add Server
    add_server_name = State()
    add_server_api_url = State()
    add_server_api_user = State()
    add_server_api_password = State()
    add_server_inbound_id = State()
    # Add Tariff
    add_tariff_name_ru = State()
    add_tariff_name_en = State()
    add_tariff_duration = State()
    add_tariff_price_rub = State()
    add_tariff_price_stars = State()
    # User Management
    find_user = State()
    edit_user_balance = State()
    edit_user_days = State()

# --- Клавиатуры для админки ---
async def get_main_admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Управление пользователями", callback_data="admin_users_menu")],
        [InlineKeyboardButton(text="Управление серверами", callback_data="admin_servers_menu")],
        [InlineKeyboardButton(text="Управление тарифами", callback_data="admin_tariffs_menu")],
        [InlineKeyboardButton(text="Статистика", callback_data="admin_stats")],
    ])

async def get_servers_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Список серверов", callback_data="admin_list_servers")],
        [InlineKeyboardButton(text="Добавить сервер", callback_data="admin_add_server_start")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_main_menu")],
    ])

async def get_users_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Список пользователей", callback_data="admin_list_users")],
        [InlineKeyboardButton(text="Найти пользователя", callback_data="admin_find_user_start")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_main_menu")],
    ])

async def get_tariffs_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Список тарифов", callback_data="admin_list_tariffs")],
        [InlineKeyboardButton(text="Добавить тариф", callback_data="admin_add_tariff_start")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_main_menu")],
    ])

router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())





# --- Главное меню админки ---



@router.callback_query(F.data == "admin_main_menu")
async def cq_admin_panel(callback: CallbackQuery):
    await callback.answer()
    keyboard = await get_main_admin_keyboard()
    await callback.message.edit_text("<b>Панель администратора</b>", reply_markup=keyboard)

@router.callback_query(F.data == "admin_panel_main")
async def callback_admin_panel_main(callback: CallbackQuery):
    await callback.answer()
    keyboard = await get_main_admin_keyboard()
    await callback.message.edit_text("<b>Панель администратора</b>", reply_markup=keyboard)

# --- Отмена FSM ---

@router.message(Command("cancel"))


# --- Управление серверами ---

@router.callback_query(F.data == "admin_servers_menu")
async def cq_servers_menu(callback: CallbackQuery):
    await callback.answer()
    keyboard = await get_servers_menu_keyboard()
    await callback.message.edit_text("<b>Управление серверами</b>", reply_markup=keyboard)

@router.callback_query(F.data == "admin_list_servers")
async def cq_list_servers(callback: CallbackQuery, session: AsyncSession):
    await callback.answer()
    servers = (await session.execute(select(Server).order_by(Server.id))).scalars().all()

    if not servers:
        await callback.message.edit_text(
            "В базе данных нет ни одного сервера.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_servers_menu")]
            ])
        )
        return

    response_text = "<b>Список серверов:</b>\n\n"
    buttons = []
    for server in servers:
        status = "✅" if server.is_active else "❌"
        response_text += f"{status} ID: <code>{server.id}</code> | {server.name}\n"
        buttons.append([InlineKeyboardButton(text=f"Переключить ID {server.id}", callback_data=f"admin_toggle_server_{server.id}")])
    
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_servers_menu")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text(response_text, reply_markup=keyboard)

@router.callback_query(F.data.startswith("admin_toggle_server_"))
async def cq_toggle_server(callback: CallbackQuery, session: AsyncSession):
    server_id = int(callback.data.split("_")[-1])
    server = await session.get(Server, server_id)
    if not server:
        await callback.answer(f"Сервер с ID {server_id} не найден.", show_alert=True)
        return

    server.is_active = not server.is_active
    await session.commit()
    status = "включен" if server.is_active else "отключен"
    await callback.answer(f"Сервер {server.name} {status}")
    logger.info(f"Admin {callback.from_user.id} toggled server {server_id} to {status}")
    
    # Refresh the list
    await cq_list_servers(callback, session)

# --- Управление тарифами ---

@router.callback_query(F.data == "admin_users_menu")
async def cq_users_menu(callback: CallbackQuery):
    await callback.answer()
    keyboard = await get_users_menu_keyboard()
    await callback.message.edit_text("<b>Управление пользователями</b>", reply_markup=keyboard)

@router.callback_query(F.data == "admin_list_users")
async def cq_list_users(callback: CallbackQuery, session: AsyncSession):
    await callback.answer()
    users = (await session.execute(select(User).options(selectinload(User.subscriptions)).order_by(User.id))).scalars().all()

    if not users:
        await callback.message.edit_text(
            "В базе данных нет ни одного пользователя.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_users_menu")]
            ])
        )
        return

    response_text = "<b>Список пользователей:</b>\n\n"
    for user in users:
        status = "✅" if not user.is_banned else "🚫"
        response_text += f"{status} ID: <code>{user.telegram_id}</code> | @{user.username if user.username else 'N/A'}\n"
        response_text += f"   Дни: {user.unassigned_days} | Баланс: {user.referral_balance / 100} RUB\n"
        response_text += f"   Подписки: {len([s for s in user.subscriptions if s.is_active and s.expires_at > datetime.utcnow()])}\n\n"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_users_menu")]
    ])
    await callback.message.edit_text(response_text, reply_markup=keyboard)

@router.callback_query(F.data == "admin_tariffs_menu")
async def cq_tariffs_menu(callback: CallbackQuery):
    await callback.answer()
    keyboard = await get_tariffs_menu_keyboard()
    await callback.message.edit_text("<b>Управление тарифами</b>", reply_markup=keyboard)

@router.callback_query(F.data == "admin_list_tariffs")
async def cq_list_tariffs(callback: CallbackQuery, session: AsyncSession):
    await callback.answer()
    tariffs = (await session.execute(select(Tariff).order_by(Tariff.id))).scalars().all()

    if not tariffs:
        await callback.message.edit_text(
            "В базе данных нет ни одного тарифа.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_tariffs_menu")]
            ])
        )
        return

    response_text = "<b>Список тарифов:</b>\n\n"
    buttons = []
    for tariff in tariffs:
        status = "✅" if tariff.is_active else "❌"
        name_ru = tariff.name.get('ru', '[нет названия]')
        name_en = tariff.name.get('en', '[no name]')
        response_text += f"{status} ID: <code>{tariff.id}</code> | {name_ru} / {name_en} ({tariff.duration_days} д.)\n"
        response_text += f"   Цена: {tariff.price_rub / 100} RUB | {tariff.price_stars} ⭐️\n"
        buttons.append([
            InlineKeyboardButton(text=f"Переключить ID {tariff.id}", callback_data=f"admin_toggle_tariff_{tariff.id}"),
            InlineKeyboardButton(text=f"🗑️ Удалить ID {tariff.id}", callback_data=f"admin_delete_tariff_confirm_{tariff.id}")
        ])

    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_tariffs_menu")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.message.edit_text(response_text, reply_markup=keyboard)

@router.callback_query(F.data.startswith("admin_delete_tariff_confirm_"))
async def cq_delete_tariff_confirm(callback: CallbackQuery, session: AsyncSession):
    tariff_id = int(callback.data.split("_")[-1])
    tariff = await session.get(Tariff, tariff_id)
    if not tariff:
        await callback.answer(f"Тариф с ID {tariff_id} не найден.", show_alert=True)
        return

    name_ru = tariff.name.get('ru', f"ID {tariff_id}")
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да, удалить", callback_data=f"admin_delete_tariff_execute_{tariff_id}")],
        [InlineKeyboardButton(text="Отмена", callback_data="admin_list_tariffs")]
    ])
    await callback.message.edit_text(f"Вы уверены, что хотите удалить тариф \"{name_ru}\"? Это действие необратимо.", reply_markup=keyboard)

@router.callback_query(F.data.startswith("admin_delete_tariff_execute_"))
async def cq_delete_tariff_execute(callback: CallbackQuery, session: AsyncSession):
    tariff_id = int(callback.data.split("_")[-1])
    tariff = await session.get(Tariff, tariff_id)
    if not tariff:
        await callback.answer(f"Тариф с ID {tariff_id} не найден.", show_alert=True)
        return

    tariff.is_active = False
    await session.commit()
    logger.info(f"Admin {callback.from_user.id} deactivated tariff {tariff_id}")
    await callback.answer(f"Тариф ID {tariff_id} деактивирован и скрыт от пользователей.", show_alert=True)
    await cq_list_tariffs(callback, session)


@router.callback_query(F.data.startswith("admin_toggle_tariff_"))
async def cq_toggle_tariff(callback: CallbackQuery, session: AsyncSession):
    tariff_id = int(callback.data.split("_")[-1])
    tariff = await session.get(Tariff, tariff_id)
    if not tariff:
        await callback.answer(f"Тариф с ID {tariff_id} не найден.", show_alert=True)
        return

    tariff.is_active = not tariff.is_active
    await session.commit()
    status = "включен" if tariff.is_active else "отключен"
    await callback.answer(f"Тариф {tariff.name} {status}")
    logger.info(f"Admin {callback.from_user.id} toggled tariff {tariff_id} to {status}")

    # Refresh the list
    await cq_list_tariffs(callback, session)

# --- Статистика ---

@router.callback_query(F.data == "admin_stats")
async def cq_stats(callback: CallbackQuery, session: AsyncSession):
    await callback.answer()
    
    total_users = await session.scalar(select(func.count(User.id)))
    now = datetime.utcnow()
    users_today = await session.scalar(select(func.count(User.id)).where(User.created_at >= now - timedelta(days=1)))
    users_week = await session.scalar(select(func.count(User.id)).where(User.created_at >= now - timedelta(days=7)))
    active_subs = await session.scalar(select(func.count(Subscription.id)).where(Subscription.is_active == True, Subscription.expires_at > now))

    stats_text = (
        f"📊 <b>Статистика бота</b>\n\n"
        f"👤 Всего пользователей: <b>{total_users}</b>\n"
        f"📈 Новых за 24 часа: <b>{users_today}</b>\n"
        f"📈 Новых за 7 дней: <b>{users_week}</b>\n"
        f"🔑 Активных подписок: <b>{active_subs}</b>"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_main_menu")]
    ])
    await callback.message.edit_text(stats_text, reply_markup=keyboard)

# --- Процессы добавления (FSM) ---

# Добавление тарифа
@router.callback_query(F.data == "admin_add_tariff_start")
async def cq_add_tariff_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(AdminFSM.add_tariff_name_ru)
    await callback.message.edit_text(
        "<b>Шаг 1/5: Название тарифа (RU)</b>\nВведите русское название (напр. 📅 30 дней).",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_cancel_fsm")]
        ])
    )

@router.message(AdminFSM.add_tariff_name_ru)
async def msg_add_tariff_name_ru(message: Message, state: FSMContext):
    logger.info(f"Admin {message.from_user.id} entered tariff name (RU): {message.text}")
    await state.update_data(name_ru=message.text)
    await state.set_state(AdminFSM.add_tariff_name_en)
    await message.answer(
        "<b>Шаг 2/5: Название тарифа (EN)</b>\nВведите английское название (напр. 📅 30 days).",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_cancel_fsm")]
        ])
    )

@router.message(AdminFSM.add_tariff_name_en)
async def msg_add_tariff_name_en(message: Message, state: FSMContext):
    logger.info(f"Admin {message.from_user.id} entered tariff name (EN): {message.text}")
    await state.update_data(name_en=message.text)
    await state.set_state(AdminFSM.add_tariff_duration)
    await message.answer(
        "<b>Шаг 3/5: Длительность (в днях)</b>\nВведите количество дней.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_cancel_fsm")]
        ])
    )

@router.message(AdminFSM.add_tariff_duration)
async def msg_add_tariff_duration(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Длительность должна быть числом. Попробуйте еще раз.")
        return
    logger.info(f"Admin {message.from_user.id} entered tariff duration: {message.text}")
    await state.update_data(duration_days=int(message.text))
    await state.set_state(AdminFSM.add_tariff_price_rub)
    await message.answer(
        "<b>Шаг 4/5: Цена (в копейках)</b>\nВведите цену в копейках (напр. 19900 для 199.00 RUB).",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_cancel_fsm")]
        ])
    )

@router.message(AdminFSM.add_tariff_price_rub)
async def msg_add_tariff_price_rub(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Цена должна быть числом (в копейках). Попробуйте еще раз.")
        return
    logger.info(f"Admin {message.from_user.id} entered tariff price (RUB): {message.text}")
    await state.update_data(price_rub=int(message.text))
    await state.set_state(AdminFSM.add_tariff_price_stars)
    await message.answer(
        "<b>Шаг 5/5: Цена (в Telegram Stars)</b>\nВведите цену в Telegram Stars.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_cancel_fsm")]
        ])
    )

@router.message(AdminFSM.add_tariff_price_stars)
async def msg_add_tariff_price_stars(message: Message, state: FSMContext, session: AsyncSession):
    if not message.text.isdigit():
        await message.answer("Цена в Stars должна быть числом. Попробуйте еще раз.")
        return
    logger.info(f"Admin {message.from_user.id} entered tariff price (Stars): {message.text}")
    await state.update_data(price_stars=int(message.text))
    
    data = await state.get_data()
    await state.clear()

    try:
        new_tariff = Tariff(
            name={"ru": data['name_ru'], "en": data['name_en']},
            duration_days=data['duration_days'],
            price_rub=data['price_rub'],
            price_stars=data['price_stars']
        )
        session.add(new_tariff)
        await session.commit()
        logger.info(f"Admin {message.from_user.id} successfully added new tariff: {data['name_ru']}")
        
        keyboard = await get_tariffs_menu_keyboard()
        await message.answer(f"✅ Тариф '{data['name_ru']}' успешно добавлен!", reply_markup=keyboard)

    except Exception as e:
        logger.error(f"Failed to add new tariff. Admin: {message.from_user.id}. Data: {data}. Error: {e}")
        keyboard = await get_tariffs_menu_keyboard()
        await message.answer("❌ Произошла ошибка при добавлении тарифа. Подробности в логах.", reply_markup=keyboard)


# Добавление сервера
@router.callback_query(F.data == "admin_add_server_start")
async def cq_add_server_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(AdminFSM.add_server_name)
    await callback.message.edit_text(
        "<b>Шаг 1/5: Название сервера</b>\nВведите название (напр. 🇩🇪 Германия).",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_cancel_fsm")]
        ])
    )

@router.message(AdminFSM.add_server_name)
async def msg_add_server_name(message: Message, state: FSMContext):
    logger.info(f"Admin {message.from_user.id} entered server name: {message.text}")
    await state.update_data(server_name=message.text)
    await state.set_state(AdminFSM.add_server_api_url)
    await message.answer(
        "<b>Шаг 2/5: API URL</b>\nВведите URL для API (напр. http://your.domain:54321).",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_cancel_fsm")]
        ])
    )

@router.message(AdminFSM.add_server_api_url)
async def msg_add_server_api_url(message: Message, state: FSMContext):
    logger.info(f"Admin {message.from_user.id} entered server API URL: {message.text}")
    await state.update_data(api_url=message.text)
    await state.set_state(AdminFSM.add_server_api_user)
    await message.answer(
        "<b>Шаг 3/5: API User</b>\nВведите имя пользователя для API.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_cancel_fsm")]
        ])
    )

@router.message(AdminFSM.add_server_api_user)
async def msg_add_server_api_user(message: Message, state: FSMContext):
    logger.info(f"Admin {message.from_user.id} entered server API user: {message.text}")
    await state.update_data(api_user=message.text)
    await state.set_state(AdminFSM.add_server_api_password)
    await message.answer(
        "<b>Шаг 4/5: API Password</b>\nВведите пароль для API.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_cancel_fsm")]
        ])
    )

@router.message(AdminFSM.add_server_api_password)
async def msg_add_server_api_password(message: Message, state: FSMContext):
    logger.info(f"Admin {message.from_user.id} entered server API password.")
    encrypted_password = encrypt_password(message.text)
    await state.update_data(api_password=encrypted_password)
    await state.set_state(AdminFSM.add_server_inbound_id)
    await message.answer(
        "<b>Шаг 5/5: Inbound ID</b>\nВведите ID входящего подключения (inbound).",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_cancel_fsm")]
        ])
    )

@router.message(AdminFSM.add_server_inbound_id)
async def msg_add_server_inbound_id(message: Message, state: FSMContext, session: AsyncSession):
    if not message.text.isdigit():
        await message.answer("Inbound ID должен быть числом. Попробуйте еще раз.")
        return

    logger.info(f"Admin {message.from_user.id} entered inbound ID: {message.text}")
    await state.update_data(inbound_id=int(message.text))
    
    data = await state.get_data()
    await state.clear()

    try:
        new_server = Server(
            name=data['server_name'],
            api_url=data['api_url'],
            api_user=data['api_user'],
            api_password=data['api_password'],
            inbound_id=data['inbound_id']
        )
        session.add(new_server)
        await session.commit()
        logger.info(f"Admin {message.from_user.id} successfully added new server: {data['server_name']}")
        
        keyboard = await get_servers_menu_keyboard()
        await message.answer(f"✅ Сервер '{data['server_name']}' успешно добавлен!", reply_markup=keyboard)

    except Exception as e:
        logger.error(f"Failed to add new server. Admin: {message.from_user.id}. Data: {data}. Error: {e}")
        keyboard = await get_servers_menu_keyboard()
        await message.answer("❌ Произошла ошибка при добавлении сервера. Подробности в логах.", reply_markup=keyboard)


# Поиск пользователя
@router.callback_query(F.data == "admin_find_user_start")
async def cq_find_user_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(AdminFSM.find_user)
    await callback.message.edit_text(
        "<b>Поиск пользователя</b>\nВведите Telegram ID или username пользователя.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_cancel_fsm")]
        ])
    )

@router.message(AdminFSM.find_user)
async def msg_find_user(message: Message, state: FSMContext, session: AsyncSession):
    query = message.text.strip()
    user = None
    if query.isdigit():
        user = (await session.execute(select(User).where(User.telegram_id == int(query)))).scalars().first()
    else:
        user = (await session.execute(select(User).where(User.username == query.replace("@", "")))).scalars().first()

    if user:
        await state.clear()
        await cq_user_details(message, session, user)
    else:
        await message.answer(
            "Пользователь не найден. Попробуйте еще раз или отмените.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_cancel_fsm")]
            ])
        )

async def get_user_management_keyboard(user: User) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="💰 Изменить баланс", callback_data=f"admin_edit_user_balance_start_{user.telegram_id}"),
            InlineKeyboardButton(text="📅 Изменить дни", callback_data=f"admin_edit_user_days_start_{user.telegram_id}")
        ],
        [
            InlineKeyboardButton(
                text="✅ Разблокировать" if user.is_banned else "🚫 Заблокировать",
                callback_data=f"admin_toggle_user_block_{user.telegram_id}"
            ),
            InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"admin_delete_user_confirm_{user.telegram_id}")
        ],
        [InlineKeyboardButton(text="⬅️ К поиску", callback_data="admin_users_menu")],
        [InlineKeyboardButton(text="⬅️ Главное меню", callback_data="admin_main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def cq_user_details(message: Message | CallbackQuery, session: AsyncSession, user: User):
    if isinstance(message, CallbackQuery):
        await message.answer()
        user_message = message.message
    else:
        user_message = message

    subscriptions = (await session.execute(select(Subscription).where(Subscription.user_id == user.telegram_id))).scalars().all()
    
    subs_text = ""
    if subscriptions:
        for sub in subscriptions:
            server = await session.get(Server, sub.server_id)
            subs_text += f"  - Сервер: {server.name if server else 'Неизвестно'}, Истекает: {sub.expires_at.strftime('%Y-%m-%d %H:%M')}, Активна: {'Да' if sub.is_active else 'Нет'}\n"
    else:
        subs_text = "  Нет активных подписок.\n"

    user_info = (
        f"<b>Информация о пользователе:</b>\n"
        f"ID: <code>{user.telegram_id}</code> (@{user.username if user.username else 'N/A'})\n"
        f"Статус: {'Заблокирован' if user.is_banned else 'Активен'}\n"
        f"Язык: {user.language_code}\n"
        f"Нераспределенные дни: {user.unassigned_days}\n"
        f"Реферальный баланс: {user.referral_balance / 100} RUB\n"
        f"L2 Реферальный баланс: {user.l2_referral_balance / 100} RUB\n"
        f"Пробный период: {'Использован' if user.trial_used else 'Не использован'}\n"
        f"Первый VPN: {'Активирован' if user.activated_first_vpn else 'Не активирован'}\n"
        f"Реферер ID: {user.referrer_id if user.referrer_id else 'Нет'}\n"
        f"Реферальный код: {user.referral_code if user.referral_code else 'Нет'}\n"
        f"Создан: {user.created_at.strftime('%Y-%m-%d %H:%M')}\n"
        f"<b>Подписки:</b>\n{subs_text}"
    )

    keyboard = await get_user_management_keyboard(user)
    # Use edit_text for callback queries and answer for messages
    if isinstance(message, CallbackQuery):
        await user_message.edit_text(user_info, reply_markup=keyboard)
    else:
        await user_message.answer(user_info, reply_markup=keyboard)

# --- User Management Actions ---

@router.callback_query(F.data.startswith("admin_toggle_user_block_"))
async def cq_toggle_user_block(callback: CallbackQuery, session: AsyncSession):
    user_telegram_id = int(callback.data.split("_")[-1])
    user = (await session.execute(select(User).where(User.telegram_id == user_telegram_id))).scalars().first()
    if not user:
        await callback.answer("Пользователь не найден.", show_alert=True)
        return

    user.is_banned = not user.is_banned
    await session.commit()
    
    status = "заблокирован" if user.is_banned else "разблокирован"

    logger.info(f"Admin {callback.from_user.id} {status} user {user.telegram_id}")
    await callback.answer(f"Пользователь {user.username or user.telegram_id} {status}.")
    
    await cq_user_details(callback, session, user)

@router.callback_query(F.data.startswith("admin_delete_user_confirm_"))
async def cq_delete_user_confirm(callback: CallbackQuery, session: AsyncSession):
    user_telegram_id = int(callback.data.split("_")[-1])
    user = (await session.execute(select(User).where(User.telegram_id == user_telegram_id))).scalars().first()
    if not user:
        await callback.answer("Пользователь не найден.", show_alert=True)
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да, удалить", callback_data=f"admin_delete_user_execute_{user.telegram_id}")],
        [InlineKeyboardButton(text="Отмена", callback_data=f"admin_show_user_details_{user.telegram_id}")]
    ])
    await callback.message.edit_text(
        f"Вы уверены, что хотите удалить пользователя @{user.username or user_id}?\n"
        f"<b>Это действие необратимо и удалит все его подписки.</b>",
        reply_markup=keyboard
    )

@router.callback_query(F.data.startswith("admin_delete_user_execute_"))
async def cq_delete_user_execute(callback: CallbackQuery, session: AsyncSession):
    user_telegram_id = int(callback.data.split("_")[-1])
    user = (await session.execute(select(User).where(User.telegram_id == user_telegram_id))).scalars().first()
    if not user:
        await callback.answer("Пользователь не найден.", show_alert=True)
        return

    # 1. Find all user subscriptions
    subscriptions = (await session.execute(
        select(Subscription).where(Subscription.user_id == user.telegram_id)
    )).scalars().all()

    # 2. Attempt to delete clients from XUI panels
    if subscriptions:
        await callback.message.edit_text(f"Начинаю удаление {len(subscriptions)} VLESS-клиентов с VPN-серверов...")
        for sub in subscriptions:
            server = await session.get(Server, sub.server_id)
            if not server:
                logger.warning(f"Server with ID {sub.server_id} not found for subscription {sub.id}. Skipping XUI deletion.")
                continue
            
            try:
                xui_client = get_client(server)
                await xui_client.delete_user(server.inbound_id, sub.xui_user_uuid)
                logger.info(f"Successfully deleted VLESS client {sub.xui_user_uuid} from server {server.name} for user {user.telegram_id}")
            except XUIClientError as e:
                logger.error(f"Failed to delete VLESS client {sub.xui_user_uuid} from server {server.name}. Error: {e}")
                # We continue anyway, to delete the user from the bot's DB
            except Exception as e:
                logger.error(f"An unexpected error occurred during XUI client deletion for user {user.telegram_id} on server {server.name}. Error: {e}")

    # 3. Delete user data from the bot's database
    await callback.message.edit_text("Удаляю данные пользователя из базы данных бота...")
    await session.execute(delete(Subscription).where(Subscription.user_id == user.telegram_id))
    await session.execute(delete(Transaction).where(Transaction.user_id == user.telegram_id))
    await session.execute(delete(GiftCode).where(GiftCode.buyer_user_id == user.telegram_id))
    await session.execute(delete(GiftCode).where(GiftCode.activated_by_user_id == user.telegram_id))
    
    await session.delete(user)
    await session.commit()
    
    logger.warning(f"Admin {callback.from_user.id} DELETED user {user.telegram_id} and all their data.")
    await callback.answer(f"Пользователь {user.username or user.telegram_id} и все его данные удалены.", show_alert=True)
    
    await cq_users_menu(callback)

# Callback to show user details (used for cancellation)
@router.callback_query(F.data.startswith("admin_show_user_details_"))
async def cq_show_user_details_from_callback(callback: CallbackQuery, session: AsyncSession):
    user_id = int(callback.data.split("_")[-1])
    user = await session.get(User, user_id)
    if not user:
        await callback.answer("Пользователь не найден.", show_alert=True)
        return
    await cq_user_details(callback, session, user)

# --- FSM for Editing User ---

# Edit Balance
@router.callback_query(F.data.startswith("admin_edit_user_balance_start_"))
async def cq_edit_user_balance_start(callback: CallbackQuery, state: FSMContext):
    user_telegram_id = int(callback.data.split("_")[-1])
    await state.update_data(user_telegram_id=user_telegram_id)
    await state.set_state(AdminFSM.edit_user_balance)
    await callback.answer()
    await callback.message.edit_text(
        "Введите новую сумму <b>реферального баланса</b> в копейках (целое число).",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data=f"admin_show_user_details_{user_telegram_id}")]
        ])
    )

@router.message(AdminFSM.edit_user_balance)
async def msg_edit_user_balance(message: Message, state: FSMContext, session: AsyncSession):
    if not message.text.isdigit():
        await message.answer("Баланс должен быть целым числом. Попробуйте еще раз.")
        return

    data = await state.get_data()
    user = (await session.execute(select(User).where(User.telegram_id == data['user_telegram_id']))).scalars().first()
    if not user:
        await message.answer("Пользователь не найден. Отмена.")
        await state.clear()
        return

    new_balance = int(message.text)
    old_balance = user.referral_balance
    user.referral_balance = new_balance
    await session.commit()
    await state.clear()
    
    logger.info(f"Admin {message.from_user.id} changed balance for user {user.telegram_id} to {new_balance}")
    await message.answer(f"Баланс пользователя @{user.username or user.telegram_id} изменен на {new_balance / 100} RUB.")
    await cq_user_details(message, session, user)

# Edit Days
@router.callback_query(F.data.startswith("admin_edit_user_days_start_"))
async def cq_edit_user_days_start(callback: CallbackQuery, state: FSMContext):
    user_telegram_id = int(callback.data.split("_")[-1])
    await state.update_data(user_telegram_id=user_telegram_id)
    await state.set_state(AdminFSM.edit_user_days)
    await callback.answer()
    await callback.message.edit_text(
        "Введите новое количество <b>нераспределенных дней</b> (целое число).",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data=f"admin_show_user_details_{user_telegram_id}")]
        ])
    )

@router.message(AdminFSM.edit_user_days)
async def msg_edit_user_days(message: Message, state: FSMContext, session: AsyncSession):
    if not message.text.isdigit():
        await message.answer("Количество дней должно быть целым числом. Попробуйте еще раз.")
        return

    data = await state.get_data()
    user = (await session.execute(select(User).where(User.telegram_id == data['user_telegram_id']))).scalars().first()
    if not user:
        await message.answer("Пользователь не найден. Отмена.")
        await state.clear()
        return

    new_days = int(message.text)
    old_days = user.unassigned_days
    user.unassigned_days = new_days
    await session.commit()
    await state.clear()

    logger.info(f"Admin {message.from_user.id} changed unassigned days for user {user.telegram_id} to {new_days}")
    await message.answer(f"Нераспределенные дни для @{user.username or user.telegram_id} изменены на {new_days}.")
    await cq_user_details(message, session, user)
