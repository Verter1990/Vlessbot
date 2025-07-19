from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

# --- Клавиатура выбора ОС ---
def get_os_selection_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="📱 iPhone (iOS)", callback_data="info_ios"),
            InlineKeyboardButton(text="📱 Android", callback_data="info_android")
        ],
        [
            InlineKeyboardButton(text="💻 Windows", callback_data="info_windows"),
            InlineKeyboardButton(text="💻 macOS", callback_data="info_macos")
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main_menu") # Эта кнопка будет обрабатываться в user_handlers
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# --- Тексты инструкций ---

INSTRUCTIONS = {
    "ios": """
<b><u>Инструкция для iPhone / iPad (iOS)</u></b>

Для подключения мы рекомендуем одно из этих приложений:

• <b>FoXray</b> (<a href="https://apps.apple.com/us/app/foxray/id6448898396">App Store</a>) - бесплатное, простое и удобное.
• <b>Shadowrocket</b> (<a href="https://apps.apple.com/us/app/shadowrocket/id932747118">App Store</a>) - платное, но очень мощное и популярное.

<b><u>Пошаговая настройка (на примере FoXray):</u></b>
1. Установите приложение FoXray из App Store.
2. Вернитесь в этот чат и скопируйте вашу VLESS-ссылку (просто нажмите на нее).
3. Откройте FoXray. Приложение автоматически обнаружит ссылку в буфере обмена и предложит добавить сервер. Согласитесь.
   <i>[Скриншот: Окно FoXray с предложением добавить ключ]</i>
4. Нажмите на большую круглую кнопку в центре для подключения. При первом запуске приложение попросит разрешение на добавление конфигурации VPN. Разрешите.
   <i>[Скриншот: Главный экран FoXray с кнопкой подключения]</i>
5. Готово! Вверху экрана вашего iPhone появится значок [VPN].

⚠️ <b>Частые проблемы:</b>
- <i>Интернет не работает после подключения:</i> Попробуйте перезагрузить телефон или переключить авиарежим.
- <i>Приложение не видит ссылку:</i> Убедитесь, что вы скопировали ссылку полностью.
""",
    "android": """
<b><u>Инструкция для Android</u></b>

1. Установите приложение <b>v2rayNG</b> из <a href="https://play.google.com/store/apps/details?id=com.v2ray.ang">Google Play</a>.
   <i>(Если Google Play недоступен, скачайте .apk с <a href="https://github.com/2dust/v2rayNG/releases/latest">GitHub</a>).</i>
2. Вернитесь в этот чат и скопируйте вашу VLESS-ссылку (просто нажмите на нее).
3. Откройте v2rayNG. Нажмите на иконку <b>"+"</b> в правом верхнем углу.
   <i>[Скриншот: Главный экран v2rayNG с кнопкой "+"]</i>
4. Выберите в меню <b>"Import config from Clipboard"</b> (Импорт из буфера обмена).
   <i>[Скриншот: Меню после нажатия на "+"]</i>
5. Ваш ключ появится в списке. Нажмите на него, чтобы он выделился.
6. Нажмите на большую круглую кнопку с логотипом "V" внизу справа для подключения. Она станет зеленой.
   <i>[Скриншот: Кнопка подключения в v2rayNG]</i>
7. Готово! В строке состояния появится значок ключа [VPN].

⚠️ <b>Частые проблемы:</b>
- <i>Интернет не работает:</i> В настройках v2rayNG (три полоски слева) убедитесь, что в разделе "VPN routing" (Маршрутизация) не включены специфические правила, блокирующие трафик.
- <i>Ошибка "invalid config":</i> Убедитесь, что вы скопировали ссылку полностью.
""",
    "windows": """
<b><u>Инструкция для Windows</u></b>

1. Скачайте приложение <b>v2rayN</b> с <a href="https://github.com/2dust/v2rayN/releases/latest">GitHub</a>.
   <i>(Вам нужен файл с названием <b>v2rayN-Core.zip</b>).</i>
2. Распакуйте скачанный архив в удобную папку (например, на Рабочий стол).
3. Запустите файл <b>v2rayN.exe</b>.
4. Вернитесь в этот чат и скопируйте вашу VLESS-ссылку.
5. Откройте окно программы v2rayN и нажмите на клавиатуре <b>Ctrl+V</b>. Ваш ключ автоматически добавится в список серверов.
   <i>[Скриншот: Главное окно v2rayN со списком серверов]</i>
6. В системном трее (возле часов, в правом нижнем углу экрана) найдите синюю иконку "V". Нажмите на нее <u>правой кнопкой мыши</u>.
   <i>[Скриншот: Иконка v2rayN в трее]</i>
7. В появившемся меню выберите <b>"System Proxy"</b> -> <b>"Set system proxy"</b>.
   <i>[Скриншот: Контекстное меню с выбором системного прокси]</i>
8. Готово! Иконка в трее станет красной, а весь ваш трафик будет защищен.

⚠️ <b>Частые проблемы:</b>
- <i>Иконка не становится красной:</i> Убедитесь, что вы выбрали сервер в главном окне программы (нажмите на него левой кнопкой мыши).
- <i>Сайты не открываются:</i> Проверьте, что в меню "System Proxy" выбрано "Set system proxy", а не "Clear system proxy".
""",
    "macos": """
<b><u>Инструкция для macOS</u></b>

Мы рекомендуем использовать приложение <b>V2RayU</b>.

1. Скачайте последнюю версию V2RayU с <a href="https://github.com/yanue/V2RayU/releases/latest">GitHub</a>.
   <i>(Вам нужен файл с расширением <b>.dmg</b>).</i>
2. Установите приложение, перетащив его в папку "Applications".
3. Запустите V2RayU. Его иконка появится в строке меню (вверху экрана).
4. Вернитесь в этот чат и скопируйте вашу VLESS-ссылку.
5. Нажмите на иконку V2RayU в строке меню, выберите <b>"Subscribe"</b> -> <b>"Subscribe settings"</b>. Вставьте ссылку в поле "url" и нажмите "Update".
   <i>Либо проще: нажмите на иконку, выберите "Import from pasteboard".</i>
   <i>[Скриншот: Меню V2RayU с пунктом "Import"]</i>
6. После импорта снова нажмите на иконку, выберите <b>"Server"</b> и кликните на добавленный сервер.
7. Включите VPN, выбрав <b>"Turn V2RayU On"</b>.
   <i>[Скриншот: Главное меню V2RayU с переключателем]</i>
8. Готово!

⚠️ <b>Частые проблемы:</b>
- <i>Не работает интернет:</i> Убедитесь, что в меню V2RayU выбран режим "Global Mode".
- <i>Сервер не появляется после импорта:</i> Попробуйте обновить подписку вручную через меню "Subscribe".
"""
}

# --- Обработчики для каждой ОС ---

@router.callback_query(F.data.startswith("info_"))
async def show_instruction(callback: CallbackQuery):
    os_type = callback.data.split("_")[1]
    instruction_text = INSTRUCTIONS.get(os_type, "Инструкция не найдена.")
    
    # Клавиатура для возврата к выбору ОС
    back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад к выбору ОС", callback_data="how_to_connect")]
    ])
    
    await callback.message.edit_text(
        instruction_text,
        reply_markup=back_keyboard,
        disable_web_page_preview=True
    )
    await callback.answer()

# Обработчик для кнопки "Как подключиться?" (показывает меню выбора ОС)
@router.callback_query(F.data == "how_to_connect")
async def how_to_connect_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выберите вашу операционную систему:",
        reply_markup=get_os_selection_keyboard()
    )
    await callback.answer()
