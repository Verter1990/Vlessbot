

import httpx
import asyncio
import uuid
import json
from datetime import datetime, timedelta
from urllib.parse import urlparse
from dotenv import load_dotenv
import os

# Загружаем переменные из .env файла
load_dotenv()

# --- Конфигурация из .env файла ---
XUI_API_URL = os.getenv("XUI_API_URL")
XUI_API_USER = os.getenv("XUI_API_USER")
XUI_API_PASSWORD = os.getenv("XUI_API_PASSWORD")
INBOUND_ID = 20 # Как вы и просили

# --- Параметры для тестового ключа ---
TRIAL_PERIOD_DAYS = 3
TRIAL_TRAFFIC_MB = 1024

async def main():
    """Главная функция для генерации ключа."""
    print("--- Запуск генерации тестового ключа ---")

    if not all([XUI_API_URL, XUI_API_USER, XUI_API_PASSWORD]):
        print("\n❌ ОШИБКА: Не найдены переменные XUI_API_URL, XUI_API_USER, или XUI_API_PASSWORD в .env файле.")
        return

    async with httpx.AsyncClient(base_url=XUI_API_URL, verify=False) as client:
        try:
            # 1. Аутентификация
            print(f"1. Аутентификация на сервере {XUI_API_URL}...")
            login_response = await client.post("/login", data={"username": XUI_API_USER, "password": XUI_API_PASSWORD})
            login_response.raise_for_status() # Проверка на HTTP ошибки (4xx, 5xx)
            login_data = login_response.json()
            if not login_data.get("success"):
                raise Exception(f"Не удалось войти в систему: {login_data.get('msg')}")
            print("   ...Успешно! Сессия получена.")

            # 2. Подготовка данных для нового клиента
            print("2. Подготовка данных для нового пользователя...")
            user_uuid = str(uuid.uuid4())
            user_email = f"test-user-{user_uuid[:8]}@test.com"
            expire_time_ms = int((datetime.now() + timedelta(days=TRIAL_PERIOD_DAYS)).timestamp() * 1000)
            traffic_bytes = TRIAL_TRAFFIC_MB * 1024 * 1024

            client_settings = {
                "clients": [
                    {
                        "id": user_uuid,
                        "email": user_email,
                        "expiryTime": expire_time_ms,
                        "totalGB": traffic_bytes,
                        "enable": True,
                        "tgId": "",
                        "subId": ""
                    }
                ]
            }

            # 3. Формирование данных для POST-запроса (как в документации)
            post_data = {
                'id': INBOUND_ID,
                'settings': json.dumps(client_settings)
            }
            print(f"   ...Данные готовы: {post_data}")

            # 4. Отправка запроса на создание клиента
            print(f"3. Отправка запроса на создание пользователя на инбаунд {INBOUND_ID}...")
            add_client_response = await client.post("/panel/api/inbounds/addClient", data=post_data)
            add_client_response.raise_for_status()
            add_client_data = add_client_response.json()

            if not add_client_data.get("success"):
                raise Exception(f"Сервер X-UI вернул ошибку: {add_client_data.get('msg')}")

            print("   ...Успешно! Пользователь создан.")

            # 5. Генерация ссылки
            print("4. Генерация VLESS ссылки...")
            parsed_url = urlparse(XUI_API_URL)
            host = parsed_url.hostname
            port = 443 # Стандартный порт для HTTPS
            params = "security=tls&encryption=none&type=tcp" # Стандартные параметры

            vless_link = f"vless://{user_uuid}@{host}:{port}?{params}#Test-Trial-Link"

            print("\n" + "="*20)
            print("USPEH! Sgenerirovannaya ssylka:")
            print(vless_link)
            print("="*20)

        except httpx.HTTPStatusError as e:
            print(f"\n❌ ОШИБКА HTTP: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            print(f"\n❌ НЕПРЕДВИДЕННАЯ ОШИБКА: {e}")

if __name__ == "__main__":
    asyncio.run(main())
