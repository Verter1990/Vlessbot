# tests/integration/test_database_crud.py

import pytest
from sqlalchemy import select
from core.database.models import User, Server, Tariff

# Помечаем все тесты в этом файле как асинхронные
pytestmark = pytest.mark.asyncio

async def test_create_and_get_user(db_session):
    """
    Тест: Успешное создание и получение пользователя из БД.
    """
    # 1. Arrange: Подготовка данных
    new_user = User(
        telegram_id=12345,
        username="testuser",
        language_code="en"
    )

    # 2. Act: Выполнение действия
    db_session.add(new_user)
    await db_session.commit()
    await db_session.refresh(new_user)

    # 3. Assert: Проверка результата
    # Получаем пользователя из БД
    result = await db_session.execute(select(User).where(User.telegram_id == 12345))
    retrieved_user = result.scalars().first()

    assert retrieved_user is not None
    assert retrieved_user.telegram_id == 12345
    assert retrieved_user.username == "testuser"
    assert retrieved_user.language_code == "en"
    assert retrieved_user.id is not None

async def test_create_tariff(db_session):
    """
    Тест: Успешное создание и получение тарифа.
    """
    # Arrange
    new_tariff = Tariff(
        name={"ru": "Тестовый", "en": "Test"},
        duration_days=10,
        price_rub=10000, # 100.00 RUB
        price_stars=50
    )

    # Act
    db_session.add(new_tariff)
    await db_session.commit()

    # Assert
    retrieved_tariff = await db_session.get(Tariff, new_tariff.id)
    assert retrieved_tariff is not None
    assert retrieved_tariff.name["en"] == "Test"
    assert retrieved_tariff.duration_days == 10