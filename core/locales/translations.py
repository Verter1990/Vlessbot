# core/locales/translations.py

translations = {
    'ru': {
        # Dynamic content from DB
        'db_content': {
            "Неделя": "Неделя",
            "Месяц": "Месяц",
            "Год": "Год",
            "Нидерланды": "Нидерланды",
        },

        # General
        'error_generic': "Произошла ошибка. Попробуйте позже.",
        'btn_main_menu': "Главное меню",
        'btn_back': "Назад",
        'user_not_found_error': "Произошла ошибка, пользователь не найден.",
        'tariff_not_found': "Произошла ошибка. Тариф не найден.",

        # Language Selection
        'select_language': "Пожалуйста, выберите язык:",
        'language_changed': "Язык изменен на русский.",

        # New Welcome Message
        'welcome_new_user': '''Что может делать этот бот?
Представляем наш VPN сервис: быстрый, стабильный и простой в использовании. Забудьте про все блокировки! Пользуйтесь доступом на любом устройстве: iOS, Android, MacOS, Windows
Поехали? Нажмите кнопку внизу''',
        'btn_start_bot': "Поехали!",

        # Main Menu (/start)
        'welcome': "Привет, {full_name}! Это главное меню.",
        'subscription_active_until': '''

Ваша подписка активна до: **{expiry_date}**''',
        'no_active_subscription': '''

У вас пока нет активной подписки.''',
        'unassigned_days': '''
У вас есть **{days}** неиспользованных дней VPN-доступа.''',
        'referral_stats': '''

Вы пригласили: **{referrals}** чел.
Заработано: **{earnings:.2f} руб.**''',
        'btn_setup_vpn': "⚙️ Настроить VPN",
        'btn_pay_subscription': "💰 Оплатить подписку",
        'btn_referral_program': "🤝 Партнёрская программа",
        'btn_why_vpn': "Чем лучше наш VPN?",
        'btn_get_free_vpn': "Получить бесплатный VPN на 3 дня",
        'btn_help': "❓ Нужна помощь?",
        'btn_terms_of_use': "Правила использования",

        # Gift/Referral activation
        'referral_bonus_applied': "Вы пришли по приглашению! Вам начислено 100 бонусных рублей.",
        'gift_activated': '''✅ Подарок успешно активирован!
На ваш баланс зачислено **{days}** дней подписки.''',
        'gift_not_found_or_used': "❌ Этот подарочный код не найден или уже был использован.",
        'gift_activation_error': "❌ Произошла ошибка при активации подарка: тариф не найден.",

        # VPN Setup
        'select_server_for_setup': "Выберите сервер для настройки:",
        'vpn_setup_instructions': '''Как настроить?
1️⃣Нажмите страну(сервер) ниже
2️⃣Скачайте предложенное приложение
3️⃣Вернитесь в бота и нажмите "Добавить ключ"

Чтобы Ютуб был ускорен и без рекламы - выбирайте YouTubeNoAds

Нужна помощь? {support_chat_link} - ответим за 7 минут.''',
        'no_servers_available': "Извините, в данный момент нет доступных серверов.",
        'server_or_user_not_found': "Произошла ошибка. Пользователь или сервер не найден.",
        'vpn_key_info': '''У вас уже есть активная подписка на {server_name}.
Ваш ключ VPN: <code>{vless_link}</code>
Срок действия до: {expiry_date}''',
        'show_subscription_error': "Произошла непредвиденная ошибка при отображении вашей подписки. Пожалуйста, попробуйте позже.",
        'no_active_subscription_for_server': "У вас нет активной подписки на {server_name}. Выберите способ активации:",
        'btn_activate_unassigned_days': "Активировать {days} дней (бесплатно)",
        'btn_pay_from_referral_balance': "Оплатить с реферального баланса ({balance:.2f} руб.)",
        'btn_select_tariff_for_payment': "Выбрать тариф для оплаты",
        'btn_back_to_server_selection': "Назад к выбору сервера",

        # Referral Balance Payment
        'referral_balance_menu_title': '''Ваш реферальный баланс: {balance:.2f} руб.
Выберите тариф для оплаты:''',
        'referral_payment_insufficient_funds': "У вас недостаточно средств ({balance:.2f} руб.) на реферальном балансе для покупки любого тарифа.",
        'referral_payment_error': "Произошла ошибка. Пользователь, тариф или сервер не найдены.",
        'referral_payment_insufficient_funds_for_tariff': "У вас недостаточно средств на реферальном балансе.",
        'referral_payment_success': '''✅ Подписка на **{tariff_name}** успешно активирована с вашего реферального баланса!

Ваш ключ для сервера **{server_name}**:
<code>{vless_link}</code>

Он будет действовать **{days}** дней.''',
        'referral_payment_activation_error': "Произошла ошибка при активации подписки. Пожалуйста, попробуйте позже.",

        # Unassigned Days Activation
        'no_unassigned_days': "У вас нет неиспользованных дней для активации.",
        'unassigned_days_activation_success': '''✅ Ваши неиспользованные дни активированы для сервера **{server_name}**!

Ваш ключ VPN: <code>{vless_link}</code>

Инструкции по подключению: ...''',
        'unassigned_days_activation_error': "Произошла ошибка при активации дней. Пожалуйста, попробуйте позже.",

        # Payment
        'choose_tariff': "Выберите тариф:",
        'no_tariffs_available': "Извините, в данный момент нет доступных тарифов.",
        'tariff_selection_title': '''<b>{tariff_name}</b> - {price:.2f} ₽ за доступ к премиум версии сроком на {days} дней.

Пожалуйста, выберите способ оплаты:''',
        'btn_pay_card': "Оплатить {price:.2f} ₽ (Картой)",
        'btn_pay_stars': "Оплатить {stars} ⭐️",
        'btn_pay_transfer': "Оплата переводом",
        'btn_pay_crypto': "Оплатить криптовалютой",
        'btn_back_to_tariffs': "Выбор тарифа",
        'crypto_payment_info': '''Оплата криптовалютой доступна только на год со скидкой 25%!

Оплатите на один из кошельков <b>{price_usd} USD</b> (или эквивалент в крипте):

BTC: <code>{btc_address}</code>
ETH (ERC-20): <code>{eth_address}</code>
USDT (TRC-20): <code>{usdt_address}</code>

И пришлите ссылку на транзакцию или чек к нам в службу поддержки ⬇️''',
        'btn_send_check_to_support': "Отправить чек в техподдержку",
        'stars_payment_unavailable': "Извините, оплата звездами в данный момент недоступна.",
        'invoice_title_subscription': "Подписка: {tariff_name}",
        'invoice_description_subscription': "Доступ к VPN на {days} дней.",
        'invoice_label_subscription': "{tariff_name} ({days} дней)",
        'payment_error_server_not_found': "Произошла ошибка при обработке вашего платежа (сервер не найден). Пожалуйста, свяжитесь с поддержкой.",
        'payment_success_key_created': '''✅ Оплата прошла успешно!

Ваш ключ для сервера **{server_name}** готов:
<code>{vless_link}</code>

Он будет действовать **{days}** дней.

Инструкции по подключению: ...''',
        'payment_success_key_error': "К сожалению, произошла ошибка при создании вашего VPN ключа после оплаты. Пожалуйста, свяжитесь с поддержкой, мы все решим.",
        'payment_success_days_added': '''✅ Оплата прошла успешно!

На ваш баланс зачислено **{days}** неиспользованных дней VPN-доступа.

Теперь вы можете перейти в раздел "Настроить VPN" и выбрать любой сервер для получения ключа.

Инструкции по подключению: ...''',
        'gift_purchase_success': '''✅ Оплата прошла успешно!

Вы приобрели в подарок подписку: **{tariff_name}**.

Перешлите это сообщение или ссылку ниже тому, кому вы дарите подписку:
<code>{gift_link}</code>''',
        'payment_payload_parse_error': "Произошла ошибка при обработке вашего платежа. Пожалуйста, свяжитесь с поддержкой.",
        'payment_unexpected_error': "Произошла непредвиденная ошибка. Пожалуйста, свяжитесь с поддержкой.",

        # Trial
        'trial_already_used': "Вы уже использовали свой бесплатный пробный период. Чтобы продолжить пользоваться сервисом, пожалуйста, оформите подписку.",
        'trial_unavailable': "Извините, пробный период временно недоступен. Пожалуйста, попробуйте позже.",
        'trial_server_unavailable': "Извините, пробный сервер временно недоступен. Пожалуйста, попробуйте позже.",
        'trial_key_creation_wait': "Пожалуйста, подождите, мы создаем для вас пробный ключ...",
        'trial_key_creation_success': 'Ваш пробный ключ на 3 дня: <code>{vless_link}</code>

Инструкции по подключению: ...',
        'trial_key_creation_error': "Произошла ошибка при создании пробного ключа. Обратитесь в поддержку.",

        # Referral Program
        'ref_program_title': "<b>Условия партнерской программы</b>",
        'ref_program_conditions': '30% от оплат рефералов и 5% от оплат рефералов второго уровня + 15 дней за каждого приглашенного кто запустил VPN',
        'ref_program_withdrawal': "Вывод денег от 1000 руб., для вывода обратитесь в техническую поддержку.",
        'ref_total_referrals': "<b>Всего рефералов:</b> {count}",
        'ref_last_10': "(Последние 10: {logins})",
        'ref_not_activated': "<b>Не запустили VPN:</b>",
        'ref_no_inactive_referrals': "(Нет таких)",
        'ref_activation_info': "Чтобы стать полноценным рефералом и дать вам бонусное время ваш приглашенный должен начать использование сервиса и запустить VPN",
        'ref_friend_bonus_info': "Каждому вашему другу будет начислено 100 рублей на реферальный баланс.",
        'ref_balance_info': "<b>Реферальный баланс:</b> {total_balance:.2f} руб. (из них {l2_balance:.2f} руб. за рефералов второго уровня) руб.",
        'ref_bonus_days_info': "<b>Бонусных дней за рефералов:</b> {days}.",
        'ref_paid_out_info': "<b>Всего выплачено:</b> {total_paid_out:.2f} руб.",
        'ref_copy_link_info': "Скопируйте партнёрскую ссылку:",
        'ref_create_invite_info': '''Или нажмите на кнопку "Создать приглашение" ниже, и перешлите то что вам напишет бот другу:''',
        'btn_gift_subscription': "Подарить подписку",
        'btn_create_invitation': "Создать приглашение",

        # Gift Subscription
        'gift_subscription_unavailable': "Извините, возможность подарить подписку в данный момент недоступна.",
        'gift_purchase_title': "Вы можете подарить ПРО подписку другому пользователю.",
        'gift_purchase_instructions': '''<b>{price:.2f} ₽</b> за доступ к премиум версии SiriusVPN сроком на <b>{days} дней</b>, будет куплено в подарок.

Вы можете оплатить картой онлайн или обратиться в техническую поддержку и получить реквизиты для оплаты подарка на год криптой или переводом.

После оплаты бот пришлет вам сообщение с подарком. Перешлите его тому кому вы его дарите.''',
        'btn_pay_gift_card': "Оплатить {price:.2f} ₽ (Картой)",
        'btn_pay_gift_stars': "Оплатить {stars} ⭐️",
        'btn_contact_support_for_gift': "Обратиться в техподдержку",
        'btn_back_to_referral_menu': "Назад в меню партнера",
        'invoice_title_gift': "Подарок: {tariff_name}",
        'invoice_description_gift': "Подарочная подписка на {days} дней.",
        'invoice_label_gift': "Подарок: {tariff_name}",

        # Placeholders & TBD
        'tbd': "Эта функция находится в разработке.",
        'support_info': "Для помощи обратитесь в поддержку.",
        'support_redirect_message': "Нажмите на кнопку ниже, чтобы перейти в наш бот технической поддержки.",
        'btn_go_to_support_chat': "Перейти в бот поддержки",
        'help_message_full': """Здравствуйте! Перед созданием заявки, пожалуйста, внимательно ознакомьтесь с инструкциями и  решениями основных возможных ошибок на нашем портале поддержки

1️⃣⚠️ Как подключить VPN на вашем устройстве
   - https://vpn-help.notion.site/

2️⃣⚠️ Если не работает, попробуйте сначала обновить подписку в приложении и перезагрузить его: https://t.me/siriusvpn/90 (есть также в инструкциях по для вашего приложения по ссылке выше)

Статус Сервиса:  все сервера в норме. 

⚠️ВНИМАНИЕ! Из-за блокировок YouTube в РФ служба поддержки работает с перегрузкой. Если вам не помогли, или ответ не понятен — значит техподдержка потеряла вашу заявку. Напишите ваш вопрос еще раз. Спасибо за понимание⚠️

Также пожалуйста проверьте пожалуйста есть ли необходимая инструкция и, возможно, ответ на ваш вопрос в разделе ЧаВо на нашем портале технической поддержки https://vpn-help.notion.site/

⬇️ Если у вас другая проблема, напишите нам. ⬇️

Обязательно приложите скриншот ошибки и настроек из вашего VPN-приложения. Это нужно чтобы мы могли понять какое устройство вы настраиваете и в чем именно проблема.""",
        'terms_of_use_full': '''Контакты для связи(отзывы, пожелания, предложения, ошибки): {support_chat_link}

Для возврата платежа обращайтесь в наш бот поддержки https://t.me/Stena_VPN_helpbot
Стоимость подписки: 99 ₽ в месяц, снимается автоматически если вы не удалили карту.
Для отмены платной подписки и удаления карты нажмите на кнопку "Отменить подписку" ниже. Доступ согласно оплаченного периода будет сохранен.

Продолжая использование бота вы соглашаетесь с нашим
<a href="{terms_of_service_url}">лицензионным соглашением</a> и <a href="{privacy_policy_url}">политикой обработки персональных данных</a>''',
        'btn_cancel_subscription': "Отменить подписку",
        'payment_card_unavailable': "Оплата картой временно недоступна.",
        'payment_transfer_unavailable': "Оплата переводом временно недоступна.",
        'payment_gift_card_unavailable': "Оплата картой для подарка временно недоступна.",

        # YooKassa Integration
        'payment_redirect_info': "Вы будете перенаправлены на страницу оплаты. Нажмите на кнопку ниже, чтобы продолжить.",
        'btn_go_to_payment': "Перейти к оплате",
        # --- Redesign --- 
        'btn_my_keys': "🔑 Мои ключи",
        'btn_my_profile': "👤 Мой профиль",
        'btn_extend_subscription': "➕ Продлить/Расширить подписку",
        'btn_activate_days': "🌟 Активировать {days} дней",
        'btn_how_it_works': "❓ Как это работает?",
        'my_profile_title': "<b>👤 Мой профиль</b>",
        'my_profile_info': '''
<b>ID:</b> <code>{user_id}</code>
<b>Дней на балансе:</b> {unassigned_days}
<b>Реферальный баланс:</b> {ref_balance:.2f} руб.
<b>Приглашено:</b> {ref_count} чел.''',
        'my_keys_title': "<b>🔑 Мои активные ключи</b>",
        'my_keys_no_keys': "У вас пока нет активных ключей.",
        'my_keys_item': '''

Сервер: <b>{server_name}</b>
Истекает: {expires_at}''',
        'btn_show_key': "Показать ключ",
    },
    'en': {
        # Dynamic content from DB
        'db_content': {
            "Неделя": "Week",
            "Месяц": "Month",
            "Год": "Year",
            "Нидерланды": "Netherlands",
        },

        # General
        'error_generic': "An error occurred. Please try again later.",
        'btn_main_menu': "Main Menu",
        'btn_back': "Back",
        'user_not_found_error': "An error occurred, user not found.",
        'tariff_not_found': "An error occurred. Tariff not found.",

        # Language Selection
        'select_language': "Please select a language:",
        'language_changed': "Language changed to English.",

        # New Welcome Message
        'welcome_new_user': '''What can this bot do?
Introducing our VPN service: fast, stable, and easy to use. Forget about all blockages! Enjoy access on any device: iOS, Android, MacOS, Windows
Ready to go? Press the button below''',
        'btn_start_bot': "Let's go!",

        # Main Menu (/start)
        'welcome': "Hello, {full_name}! This is the main menu.",
        'subscription_active_until': "

Your subscription is active until: **{expiry_date}**",
        'no_active_subscription': "
You don't have an active subscription yet.",
        'unassigned_days': "
You have **{days}** unused days of VPN access.",
        'referral_stats': "

You have invited: **{referrals}** people.
Earned: **{earnings:.2f} RUB.**",
        'btn_setup_vpn': "⚙️ Setup VPN",
        'btn_pay_subscription': "💰 Pay for subscription",
        'btn_referral_program': "🤝 Referral Program",
        'btn_why_vpn': "Why is our VPN better?",
        'btn_get_free_vpn': "Get free VPN for 3 days",
        'btn_help': "❓ Need help?",
        'btn_terms_of_use': "Terms of Use",

        # Gift/Referral activation
        'referral_bonus_applied': "You have joined via a referral link! You've been credited 100 bonus rubles.",
        'gift_activated': "✅ Gift activated successfully!
**{days}** subscription days have been added to your balance.",
        'gift_not_found_or_used': "❌ This gift code was not found or has already been used.",
        'gift_activation_error': "❌ An error occurred while activating the gift: the tariff was not found.",

        # VPN Setup
        'select_server_for_setup': "Select a server to set up:",
        'vpn_setup_instructions': '''How to set up?
1️⃣Click the country (server) below
2️⃣Download the suggested application
3️⃣Return to the bot and click "Add key"

To make YouTube faster and ad-free - choose YouTubeNoAds

Need help? {support_chat_link} - we will respond in 7 minutes.''',
        'no_servers_available': "Sorry, there are no available servers at the moment.",
        'server_or_user_not_found': "An error occurred. User or server not found.",
        'vpn_key_info': "You already have an active subscription for {server_name}.
Your VPN key: <a href=\"{vless_link}\">{vless_link}</a>
Expires on: {expiry_date}",
        'show_subscription_error': "An unexpected error occurred while displaying your subscription. Please try again later.",
        'no_active_subscription_for_server': "You don't have an active subscription for {server_name}. Choose an activation method:",
        'btn_activate_unassigned_days': "Activate {days} days (free)",
        'btn_pay_from_referral_balance': "Pay from referral balance ({balance:.2f} RUB)",
        'btn_select_tariff_for_payment': "Select a tariff for payment",
        'btn_back_to_server_selection': "Back to server selection",

        # Referral Balance Payment
        'referral_balance_menu_title': '''Your referral balance: {balance:.2f} RUB.
Choose a tariff to pay:''',
        'referral_payment_insufficient_funds': "You have insufficient funds ({balance:.2f} RUB) in your referral balance to purchase any tariff.",
        'referral_payment_error': "An error occurred. User, tariff or server not found.",
        'referral_payment_insufficient_funds_for_tariff': "You have insufficient funds in your referral balance.",
        'referral_payment_success': "✅ Subscription for **{tariff_name}** has been successfully activated from your referral balance!

Your key for server **{server_name}**:
<a href=\"{vless_link}\">{vless_link}</a>

It will be valid for **{days}** days.",
        'referral_payment_activation_error': "An error occurred while activating the subscription. Please try again later.",

        # Unassigned Days Activation
        'no_unassigned_days': "You have no unused days to activate.",
        'unassigned_days_activation_success': "✅ Your unused days have been activated for server **{server_name}**!

Your VPN key: <a href=\"{vless_link}\">{vless_link}</a>

Connection instructions: ...",
        'unassigned_days_activation_error': "An error occurred while activating the days. Please try again later.",

        # Payment
        'choose_tariff': "Choose a tariff:",
        'no_tariffs_available': "Sorry, there are no available tariffs at the moment.",
        'tariff_selection_title': "<b>{tariff_name}</b> - {price:.2f} RUB for premium access for {days} days.

Please choose a payment method:",
        'btn_pay_card': "Pay {price:.2f} RUB (Card)",
        'btn_pay_stars': "Pay {stars} ⭐️",
        'btn_pay_transfer': "Bank Transfer",
        'btn_pay_crypto': "Pay with Cryptocurrency",
        'btn_back_to_tariffs': "Choose tariff",
        'crypto_payment_info': "Cryptocurrency payment is available only for a year with a 25% discount!

Pay <b>{price_usd} USD</b> (or the equivalent in crypto) to one of the wallets:

BTC: <code>{btc_address}</code>
ETH (ERC-20): <code>{eth_address}</code>
USDT (TRC-20): <code>{usdt_address}</code>

And send the transaction link or receipt to our support service ⬇️",
        'btn_send_check_to_support': "Send receipt to support",
        'stars_payment_unavailable': "Sorry, payment with stars is currently unavailable.",
        'invoice_title_subscription': "Subscription: {tariff_name}",
        'invoice_description_subscription': "VPN access for {days} days.",
        'invoice_label_subscription': "{tariff_name} ({days} days)",
        'payment_error_server_not_found': "An error occurred while processing your payment (server not found). Please contact support.",
        'payment_success_key_created': "✅ Payment successful!

Your key for server **{server_name}** is ready:
<code>{vless_link}</code>

It will be valid for **{days}** days.

Connection instructions: ...",
        'payment_success_key_error': "Unfortunately, an error occurred while creating your VPN key after payment. Please contact support, we will solve it.",
        'payment_success_days_added': "✅ Payment successful!

**{days}** unused days of VPN access have been credited to your balance.

You can now go to the "Setup VPN" section and select any server to get a key.

Connection instructions: ...",
        'gift_purchase_success': "✅ Payment successful!

You have purchased a gift subscription: **{tariff_name}**.

Forward this message or the link below to the person you are gifting the subscription to:
<code>{gift_link}</code>",
        'payment_payload_parse_error': "An error occurred while processing your payment. Please contact support.",
        'payment_unexpected_error': "An unexpected error occurred. Please contact support.",

        # Trial
        'trial_already_used': "You have already used your free trial period. To continue using the service, please purchase a subscription.",
        'trial_unavailable': "Sorry, the trial period is temporarily unavailable. Please try again later.",
        'trial_server_unavailable': "Sorry, the trial server is temporarily unavailable. Please try again later.",
        'trial_key_creation_wait': "Please wait, we are creating a trial key for you...",
        'trial_key_creation_success': "Your trial key for 3 days: <a href=\"{vless_link}\">{vless_link}</a>

Connection instructions: ...",
        'trial_key_creation_error': "An error occurred while creating the trial key. Please contact support.",

        # Referral Program
        'ref_program_title': "<b>Referral Program Terms</b>",        'ref_program_conditions': '''30% from referral payments and 5% from second-level referral payments + 15 days for each invited user who starts the VPN''',        'ref_program_withdrawal': "Withdrawal of funds from 1000 RUB, please contact technical support for withdrawal.",        'ref_total_referrals': "<b>Total referrals:</b> {count}",        'ref_last_10': "(Last 10: {logins})",        'ref_not_activated': "<b>Haven't started VPN:</b>",        'ref_no_inactive_referrals': "(None)",        'ref_activation_info': "To become a full-fledged referral and give you bonus time, your invited friend must start using the service and launch the VPN",        'ref_friend_bonus_info': "Each of your friends will be credited with 100 rubles to their referral balance.",        'ref_balance_info': "<b>Referral balance:</b> {total_balance:.2f} RUB (of which {l2_balance:.2f} RUB is for second-level referrals) RUB.",        'ref_bonus_days_info': "<b>Bonus days from referrals:</b> {days}.",        'ref_paid_out_info': "<b>Total paid out:</b> {total_paid_out:.2f} RUB.",        'ref_copy_link_info': "Copy your partner link:",        'ref_create_invite_info': '''Or click the "Create Invitation" button below and forward what the bot writes to your friend:''',
        'btn_gift_subscription': "Gift a subscription",
        'btn_create_invitation': "Create Invitation",

        # Gift Subscription
        'gift_subscription_unavailable': "Sorry, the option to gift a subscription is currently unavailable.",
        'gift_purchase_title': "You can gift a PRO subscription to another user.",
        'gift_purchase_instructions': "<b>{price:.2f} ₽</b> for premium access to SiriusVPN for <b>{days} days</b>, will be purchased as a gift.

You can pay by card online or contact technical support to get details for paying for a yearly gift with crypto or bank transfer.

After payment, the bot will send you a message with the gift. Forward it to the person you are gifting it to.",
        'btn_pay_gift_card': "Pay {price:.2f} ₽ (Card)",
        'btn_pay_gift_stars': "Pay {stars} ⭐️",
        'btn_contact_support_for_gift': "Contact support",
        'btn_back_to_referral_menu': "Back to referral menu",
        'invoice_title_gift': "Gift: {tariff_name}",
        'invoice_description_gift': "Gift subscription for {days} days.",
        'invoice_label_gift': "Gift: {tariff_name}",

        # Placeholders & TBD
        'tbd': "This feature is under development.",
        'support_info': "For help, please contact support.",
        'support_redirect_message': "Click the button below to go to our support bot.",
        'btn_go_to_support_chat': "Go to Support Bot",
        'terms_info': "Terms of use are under development.",
        'terms_of_use_full': "Contact for communication (feedback, wishes, suggestions, errors): {support_chat_link}

For a refund, contact @SiriusVPNhelpbot
Subscription cost: 99 ₽ per month, automatically debited if you have not deleted the card.
To cancel a paid subscription and delete a card, click the "Cancel subscription" button below. Access according to the paid period will be saved.

By continuing to use the bot, you agree to our
<a href=\"{terms_of_service_url}\">license agreement</a> and <a href=\"{privacy_policy_url}\">privacy policy</a>",
        'btn_cancel_subscription': "Cancel subscription",
        'payment_card_unavailable': "Card payment is temporarily unavailable.",
        'payment_transfer_unavailable': "Bank transfer payment is temporarily unavailable.",
        'payment_gift_card_unavailable': "Gift card payment is temporarily unavailable.",

        # YooKassa Integration
        'payment_redirect_info': "You will be redirected to the payment page. Click the button below to continue.",
        'btn_go_to_payment': "Go to payment",
        'btn_back_to_gift_menu': "Back to gift purchase",

        # --- Instructions ---
        'btn_how_to_connect': "❓ How to connect?",
        'info_os_selection_title': "Select your operating system:",
        'btn_ios': "📱 iPhone (iOS)",
        'btn_android': "📱 Android",
        'btn_windows': "💻 Windows",
        'btn_macos': "💻 macOS",
        'btn_back_to_os_selection': "⬅️ Back to OS selection",
        'key_created_or_updated': "Your key for server **{server_name}** is ready!

<code>{vless_link}</code>

It will be valid until **{expires_at}**.",

        'info_title_ios': "<b><u>Instructions for iPhone / iPad (iOS)</u></b>",
        'info_app_recommendation_ios': "For connection, we recommend one of these applications:",
        'info_app_foxray': "• <b>FoXray</b> (<a href=\"https://apps.apple.com/us/app/foxray/id6448898396\">App Store</a>) - free, simple, and convenient.",
        'info_app_shadowrocket': "• <b>Shadowrocket</b> (<a href=\"https://apps.apple.com/us/app/shadowrocket/id932747118\">App Store</a>) - paid, but very powerful and popular.",
        'info_setup_title_ios': "<b><u>Step-by-step setup (using FoXray as an example):</u></b>",
        'info_step1_ios': "1. Install the FoXray app from the App Store.",
        'info_step2_ios': "2. Return to this chat and copy your VLESS link (just click on it).",
        'info_step3_ios': "3. Open FoXray. The app will automatically detect the link in your clipboard and offer to add the server. Agree.",
        'info_step4_ios': "4. Tap the large round button in the center to connect. On the first launch, the app will ask for permission to add a VPN configuration. Allow it.",
        'info_step5_ios': "5. Done! A [VPN] icon will appear at the top of your iPhone screen.",
        'info_faq_title': "⚠️ <b>Common Issues:</b>",
        'info_faq1_ios': "- <i>Internet not working after connection:</i> Try restarting your phone or toggling airplane mode.",
        'info_faq2_ios': "- <i>App doesn't see the link:</i> Make sure you copied the entire link.",

        'info_title_android': "<b><u>Instructions for Android</u></b>",
        'info_step1_android': "1. Install the <b>v2rayNG</b> app from <a href=\"https://play.google.com/store/apps/details?id=com.v2ray.ang\">Google Play</a>.",
        'info_step1_alt_android': "   <i>(If Google Play is unavailable, download the .apk from <a href=\"https://github.com/2dust/v2rayNG/releases/latest\">GitHub</a>).</i>",
        'info_step2_android': "2. Return to this chat and copy your VLESS link.",
        'info_step3_android': "3. Open v2rayNG. Tap the <b>"+"</b> icon in the top right corner.",
        'info_step4_android': "4. Select <b>"Import config from Clipboard"</b> from the menu.",
        'info_step5_android': "5. Your key will appear in the list. Tap it to select it.",
        'info_step6_android': "6. Tap the large round button with the "V" logo at the bottom right to connect. It will turn green.",
        'info_step7_android': "7. Done! A key icon [VPN] will appear in your status bar.",
        'info_faq1_android': "- <i>Internet not working:</i> In v2rayNG settings (three bars on the left), ensure that no specific traffic-blocking rules are enabled under "VPN routing".",
        'info_faq2_android': "- <i>"Invalid config" error:</i> Make sure you copied the entire link.",

        'info_title_windows': "<b><u>Instructions for Windows</u></b>",
        'info_step1_windows': "1. Download the <b>v2rayN</b> application from <a href=\"https://github.com/2dust/v2rayN/releases/latest\">GitHub</a>.",
        'info_step1_alt_windows': "   <i>(You need the file named <b>v2rayN-Core.zip</b>).</i>",
        'info_step2_windows': "2. Unzip the downloaded archive to a convenient folder (e.g., your Desktop).",
        'info_step3_windows': "3. Run the <b>v2rayN.exe</b> file.",
        'info_step4_windows': "4. Return to this chat and copy your VLESS link.",
        'info_step5_windows': "5. Open the v2rayN program window and press <b>Ctrl+V</b>. Your key will be automatically added to the server list.",
        'info_step6_windows': "6. In the system tray (near the clock, bottom right corner), find the blue "V" icon. <u>Right-click</u> on it.",
        'info_step7_windows': "7. In the context menu, select <b>"System Proxy"</b> -> <b>"Set system proxy"</b>.",
        'info_step8_windows': "8. Done! The tray icon will turn red, and all your traffic will be protected.",
        'info_faq1_windows': "- <i>Icon doesn't turn red:</i> Make sure you have selected a server in the main program window (left-click on it).",
        'info_faq2_windows': "- <i>Websites don't open:</i> Check that "Set system proxy" is selected in the "System Proxy" menu, not "Clear system proxy".",

        'info_title_macos': "<b><u>Instructions for macOS</u></b>",
        'info_app_recommendation_macos': "We recommend using the <b>V2RayU</b> application.",
        'info_step1_macos': "1. Download the latest version of V2RayU from <a href=\"https://github.com/yanue/V2RayU/releases/latest\">GitHub</a>.",
        'info_step1_alt_macos': "   <i>(You need the file with the <b>.dmg</b> extension).</i>",
        'info_step2_macos': "2. Install the application by dragging it to the "Applications" folder.",
        'info_step3_macos': "3. Launch V2RayU. Its icon will appear in the menu bar (at the top of the screen).",
        'info_step4_macos': "4. Return to this chat and copy your VLESS link.",
        'info_step5_macos': "5. Click the V2RayU icon in the menu bar and select <b>"Import from pasteboard"</b>. The key will be added automatically.",
        'info_step6_macos': "6. After importing, click the icon again, select <b>"Server"</b>, and click on the added server.",
        'info_step7_macos': "7. Turn on the VPN by selecting <b>"Turn V2RayU On"</b>.",
        'info_step8_macos': "8. Done!",
        'info_faq1_macos': "- <i>Internet not working:</i> Make sure "Global Mode" is selected in the V2RayU menu.",
        'info_faq2_macos': "- <i>Server doesn't appear after import:</i> Try updating the subscription manually via the "Subscribe" -> "Subscribe settings" -> "Update" menu.",
        # --- Redesign --- 
        'btn_my_keys': "🔑 My Keys",
        'btn_my_profile': "👤 My Profile",
        'btn_extend_subscription': "➕ Extend/Upgrade Subscription",
        'btn_activate_days': "🌟 Activate {days} days",
        'btn_how_it_works': "❓ How it works?",
        'my_profile_title': "<b>👤 My Profile</b>",
        'my_profile_info': '''
<b>ID:</b> <code>{user_id}</code>
<b>Days on balance:</b> {unassigned_days}
<b>Referral balance:</b> {ref_balance:.2f} RUB
<b>Invited:</b> {ref_count} users''',
        'my_keys_title': "<b>🔑 My Active Keys</b>",
        'my_keys_no_keys': "You have no active keys yet.",
        'my_keys_item': '''

Server: <b>{server_name}</b>
Expires: {expires_at}''',
        'btn_show_key': "Show Key"
    }
}

        # --- Instructions ---
        'btn_how_to_connect': "❓ Как подключиться?",
        'info_os_selection_title': "Выберите вашу операционную систему:",
        'btn_ios': "📱 iPhone (iOS)",
        'btn_android': "📱 Android",
        'btn_windows': "💻 Windows",
        'btn_macos': "💻 macOS",
        'btn_back_to_os_selection': "⬅️ Назад к выбору ОС",
        'key_created_or_updated': '''Ваш ключ для сервера **{server_name}** готов!

<code>{vless_link}</code>

Он будет действовать до **{expires_at}**.''',

        'info_title_ios': "<b><u>Инструкция для iPhone / iPad (iOS)</u></b>",
        'info_app_recommendation_ios': "Для подключения мы рекомендуем одно из этих приложений:",
        'info_app_foxray': '''• <b>FoXray</b> (<a href="https://apps.apple.com/us/app/foxray/id6448898396">App Store</a>) - бесплатное, простое и удобное.''',
        'info_app_shadowrocket': '''• <b>Shadowrocket</b> (<a href="https://apps.apple.com/us/app/shadowrocket/id932747118">App Store</a>) - платное, но очень мощное и популярное.''',
        'info_setup_title_ios': "<b><u>Пошаговая настройка (на примере FoXray):</u></b>",
        'info_step1_ios': "1. Установите приложение FoXray из App Store.",
        'info_step2_ios': "2. Вернитесь в этот чат и скопируйте вашу VLESS-ссылку (просто нажмите на нее).",
        'info_step3_ios': "3. Откройте FoXray. Приложение автоматически обнаружит ссылку в буфере обмена и предложит добавить сервер. Согласитесь.",
        'info_step4_ios': "4. Нажмите на большую круглую кнопку в центре для подключения. При первом запуске приложение попросит разрешение на добавление конфигурации VPN. Разрешите.",
        'info_step5_ios': "5. Готово! Вверху экрана вашего iPhone появится значок [VPN].",
        'info_faq_title': "⚠️ <b>Частые проблемы:</b>",
        'info_faq1_ios': "- <i>Интернет не работает после подключения:</i> Попробуйте перезагрузить телефон или переключить авиарежим.",
        'info_faq2_ios': "- <i>Приложение не видит ссылку:</i> Убедитесь, что вы скопировали ссылку полностью.",

        'info_title_android': "<b><u>Инструкция для Android</u></b>",
        'info_step1_android': '''1. Установите приложение <b>v2rayNG</b> из <a href="https://play.google.com/store/apps/details?id=com.v2ray.ang">Google Play</a>.''',
        'info_step1_alt_android': '''   <i>(Если Google Play недоступен, скачайте .apk с <a href="https://github.com/2dust/v2rayNG/releases/latest">GitHub</a>).</i>''',
        'info_step2_android': "2. Вернитесь в этот чат и скопируйте вашу VLESS-ссылку (просто нажмите на нее).",
        'info_step3_android': "3. Откройте v2rayNG. Нажмите на иконку <b>"+"</b> в правом верхнем углу.",
        'info_step4_android': "4. Выберите в меню <b>"Import config from Clipboard"</b> (Импорт из буфера обмена).",
        'info_step5_android': "5. Ваш ключ появится в списке. Нажмите на него, чтобы он выделился.",
        'info_step6_android': '''6. Нажмите на большую круглую кнопку с логотипом "V" внизу справа для подключения. Она станет зеленой.''',
        'info_step7_android': "7. Готово! В строке состояния появится значок ключа [VPN].",
        'info_faq1_android': '''- <i>Интернет не работает:</i> В настройках v2rayNG (три полоски слева) убедитесь, что в разделе "VPN routing" (Маршрутизация) не включены специфические правила, блокирующие трафик.''',
        'info_faq2_android': '''- <i>Ошибка "invalid config":</i> Убедитесь, что вы скопировали ссылку полностью.''',

        'info_title_windows': "<b><u>Инструкция для Windows</u></b>",
        'info_step1_windows': '''1. Скачайте приложение <b>v2rayN</b> с <a href="https://github.com/2dust/v2rayN/releases/latest">GitHub</a>.''',
        'info_step1_alt_windows': '''   <i>(Вам нужен файл с названием <b>v2rayN-Core.zip</b>).</i>''',
        'info_step2_windows': "2. Распакуйте скачанный архив в удобную папку (например, на Рабочий стол).",
        'info_step3_windows': "3. Запустите файл <b>v2rayN.exe</b>.",
        'info_step4_windows': "4. Вернитесь в этот чат и скопируйте вашу VLESS-ссылку.",
        'info_step5_windows': "5. Откройте окно программы v2rayN и нажмите на клавиатуре <b>Ctrl+V</b>. Ваш ключ автоматически добавится в список серверов.",
        'info_step6_windows': '''6. В системном трее (возле часов, в правом нижнем углу экрана) найдите синюю иконку "V". Нажмите на нее <u>правой кнопкой мыши</u>.''',
        'info_step7_windows': '''7. В появившемся меню выберите <b>"System Proxy"</b> -> <b>"Set system proxy"</b>.''',
        'info_step8_windows': "8. Готово! Иконка в трее станет красной, а весь ваш трафик будет защищен.",
        'info_faq1_windows': '''- <i>Иконка не становится красной:</i> Убедитесь, что вы выбрали сервер в главном окне программы (нажмите на него левой кнопкой мыши).''',
        'info_faq2_windows': '''- <i>Сайты не открываются:</i> Проверьте, что в меню "System Proxy" выбрано "Set system proxy", а не "Clear system proxy".''',

        'info_title_macos': "<b><u>Инструкция для macOS</u></b>",
        'info_app_recommendation_macos': "Мы рекомендуем использовать приложение <b>V2RayU</b>.",
        'info_step1_macos': '''1. Скачайте последнюю версию V2RayU с <a href="https://github.com/yanue/V2RayU/releases/latest">GitHub</a>.''',
        'info_step1_alt_macos': '''   <i>(Вам нужен файл с расширением <b>.dmg</b>).</i>''',
        'info_step2_macos': "2. Установите приложение, перетащив его в папку "Applications".",
        'info_step3_macos': "3. Запустите V2RayU. Его иконка появится в строке меню (вверху экрана).",
        'info_step4_macos': "4. Вернитесь в этот чат и скопируйте вашу VLESS-ссылку.",
        'info_step5_macos': '''5. Нажмите на иконку V2RayU в строке меню и выберите <b>"Import from pasteboard"</b>. Ключ добавится автоматически.''',
        'info_step6_macos': '''6. После импорта снова нажмите на иконку, выберите <b>"Server"</b> и кликните на добавленный сервер.''',
        'info_step7_macos': "7. Включите VPN, выбрав <b>"Turn V2RayU On"</b>.",
        'info_step8_macos': "8. Готово!",
        'info_faq1_macos': '''- <i>Не работает интернет:</i> Убедитесь, что в меню V2RayU выбран режим "Global Mode".''',
        'info_faq2_macos': '''- <i>Сервер не появляется после импорта:</i> Попробуйте обновить подписку вручную через меню "Subscribe" -> "Subscribe settings" -> "Update"''',

        # --- Redesign ---
        'btn_my_keys': "🔑 Мои ключи",
        'btn_my_profile': "👤 Мой профиль",
        'btn_extend_subscription': "➕ Продлить/Расширить подписку",
        'btn_activate_days': "🌟 Активировать {days} дней",
        'btn_how_it_works': "❓ Как это работает?",
        'my_profile_title': "<b>👤 Мой профиль</b>",
        'my_profile_info': '''
<b>ID:</b> <code>{user_id}</code>
<b>Дней на балансе:</b> {unassigned_days}
<b>Реферальный баланс:</b> {ref_balance:.2f} руб.
<b>Приглашено:</b> {ref_count} чел.''',
        'my_keys_title': "<b>🔑 Мои активные ключи</b>",
        'my_keys_no_keys': "У вас пока нет активных ключей.",
        'my_keys_item': '''

Сервер: <b>{server_name}</b>
Истекает: {expires_at}''',
        'btn_show_key': "Показать ключ",
    },
    'en': {
        # Dynamic content from DB
        'db_content': {
            "Неделя": "Week",
            "Месяц": "Month",
            "Год": "Year",
            "Нидерланды": "Netherlands",
        },

        # General
        'error_generic': "An error occurred. Please try again later.",
        'btn_main_menu': "Main Menu",
        'btn_back': "Back",
        'user_not_found_error': "An error occurred, user not found.",
        'tariff_not_found': "An error occurred. Tariff not found.",

        # Language Selection
        'select_language': "Please select a language:",
        'language_changed': "Language changed to English.",

        # New Welcome Message
        'welcome_new_user': "What can this bot do?\nIntroducing our VPN service: fast, stable, and easy to use. Forget about all blockages! Enjoy access on any device: iOS, Android, MacOS, Windows\nReady to go? Press the button below",
        'btn_start_bot': "Let's go!",

        # Main Menu (/start)
        'welcome': "Hello, {full_name}! This is the main menu.",
        'subscription_active_until': '''

Your subscription is active until: **{expiry_date}**''',
        'no_active_subscription': '''
You don\'t have an active subscription yet.'''
        'unassigned_days': '''
You have **{days}** unused days of VPN access.''',
        'referral_stats': '''

You have invited: **{referrals}** people.
Earned: **{earnings:.2f} RUB.**''',
        'btn_setup_vpn': "⚙️ Setup VPN",
        'btn_pay_subscription': "💰 Pay for subscription",
        'btn_referral_program': "🤝 Referral Program",
        'btn_why_vpn': "Why is our VPN better?",
        'btn_get_free_vpn': "Get free VPN for 3 days",
        'btn_help': "❓ Need help?",
        'btn_terms_of_use': "Terms of Use",

        # Gift/Referral activation
        'referral_bonus_applied': "You have joined via a referral link! You\'ve been credited 100 bonus rubles.",
        'gift_activated': '''✅ Gift activated successfully!
**{days}** subscription days have been added to your balance.''',
        'gift_not_found_or_used': "❌ This gift code was not found or has already been used.",
        'gift_activation_error': "❌ An error occurred while activating the gift: the tariff was not found.",

        # VPN Setup
        'select_server_for_setup': "Select a server to set up:",
        'vpn_setup_instructions': "How to set up?\n1️⃣Click the country (server) below\n2️⃣Download the suggested application\n3️⃣Return to the bot and click \"Add key\"\n\nTo make YouTube faster and ad-free - choose YouTubeNoAds\n\nNeed help? {support_chat_link} - we will respond in 7 minutes.",
        'no_servers_available': "Sorry, there are no available servers at the moment.",
        'server_or_user_not_found': "An error occurred. User or server not found.",
        'vpn_key_info': "You already have an active subscription for {server_name}.\nYour VPN key: <a href=\"{vless_link}\">{vless_link}</a>\nExpires on: {expiry_date}",
        'show_subscription_error': "An unexpected error occurred while displaying your subscription. Please try again later.",
        'no_active_subscription_for_server': "You don\'t have an active subscription for {server_name}. Choose an activation method:",
        'btn_activate_unassigned_days': "Activate {days} days (free)",
        'btn_pay_from_referral_balance': "Pay from referral balance ({balance:.2f} RUB)",
        'btn_select_tariff_for_payment': "Select a tariff for payment",
        'btn_back_to_server_selection': "Back to server selection",

        # Referral Balance Payment
        'referral_balance_menu_title': "Your referral balance: {balance:.2f} RUB.\nChoose a tariff to pay:",
        'referral_payment_insufficient_funds': "You have insufficient funds ({balance:.2f} RUB) in your referral balance to purchase any tariff.",
        'referral_payment_error': "An error occurred. User, tariff or server not found.",
        'referral_payment_insufficient_funds_for_tariff': "You have insufficient funds in your referral balance.",
        'referral_payment_success': '''✅ Subscription for **{tariff_name}** has been successfully activated from your referral balance!

Your key for server **{server_name}**:
<a href="{vless_link}">{vless_link}</a>

It will be valid for **{days}** days.''',
        'referral_payment_activation_error': "An error occurred while activating the subscription. Please try again later.",

        # Unassigned Days Activation
        'no_unassigned_days': "You have no unused days to activate.",
        'unassigned_days_activation_success': '''✅ Your unused days have been activated for server **{server_name}**!

Your VPN key: <a href="{vless_link}">{vless_link}</a>

Connection instructions: ...''',
        'unassigned_days_activation_error': "An error occurred while activating the days. Please try again later.",

        # Payment
        'choose_tariff': "Choose a tariff:",
        'no_tariffs_available': "Sorry, there are no available tariffs at the moment.",
        'tariff_selection_title': '''<b>{tariff_name}</b> - {price:.2f} RUB for premium access for {days} days.

Please choose a payment method:''',
        'btn_pay_card': "Pay {price:.2f} RUB (Card)",
        'btn_pay_stars': "Pay {stars} ⭐️",
        'btn_pay_transfer': "Bank Transfer",
        'btn_pay_crypto': "Pay with Cryptocurrency",
        'btn_back_to_tariffs': "Choose tariff",
        'crypto_payment_info': '''Cryptocurrency payment is available only for a year with a 25% discount!

Pay <b>{price_usd} USD</b> (or the equivalent in crypto) to one of the wallets:

BTC: <code>{btc_address}</code>
ETH (ERC-20): <code>{eth_address}</code>
USDT (TRC-20): <code>{usdt_address}</code>

And send the transaction link or receipt to our support service ⬇️''',
        'btn_send_check_to_support': "Send receipt to support",
        'stars_payment_unavailable': "Sorry, payment with stars is currently unavailable.",
        'invoice_title_subscription': "Subscription: {tariff_name}",
        'invoice_description_subscription': "VPN access for {days} days.",
        'invoice_label_subscription': "{tariff_name} ({days} days)",
        'payment_error_server_not_found': "An error occurred while processing your payment (server not found). Please contact support.",
        'payment_success_key_created': '''✅ Payment successful!

Your key for server **{server_name}** is ready:
<code>{vless_link}</code>

It will be valid for **{days}** days.

Connection instructions: ...''',
        'payment_success_key_error': "Unfortunately, an error occurred while creating your VPN key after payment. Please contact support, we will solve it.",
        'payment_success_days_added': '''✅ Payment successful!

**{days}** unused days of VPN access have been credited to your balance.

You can now go to the "Setup VPN" section and select any server to get a key.

Connection instructions: ...''',
        'gift_purchase_success': '''✅ Payment successful!

You have purchased a gift subscription: **{tariff_name}**.

Forward this message or the link below to the person you are gifting the subscription to:
<code>{gift_link}</code>''',
        'payment_payload_parse_error': "An error occurred while processing your payment. Please contact support.",
        'payment_unexpected_error': "An unexpected error occurred. Please contact support.",

        # Trial
        'trial_already_used': "You have already used your free trial period. To continue using the service, please purchase a subscription.",
        'trial_unavailable': "Sorry, the trial period is temporarily unavailable. Please try again later.",
        'trial_server_unavailable': "Sorry, the trial server is temporarily unavailable. Please try again later.",
        'trial_key_creation_wait': "Please wait, we are creating a trial key for you...",
        'trial_key_creation_success': '''Your trial key for 3 days: <a href="{vless_link}">{vless_link}</a>

Connection instructions: ...''',
        'trial_key_creation_error': "An error occurred while creating the trial key. Please contact support.",

        # Referral Program
        'ref_program_title': "<b>Referral Program Terms</b>",
        'ref_program_conditions': "30% from referral payments and 5% from second-level referral payments + 15 days for each invited user who starts the VPN",
        'ref_program_withdrawal': "Withdrawal of funds from 1000 RUB, please contact technical support for withdrawal.",
        'ref_total_referrals': "<b>Total referrals:</b> {count}",
        'ref_last_10': "(Last 10: {logins})",
        'ref_not_activated': "<b>Haven\'t started VPN:</b>",
        'ref_no_inactive_referrals': "(None)",
        'ref_activation_info': "To become a full-fledged referral and give you bonus time, your invited friend must start using the service and launch the VPN",
        'ref_friend_bonus_info': "Each of your friends will be credited with 100 rubles to their referral balance.",
        'ref_balance_info': "<b>Referral balance:</b> {total_balance:.2f} RUB (of which {l2_balance:.2f} RUB is for second-level referrals) RUB.",
        'ref_bonus_days_info': "<b>Bonus days from referrals:</b> {days}.",
        'ref_paid_out_info': "<b>Total paid out:</b> {total_paid_out:.2f} RUB.",
        'ref_copy_link_info': "Copy your partner link:",
        'ref_create_invite_info': "Or click the \"Create Invitation\" button below and forward what the bot writes to your friend:",
        'btn_gift_subscription': "Gift a subscription",
        'btn_create_invitation': "Create Invitation",

        # Gift Subscription
        'gift_subscription_unavailable': "Sorry, the option to gift a subscription is currently unavailable.",
        'gift_purchase_title': "You can gift a PRO subscription to another user.",
        'gift_purchase_instructions': '''<b>{price:.2f} ₽</b> for premium access to SiriusVPN for <b>{days} days</b>, will be purchased as a gift.

You can pay by card online or contact technical support to get details for paying for a yearly gift with crypto or bank transfer.

After payment, the bot will send you a message with the gift. Forward it to the person you are gifting it to.''',
        'btn_pay_gift_card': "Pay {price:.2f} ₽ (Card)",
        'btn_pay_gift_stars': "Pay {stars} ⭐️",
        'btn_contact_support_for_gift': "Contact support",
        'btn_back_to_referral_menu': "Back to referral menu",
        'invoice_title_gift': "Gift: {tariff_name}",
        'invoice_description_gift': "Gift subscription for {days} days.",
        'invoice_label_gift': "Gift: {tariff_name}",

        # Placeholders & TBD
        'tbd': "This feature is under development.",
        'support_info': "For help, please contact support.",
        'support_redirect_message': "Click the button below to go to our support bot.",
        'btn_go_to_support_chat': "Go to Support Bot",
        'terms_info': "Terms of use are under development.",
        'terms_of_use_full': '''Contact for communication (feedback, wishes, suggestions, errors): {support_chat_link}

For a refund, contact @SiriusVPNhelpbot
Subscription cost: 99 ₽ per month, automatically debited if you have not deleted the card.
To cancel a paid subscription and delete a card, click the "Cancel subscription" button below. Access according to the paid period will be saved.

By continuing to use the bot, you agree to our
<a href="{terms_of_service_url}">license agreement</a> and <a href="{privacy_policy_url}">privacy policy</a>''',
        'btn_cancel_subscription': "Cancel subscription",
        'payment_card_unavailable': "Card payment is temporarily unavailable.",
        'payment_transfer_unavailable': "Bank transfer payment is temporarily unavailable.",
        'payment_gift_card_unavailable': "Gift card payment is temporarily unavailable.",

        # YooKassa Integration
        'payment_redirect_info': "You will be redirected to the payment page. Click the button below to continue.",
        'btn_go_to_payment': "Go to payment",
        'btn_back_to_gift_menu': "Back to gift purchase",

        # --- Instructions ---
        'btn_how_to_connect': "❓ How to connect?",
        'info_os_selection_title': "Select your operating system:",
        'btn_ios': "📱 iPhone (iOS)",
        'btn_android': "📱 Android",
        'btn_windows': "💻 Windows",
        'btn_macos': "💻 macOS",
        'btn_back_to_os_selection': "⬅️ Back to OS selection",
        'key_created_or_updated': '''Your key for server **{server_name}** is ready!

<code>{vless_link}</code>

It will be valid until **{expires_at}**.''',

        'info_title_ios': "<b><u>Instructions for iPhone / iPad (iOS)</u></b>",
        'info_app_recommendation_ios': "For connection, we recommend one of these applications:",
        'info_app_foxray': "• <b>FoXray</b> (<a href=\"https://apps.apple.com/us/app/foxray/id6448898396\">App Store</a>) - free, simple, and convenient.",
        'info_app_shadowrocket': "• <b>Shadowrocket</b> (<a href=\"https://apps.apple.com/us/app/shadowrocket/id932747118\">App Store</a>) - paid, but very powerful and popular.",
        'info_setup_title_ios': "<b><u>Step-by-step setup (using FoXray as an example):</u></b>",
        'info_step1_ios': "1. Install the FoXray app from the App Store.",
        'info_step2_ios': "2. Return to this chat and copy your VLESS link (just click on it).",
        'info_step3_ios': "3. Open FoXray. The app will automatically detect the link in your clipboard and offer to add the server. Agree.",
        'info_step4_ios': "4. Tap the large round button in the center to connect. On the first launch, the app will ask for permission to add a VPN configuration. Allow it.",
        'info_step5_ios': "5. Done! A [VPN] icon will appear at the top of your iPhone screen.",
        'info_faq_title': "⚠️ <b>Common Issues:</b>",
        'info_faq1_ios': "- <i>Internet not working after connection:</i> Try restarting your phone or toggling airplane mode.",
        'info_faq2_ios': "- <i>App doesn't see the link:</i> Make sure you copied the entire link.",

        'info_title_android': "<b><u>Instructions for Android</u></b>",
        'info_step1_android': "1. Install the <b>v2rayNG</b> app from <a href=\"https://play.google.com/store/apps/details?id=com.v2ray.ang\">Google Play</a>.",
        'info_step1_alt_android': "   <i>(If Google Play is unavailable, download the .apk from <a href=\"https://github.com/2dust/v2rayNG/releases/latest\">GitHub</a>).</i>",
        'info_step2_android': "2. Return to this chat and copy your VLESS link.",
        'info_step3_android': "3. Open v2rayNG. Tap the <b>\"+\"</b> icon in the top right corner.",
        'info_step4_android': "4. Select <b>\"Import config from Clipboard\"</b> from the menu.",
        'info_step5_android': "5. Your key will appear in the list. Tap it to select it.",
        'info_step6_android': "6. Tap the large round button with the \"V\" logo at the bottom right to connect. It will turn green.",
        'info_step7_android': "7. Done! A key icon [VPN] will appear in your status bar.",
        'info_faq1_android': "- <i>Internet not working:</i> In v2rayNG settings (three bars on the left), ensure that no specific traffic-blocking rules are enabled under \"VPN routing\".",
        'info_faq2_android': "- <i>\"Invalid config\" error:</i> Make sure you copied the entire link.",

        'info_title_windows': "<b><u>Instructions for Windows</u></b>",
        'info_step1_windows': "1. Download the <b>v2rayN</b> application from <a href=\"https://github.com/2dust/v2rayN/releases/latest\">GitHub</a>.",
        'info_step1_alt_windows': "   <i>(You need the file named <b>v2rayN-Core.zip</b>).</i>",
        'info_step2_windows': "2. Unzip the downloaded archive to a convenient folder (e.g., your Desktop).",
        'info_step3_windows': "3. Run the <b>v2rayN.exe</b> file.",
        'info_step4_windows': "4. Return to this chat and copy your VLESS link.",
        'info_step5_windows': "5. Open the v2rayN program window and press <b>Ctrl+V</b>. Your key will be automatically added to the server list.",
        'info_step6_windows': "6. In the system tray (near the clock, bottom right corner), find the blue \"V\" icon. <u>Right-click</u> on it.",
        'info_step7_windows': "7. In the context menu, select <b>\"System Proxy\"</b> -> <b>\"Set system proxy\"</b>.",
        'info_step8_windows': "8. Done! The tray icon will turn red, and all your traffic will be protected.",
        'info_faq1_windows': "- <i>Icon doesn't turn red:</i> Make sure you have selected a server in the main program window (left-click on it).",
        'info_faq2_windows': "- <i>Websites don't open:</i> Check that \"Set system proxy\" is selected in the \"System Proxy\" menu, not \"Clear system proxy\".",

        'info_title_macos': "<b><u>Instructions for macOS</u></b>",
        'info_app_recommendation_macos': "We recommend using the <b>V2RayU</b> application.",
        'info_step1_macos': "1. Download the latest version of V2RayU from <a href=\"https://github.com/yanue/V2RayU/releases/latest\">GitHub</a>.",
        'info_step1_alt_macos': "   <i>(You need the file with the <b>.dmg</b> extension).</i>",
        'info_step2_macos': "2. Install the application by dragging it to the \"Applications\" folder.",
        'info_step3_macos': "3. Launch V2RayU. Its icon will appear in the menu bar (at the top of the screen).",
        'info_step4_macos': "4. Return to this chat and copy your VLESS link.",
        'info_step5_macos': "5. Click the V2RayU icon in the menu bar and select <b>\"Import from pasteboard\"</b>. The key will be added automatically.",
        'info_step6_macos': "6. After importing, click the icon again, select <b>\"Server\"</b>, and click on the added server.",
        'info_step7_macos': "7. Turn on the VPN by selecting <b>\"Turn V2RayU On\"</b>.",
        'info_step8_macos': "8. Done!",
        'info_faq1_macos': "- <i>Internet not working:</i> Make sure \"Global Mode\" is selected in the V2RayU menu.",
        'info_faq2_macos': "- <i>Server doesn't appear after import:</i> Try updating the subscription manually via the \"Subscribe\" -> \"Subscribe settings\" -> \"Update\" menu.",

        # --- Redesign ---
        'btn_my_keys': "🔑 My Keys",
        'btn_my_profile': "👤 My Profile",
        'btn_extend_subscription': "➕ Extend/Upgrade Subscription",
        'btn_activate_days': "🌟 Activate {days} days",
        'btn_how_it_works': "❓ How it works?",
        'my_profile_title': "<b>👤 My Profile</b>",
        'my_profile_info': '''
<b>ID:</b> <code>{user_id}</code>
<b>Days on balance:</b> {unassigned_days}
<b>Referral balance:</b> {ref_balance:.2f} RUB
<b>Invited:</b> {ref_count} users''',
        'my_keys_title': "<b>🔑 My Active Keys</b>",
        'my_keys_no_keys': "You have no active keys yet.",
        'my_keys_item': "\n\nServer: <b>{server_name}</b>\nExpires: {expires_at}",
        'btn_show_key': "Show Key",
    }
}

def get_text(key: str, lang_code: str = 'ru'):
    """
    Returns the translated text for a given key and language code.
    Defaults to Russian if the key or language is not found.
    """
    # Fallback to 'ru' if lang_code is None or not in translations
    if lang_code not in translations:
        lang_code = 'ru'
    
    # Fallback to the key itself if not found in the specific language or in 'ru'
    default_lang_dict = translations['ru']
    lang_dict = translations[lang_code]
    
    return lang_dict.get(key, default_lang_dict.get(key, f"<{key}>"))

def get_db_text(json_text: dict, lang_code: str = 'ru'):
    """
    Returns the translated text from a JSON object based on the language code.
    Falls back to 'ru' or the first available language if the specified lang_code is not found.
    """
    if not isinstance(json_text, dict):
        return str(json_text) # Return the text as is if it's not a dict

    if lang_code in json_text:
        return json_text[lang_code]
    
    # Fallback logic
    if 'ru' in json_text:
        return json_text['ru']
    if 'en' in json_text:
        return json_text['en']
    
    # If no preferred languages are found, return the first value
    for key in json_text:
        return json_text[key]
        
    return "[no name]"
