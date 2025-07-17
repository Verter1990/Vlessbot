from aiogram import Router, F, Bot
from aiogram.filters import Command, BaseFilter, CommandObject
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from loguru import logger
from datetime import datetime, timedelta

from core.database.models import Server, Tariff, User, Subscription
from core.config import settings
from core.utils.security import encrypt_password

router = Router()

# --- Фильтр администратора ---
class IsAdmin(BaseFilter):
    async def __call__(self, message: Message | CallbackQuery) -> bool:
        admin_ids = [int(admin_id.strip()) for admin_id in settings.ADMIN_IDS.split(',')]
        return message.from_user.id in admin_ids

# --- FSM для добавления/поиска ---
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
    # Find User
    find_user = State()

router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())

# --- Клавиатуры ---

async def get_main_admin_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🖥️ Управление серверами", callback_data="admin_servers_menu")],
        [InlineKeyboardButton(text="💵 Управление тарифами", callback_data="admin_tariffs_menu")],
        [InlineKeyboardButton(text="👤 Управление пользователями", callback_data="admin_users_menu")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")]
    ])

async def get_servers_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Список серверов", callback_data="admin_list_servers")],
        [InlineKeyboardButton(text="➕ Добавить сервер", callback_data="admin_add_server_start")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_main_menu")]
    ])

async def get_tariffs_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Список тарифов", callback_data="admin_list_tariffs")],
        [InlineKeyboardButton(text="➕ Добавить тариф", callback_data="admin_add_tariff_start")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_main_menu")]
    ])

async def get_users_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Найти пользователя", callback_data="admin_find_user_start")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_main_menu")]
    ])

# --- Главное меню админки ---

@router.message(Command("admin"))
async def cmd_admin_panel(message: Message):
    logger.info(f"Admin {message.from_user.id} accessed the admin panel.")
    keyboard = await get_main_admin_keyboard()
    await message.answer("<b>Панель администратора</b>", reply_markup=keyboard)

@router.callback_query(F.data == "admin_main_menu")
async def cq_admin_panel(callback: CallbackQuery):
    await callback.answer()
    keyboard = await get_main_admin_keyboard()
    await callback.message.edit_text("<b>Панель администратора</b>", reply_markup=keyboard)

# --- Отмена FSM ---

@router.message(Command("cancel"))
@router.callback_query(F.data == "admin_cancel_fsm")
async def cancel_handler(event: Message | CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        if isinstance(event, CallbackQuery):
            await event.answer()
            await event.message.edit_text("Нет активных действий для отмены.")
        else:
            await event.answer("Нет активных действий для отмены.")
        return

    logger.info(f"Admin {event.from_user.id} cancelled state {current_state}")
    await state.clear()
    
    if isinstance(event, CallbackQuery):
        await event.answer("Действие отменено.")
        keyboard = await get_main_admin_keyboard()
        await event.message.edit_text("<b>Панель администратора</b>", reply_markup=keyboard)
    else:
        await event.answer("Действие отменено.")

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

    await session.delete(tariff)
    await session.commit()
    logger.info(f"Admin {callback.from_user.id} deleted tariff {tariff_id}")
    await callback.answer(f"Тариф ID {tariff_id} удален.", show_alert=True)
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
        f"ID: <code>{user.telegram_id}</code>\n"
        f"Username: @{user.username if user.username else 'Не указан'}\n"
        f"Язык: {user.language_code}\n"
        f"Нераспределенные дни: {user.unassigned_days}\n"
        f"Реферальный баланс: {user.referral_balance / 100} RUB\n"
        f"L2 Реферальный баланс: {user.l2_referral_balance / 100} RUB\n"
        f"Использован пробный период: {'Да' if user.trial_used else 'Нет'}\n"
        f"Активирован первый VPN: {'Да' if user.activated_first_vpn else 'Нет'}\n"
        f"Реферер ID: {user.referrer_id if user.referrer_id else 'Нет'}\n"
        f"Реферальный код: {user.referral_code if user.referral_code else 'Нет'}\n"
        f"Создан: {user.created_at.strftime('%Y-%m-%d %H:%M')}\n"
        f"<b>Подписки:</b>\n{subs_text}"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад к управлению пользователями", callback_data="admin_users_menu")],
        [InlineKeyboardButton(text="⬅️ Главное меню админки", callback_data="admin_main_menu")]
    ])
    await user_message.answer(user_info, reply_markup=keyboard)