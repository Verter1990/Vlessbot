import asyncio
from urllib.parse import urlparse, parse_qs, unquote
from loguru import logger
import json

# Импорты из вашего проекта
from core.services.xui_client import XUIClient, ClientConfig, XUIClientError
from core.utils.security import decrypt_password # Используем, если XUI_API_PASSWORD зашифрован

# --- Ваши данные ---
XUI_API_URL = "https://vpn.myvless.fun:2053/"
XUI_API_USER = "admin"
XUI_API_PASSWORD = "9M1u3vX4tp7upPXE"
ENCRYPTION_KEY = "WgzUiBYU7mixLCodcINjJgoIpXzrb_Adf8vIUhcE9MI=" # Используется для расшифровки XUI_API_PASSWORD, если он зашифрован
INBOUND_ID = 1 # ID входящего соединения, куда будут добавлены клиенты

VLESS_LINKS = [
    "vless://23baecff-d90f-45ad-8a51-dd8081aa4bd9@77.238.230.57:19217?type=tcp&security=reality&pbk=-pX5Cct3vPtoCpjaTD_OlBWate_95bHiwKf1gJNk7Xo&fp=chrome&sni=yahoo.com&sid=bb&spx=%2F#%D0%BC%D0%BE%D0%B9%20%D0%BF%D0%BA-rqn1q6c7",
    "vless://a17f73f1-530b-4ff0-90b1-075a5350a6f2@77.238.230.57:52253?type=tcp&security=reality&pbk=huAJkuPi37opRJ3NRIGDHHBa1lncK_KWiTxt_UHm0Dg&fp=chrome&sni=yahoo.com&sid=9a165c27a1560ec0&spx=%2F#%D0%9B%D0%B8%D0%B7%D0%B0%20%D1%82%D0%B5%D0%BB%D0%B5%D1%84%D0%BE%D0%BD-47rxnudb",
    "vless://e3f57232-2c79-44a0-a7a7-b46155cbd0e9@77.238.230.57:45130?type=tcp&security=reality&pbk=9suKhDGdIjz7i2JXkrgjfzWlQQ7NE-kJtI6MIK-LbE0&fp=chrome&sni=yahoo.com&sid=a46d&spx=%2F#%D0%9B%D0%B8%D0%B7%D0%B0%20%D0%BD%D0%BE%D1%83%D1%82%D0%B1%D1%83%D0%BA-it4viw3v",
    "vless://c4f16752-586d-4eb5-8686-57ab1851b4cb@77.238.230.57:12728?type=tcp&security=reality&pbk=f4Jw6NjJAumdmOwF4pYfHOi41jjrewc5GxaOAt9D7wA&fp=chrome&sni=yahoo.com&sid=c4c85cc1807a75&spx=%2F#%D0%9A%D0%BE%D0%BB%D1%8F%201-gzscfz8d",
    "vless://4b18a427-e562-43f5-9e85-506536bfaa59@77.238.230.57:41235?type=tcp&security=reality&pbk=7Sl7jBBLUjerD_sEAp7yhph6cfdiKS__0mEI1ZK6eGk&fp=chrome&sni=yahoo.com&sid=eed6cb323f623c&spx=%2F#%D0%AE%D0%BB%D1%8F%201-9ju75q2y",
    "vless://e78e5281-a3a6-4a06-8261-f50ec05fe2c8@77.238.230.57:44224?type=tcp&security=reality&pbk=Aq5Smg-a3fNOrEDEoPYwYRs_Ml6g8Y9mJNGFK26Nln0&fp=chrome&sni=yahoo.com&sid=2bc5ca24c416b973&spx=%2F#%D0%AE%D0%BB%D1%8F%202-y6fz8lxe",
    "vless://6bc88713-11f3-4d2c-a656-d57e9ce55265@77.238.230.57:48905?type=tcp&security=reality&pbk=6mhvqPB276vL0hzEE_lWPY5ThAmqEKtVRBY-nR1N3FQ&fp=chrome&sni=yahoo.com&sid=f64a407c&spx=%2F#%D0%BC%D0%BE%D0%B9%20%D1%82%D0%B5%D0%BB%D0%B5%D1%84%D0%BE%D0%BD-sbfic5ko",
    "vless://0c17f26d-fa0f-4ba0-9c3a-f8bbae7db8dc@77.238.230.57:10073?type=tcp&security=reality&pbk=CRNI3lyYjl-RLEnPvSsUMYthD39VjREgNxYbZ3xk9VI&fp=chrome&sni=yahoo.com&sid=aa148b9068&spx=%2F#%D0%BC%D0%B0%D0%BC%D0%B0%201-sa31lcjr",
    "vless://f2bcda61-f400-4b19-9039-b5f200957ec2@77.238.230.57:31626?type=tcp&security=reality&pbk=E248TLOJBxsrT5FH6GamG-bl78d8guVMX64EFa8zCHs&fp=chrome&sni=yahoo.com&sid=82d30226&spx=%2F#%D0%BF%D0%B0%D0%BF%D0%B0-r17r3qqd",
    "vless://3cc747bb-38b1-4f32-96e0-6ecc44d778a5@vpn.myvless.fun:22497?type=tcp&security=tls&fp=chrome&alpn=h3%2Ch2%2Chttp%2F1.1&flow=xtls-rprx-vision#8gd2jybv",
    "vless://0241e655-c9f1-4816-b06e-46dcb6a09028@vpn.myvless.fun:55267?type=tcp&security=tls&fp=chrome&alpn=h3%2Ch2%2Chttp%2F1.1#%20-%20Cloned-0prcxzij",
    "vless://df5ab347-41f5-45a6-9f05-7c7fd5a7ae9b@vpn.myvless.fun:51482?type=tcp&security=tls&fp=chrome&alpn=h3%2Ch2%2Chttp%2F1.1#%20-%20Cloned%20-%20Cloned-olu2wmxk",
    "vless://71ead8f2-348a-45aa-b483-df7b5cadadc1@vpn.myvless.fun:19661?type=tcp&security=tls&fp=chrome&alpn=h3%2Ch2%2Chttp%2F1.1#%20-%20Cloned%20-%20Cloned%20-%20Cloned-uq4nw27p",
    "vless://0de98a57-301b-4aae-b73a-b421d4db98b0@vpn.myvless.fun:11494?type=tcp&security=tls&fp=chrome&alpn=h3%2Ch2%2Chttp%2F1.1#%20-%20Cloned%20-%20Cloned%20-%20Cloned%20-%20Cloned-d2lvlpb6",
    "vless://6e14fca7-362b-4368-af7a-4d5b429bdf48@vpn.myvless.fun:56759?type=tcp&security=tls&fp=chrome&alpn=h3%2Ch2%2Chttp%2F1.1#%20-%20Cloned%20-%20Cloned%20-%20Cloned%20-%20Cloned%20-%20Cloned-q8yvgxwd",
    "vless://3305230f-68de-4b96-ab1c-f4e72064b374@vpn.myvless.fun:59041?type=tcp&security=tls&fp=chrome&alpn=h3%2Ch2%2Chttp%2F1.1#%20-%20Cloned%20-%20Cloned%20-%20Cloned%20-%20Cloned%20-%20Cloned%20-%20Cloned-510mbgn9",
    "vless://d7571016-01b4-4d1c-ad2a-7152dc9579de@vpn.myvless.fun:52067?type=tcp&security=tls&fp=chrome&alpn=h3%2Ch2%2Chttp%2F1.1#%D0%A2%D0%B5%D0%BB%D0%B5%D0%B2%D0%B8%D0%B7%D0%BE%D1%80-%D1%81%D0%B0%D1%88%D0%B0-bb9k9w8a",
    "vless://31d41129-5142-493f-bd88-f1db6c8ca58b@vpn.myvless.fun:10153?type=tcp&security=tls&fp=chrome&alpn=h3%2Ch2%2Chttp%2F1.1#%20-%20Cloned%20-%20Cloned%20-%20Cloned%20-%20Cloned%20-%20Cloned%20-%20Cloned%20-%20Cloned%20-%20Cloned-muw7sref",
    "vless://e6724190-3d89-4432-aedf-2a3c78bd2a5a@vpn.myvless.fun:23887?type=tcp&security=reality&pbk=qz6wQPPsf8JbwLi1tZrW47uvLGlllaXJozl03CKfzDg&fp=chrome&sni=yahoo.com&sid=bb&spx=%2F#%D0%9E%D0%BB%D1%8F-29qgau0w"
]

