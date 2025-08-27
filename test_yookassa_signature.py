import asyncio
from core.config import settings
from core.utils.security import verify_yookassa_signature

async def main():
    # Это тестовые данные, которые имитируют вебхук от YooKassa.
    # В реальном вебхуке эти данные будут сгенерированы YooKassa.
    payload_str = '''
{
  "type": "notification",
  "event": "payment.succeeded",
  "object": {
    "id": "test_payment_id_123",
    "status": "succeeded",
    "amount": {
      "value": "1.00",
      "currency": "RUB"
    },
    "metadata": {
      "telegram_user_id": "218265585",
      "tariff_id": "1",
      "payment_type": "subscription",
      "server_id": "1"
    }
  }
}
'''
    payload_bytes = payload_str.encode('utf-8')

    # Это тестовая подпись. В реальном вебхуке она будет сгенерирована YooKassa.
    # Если ваш YOOKASSA_SECRET_KEY правильный, то эта подпись, конечно, не пройдет проверку.
    # Но мы проверим, что функция verify_yookassa_signature работает с вашим ключом.
    test_signature = "test_signature"

    print(f"YooKassa Secret Key (from settings): {settings.YOOKASSA_SECRET_KEY}")
    print(f"Testing signature verification with payload: {payload_bytes[:50]}...")
    print(f"Using test signature: {test_signature}")

    is_valid = verify_yookassa_signature(payload_bytes, test_signature, settings.YOOKASSA_SECRET_KEY)

    if is_valid:
        print("Result: Signature is VALID. (This is unexpected for a test_signature, implies a problem with the test itself or the key is empty)")
    else:
        print("Result: Signature is INVALID. (This is expected for a test_signature, means the function is working)")

if __name__ == "__main__":
    asyncio.run(main())
