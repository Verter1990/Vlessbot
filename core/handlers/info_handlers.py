from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from core.locales.translations import get_text
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()

async def get_os_selection_keyboard(lang: str) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text=get_text('btn_ios', lang), callback_data="info_ios"),
            InlineKeyboardButton(text=get_text('btn_android', lang), callback_data="info_android")
        ],
        [
            InlineKeyboardButton(text=get_text('btn_windows', lang), callback_data="info_windows"),
            InlineKeyboardButton(text=get_text('btn_macos', lang), callback_data="info_macos")
        ],
        [
            InlineKeyboardButton(text=get_text('btn_back', lang), callback_data="main_menu")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_instruction_text(os_type: str, lang: str) -> str:
    if os_type == 'ios':
        return "\n".join([
            get_text('info_title_ios', lang),
            "",
            get_text('info_app_recommendation_ios', lang),
            get_text('info_app_foxray', lang),
            get_text('info_app_shadowrocket', lang),
            "",
            get_text('info_setup_title_ios', lang),
            get_text('info_step1_ios', lang),
            get_text('info_step2_ios', lang),
            get_text('info_step3_ios', lang),
            get_text('info_step4_ios', lang),
            get_text('info_step5_ios', lang),
            "",
            get_text('info_faq_title', lang),
            get_text('info_faq1_ios', lang),
            get_text('info_faq2_ios', lang),
        ])
    elif os_type == 'android':
        return "\n".join([
            get_text('info_title_android', lang),
            "",
            get_text('info_step1_android', lang),
            get_text('info_step1_alt_android', lang),
            get_text('info_step2_android', lang),
            get_text('info_step3_android', lang),
            get_text('info_step4_android', lang),
            get_text('info_step5_android', lang),
            get_text('info_step6_android', lang),
            get_text('info_step7_android', lang),
            "",
            get_text('info_faq_title', lang),
            get_text('info_faq1_android', lang),
            get_text('info_faq2_android', lang),
        ])
    elif os_type == 'windows':
        return "\n".join([
            get_text('info_title_windows', lang),
            "",
            get_text('info_step1_windows', lang),
            get_text('info_step1_alt_windows', lang),
            get_text('info_step2_windows', lang),
            get_text('info_step3_windows', lang),
            get_text('info_step4_windows', lang),
            get_text('info_step5_windows', lang),
            get_text('info_step6_windows', lang),
            get_text('info_step7_windows', lang),
            get_text('info_step8_windows', lang),
            "",
            get_text('info_faq_title', lang),
            get_text('info_faq1_windows', lang),
            get_text('info_faq2_windows', lang),
        ])
    elif os_type == 'macos':
        return "\n".join([
            get_text('info_title_macos', lang),
            "",
            get_text('info_app_recommendation_macos', lang),
            get_text('info_step1_macos', lang),
            get_text('info_step1_alt_macos', lang),
            get_text('info_step2_macos', lang),
            get_text('info_step3_macos', lang),
            get_text('info_step4_macos', lang),
            get_text('info_step5_macos', lang),
            get_text('info_step6_macos', lang),
            get_text('info_step7_macos', lang),
            get_text('info_step8_macos', lang),
            "",
            get_text('info_faq_title', lang),
            get_text('info_faq1_macos', lang),
            get_text('info_faq2_macos', lang),
        ])
    return "Инструкция не найдена."

@router.callback_query(F.data.startswith("info_"))
async def show_instruction(callback: CallbackQuery, session: AsyncSession):
    from .user_handlers import _get_user_and_lang # Local import to avoid circular dependency
    user, lang = await _get_user_and_lang(session, callback.from_user.id)

    os_type = callback.data.split("_")[1]
    instruction_text = get_instruction_text(os_type, lang)
    
    back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text('btn_back_to_os_selection', lang), callback_data="how_to_connect")]
    ])
    
    await callback.message.edit_text(
        instruction_text,
        reply_markup=back_keyboard,
        disable_web_page_preview=True
    )
    await callback.answer()

@router.callback_query(F.data == "how_to_connect")
async def how_to_connect_menu(callback: CallbackQuery, session: AsyncSession):
    from .user_handlers import _get_user_and_lang # Local import to avoid circular dependency
    user, lang = await _get_user_and_lang(session, callback.from_user.id)

    keyboard = await get_os_selection_keyboard(lang)
    await callback.message.edit_text(
        get_text('info_os_selection_title', lang),
        reply_markup=keyboard
    )
    await callback.answer()