async def import_vless_clients():
    logger.info("--- Запуск импорта VLESS клиентов ---")

    # Расшифровываем пароль, если ENCRYPTION_KEY используется
    try:
        # В данном случае XUI_API_PASSWORD не зашифрован, но функция decrypt_password
        # может быть настроена для обработки этого. Если она ожидает зашифрованный пароль,
        # и XUI_API_PASSWORD не зашифрован, это может вызвать ошибку.
        # Для простоты, если пароль не зашифрован, используем его напрямую.
        # Если decrypt_password требует ENCRYPTION_KEY, убедитесь, что он корректен.
        decrypted_password = XUI_API_PASSWORD # Предполагаем, что пароль не зашифрован для API
        # Если пароль зашифрован, используйте:
        # decrypted_password = decrypt_password(XUI_API_PASSWORD, ENCRYPTION_KEY)
    except Exception as e:
        logger.error(f"Не удалось расшифровать пароль. Ошибка: {e}")
        return

    xui_client = XUIClient(
        api_url=XUI_API_URL,
        username=XUI_API_USER,
        password=decrypted_password
    )

    successful_imports = 0
    failed_imports = 0

    for link in VLESS_LINKS:
        try:
            parsed_link = urlparse(link)
            uuid_part = parsed_link.netloc.split('@')[0]
            remark_part = parsed_link.fragment

            # Декодируем remark, так как он может содержать URL-кодированные символы
            remark = unquote(remark_part) if remark_part else f"client-{uuid_part[:8]}"

            query_params = parse_qs(parsed_link.query)
            flow = query_params.get('flow', [''])[0] # Извлекаем flow, если есть

            client_config = ClientConfig(
                id=uuid_part,
                email=remark, # Используем remark как email для идентификации
                flow=flow,
                totalGB=0, # Неограниченный трафик
                expiryTime=0, # Никогда не истекает
                enable=True
            )

            logger.info(f"Попытка добавить клиента {remark} (UUID: {uuid_part[:8]}...) в inbound {INBOUND_ID}")
            add_response = await xui_client.add_client(INBOUND_ID, client_config)

            if add_response.get("success"):
                logger.success(f"Успешно добавлен клиент: {remark}")
                successful_imports += 1
            else:
                logger.error(f"Не удалось добавить клиента {remark}: {add_response.get('msg', 'Неизвестная ошибка')}")
                failed_imports += 1

        except Exception as e:
            logger.error(f"Ошибка при обработке ссылки {link}: {e}")
            failed_imports += 1

    await xui_client.close()
    logger.info(f"--- Импорт завершен. Успешно: {successful_imports}, Ошибок: {failed_imports} ---")

if __name__ == "__main__":
    asyncio.run(import_vless_clients())
