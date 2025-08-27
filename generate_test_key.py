

import asyncio
import uuid
from datetime import datetime, timedelta
from urllib.parse import urlparse

# --- Это импорты из вашего же проекта ---
from core.config import settings
from core.services.xui_client import XUIClient, ClientConfig, XUIClientError
from core.utils.security import decrypt_password
from core.constants import TRIAL_TRAFFIC_MB, TRIAL_PERIOD_DAYS
from loguru import logger

async def generate_test_link():
    """
    Этот скрипт напрямую подключается к X-UI API, создает тестового пользователя
    и генерирует для него ссылку.
    """
    logger.info("--- Запуск тестовой генерации ключа ---")

    logger.info(f"DEBUG: First 5 chars of ENCRYPTION_KEY: {settings.ENCRYPTION_KEY[:5]}...")
    logger.info(f"DEBUG: First 5 chars of XUI_API_PASSWORD: {settings.XUI_API_PASSWORD[:5]}...")

    # 1. Расшифровываем пароль из .env
    try:
        decrypted_password = settings.XUI_API_PASSWORD
    except Exception as e:
        logger.error(f"Не удалось расшифровать пароль. Убедитесь, что ENCRYPTION_KEY в .env файле верный. Ошибка: {e}")
        return

    # 2. Создаем клиент для подключения к X-UI
    xui_client = XUIClient(
        api_url=settings.XUI_API_URL,
        username=settings.XUI_API_USER,
        password=decrypted_password
    )

    # 3. Генерируем данные для тестового пользователя
    test_uuid = str(uuid.uuid4())
    test_email = f"test-user-{test_uuid[:8]}@test.com"
    inbound_id = 20 # Как вы и просили

    # 4. Устанавливаем срок действия - 3 дня
    expire_time = datetime.now() + timedelta(days=TRIAL_PERIOD_DAYS)
    expire_time_ms = int(expire_time.timestamp() * 1000)

    # 5. Устанавливаем лимит трафика (в байтах)
    traffic_bytes = TRIAL_TRAFFIC_MB * 1024 * 1024

    # 6. Собираем конфигурацию клиента
    client_config = ClientConfig(
        id=test_uuid,
        email=test_email,
        expiryTime=expire_time_ms,
        totalGB=traffic_bytes,
        tgId="local-test-script"
    )

    try:
        # 7. Пытаемся создать пользователя
        logger.info(f"Попытка создать пользователя: {test_email} на инбаунде {inbound_id}")
        add_response = await xui_client.add_client(inbound_id, client_config)

        if not add_response.get("success"):
            raise XUIClientError(f"Не удалось создать пользователя в X-UI: {add_response}")

        logger.success("Пользователь успешно создан в панели X-UI!")

        # 8. Генерируем ссылку
        logger.info("Генерация VLESS ссылки...")
        parsed_url = urlparse(settings.XUI_API_URL)
        host = parsed_url.hostname
        port = 443 # Стандартный порт для HTTPS

        # Параметры для ссылки (можно взять из настроек инбаунда, но для теста используем стандартные)
        params = "security=tls&encryption=none&type=tcp"

        vless_link = f"vless://{test_uuid}@{host}:{port}?{params}#Test-Trial-Link"

        print("\n" + "="*20)
        print("✅ УСПЕХ! Сгенерированная ссылка:")
        print(vless_link)
        print("="*20)

    except XUIClientError as e:
        
    except Exception as e:
        print(f"\n❌ НЕПРЕДВИДЕННАЯ ОШИБКА: {e}")
    finally:
        # 9. Закрываем соединение
        await xui_client.close()
        logger.info("--- Тестовая генерация ключа завершена ---")


if __name__ == "__main__":
    # Убедимся, что база данных не используется, но зависимости загружены
    # Это позволит избежать ошибок импорта, связанных с БД
    try:
        asyncio.run(generate_test_link())
    except ImportError as e:
        logger.error(f"Ошибка импорта: {e}. Убедитесь, что все зависимости установлены: py -m pip install -r requirements.txt")

