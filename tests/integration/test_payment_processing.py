
import pytest
from unittest.mock import AsyncMock
from aiogram import Bot

from main import process_successful_payment
from core.database.models import User, Tariff, Transaction, Server
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_process_successful_payment_days_added(session: AsyncSession, mocker):
    """
    Tests that when a payment is successful and no specific server is chosen,
    the days are correctly added to the user's unassigned_days.
    """
    # 1. Arrange
    # Mock the bot's send_message method
    mock_bot = mocker.AsyncMock(spec=Bot)
    
    # Mock the _create_or_update_vpn_key function to avoid external API calls
    mocker.patch('main._create_or_update_vpn_key', new_callable=AsyncMock, return_value=('vless://link', 'some_id'))

    # Create mock data in the test database
    test_user = User(telegram_id=123, username='testuser', language_code='ru', unassigned_days=10)
    test_tariff = Tariff(name={"ru": "Тест", "en": "Test"}, duration_days=30, price_rub=10000, price_stars=400)
    session.add_all([test_user, test_tariff])
    await session.flush()

    test_transaction = Transaction(
        id='payment_123',
        user_id=test_user.telegram_id,
        tariff_id=test_tariff.id,
        amount=10000,
        status='pending',
        payment_system='yookassa',
        payment_details={'payment_type': 'subscription'} # No server_id
    )
    session.add(test_transaction)
    await session.commit()

    # 2. Act
    await process_successful_payment(session, mock_bot, test_transaction)

    # 3. Assert
    # Check that the transaction status is updated
    await session.refresh(test_transaction)
    assert test_transaction.status == 'succeeded'

    # Check that the user's days have been updated
    await session.refresh(test_user)
    assert test_user.unassigned_days == 10 + 30 # Initial days + tariff duration

    # Check that the bot sent the correct notification
    mock_bot.send_message.assert_called_once()
    call_args = mock_bot.send_message.call_args[0]
    call_kwargs = mock_bot.send_message.call_args[1]
    
    assert call_args[0] == test_user.telegram_id
    assert '30' in call_kwargs['text'] # Check that the number of days is in the message
    assert 'успешно добавились на ваш баланс' in call_kwargs['text']

@pytest.mark.asyncio
async def test_process_successful_payment_key_created(session: AsyncSession, mocker):
    """
    Tests that when a payment is successful and a server is chosen,
    a VPN key is created and the user is notified.
    """
    # 1. Arrange
    mock_bot = mocker.AsyncMock(spec=Bot)
    mock_create_key = mocker.patch('main._create_or_update_vpn_key', new_callable=AsyncMock, return_value=('vless://newkey', 'new_uuid'))

    test_user = User(telegram_id=456, username='testuser2', language_code='ru')
    test_server = Server(name={"ru": "Тест Сервер", "en": "Test Server"}, api_url="http://test.com", api_user="user", api_password="pw", inbound_id=1)
    test_tariff = Tariff(name={"ru": "Тест", "en": "Test"}, duration_days=90, price_rub=30000, price_stars=1200)
    session.add_all([test_user, test_server, test_tariff])
    await session.flush()

    test_transaction = Transaction(
        id='payment_456',
        user_id=test_user.telegram_id,
        tariff_id=test_tariff.id,
        amount=30000,
        status='pending',
        payment_system='yookassa',
        payment_details={'payment_type': 'subscription', 'server_id': test_server.id}
    )
    session.add(test_transaction)
    await session.commit()

    # 2. Act
    await process_successful_payment(session, mock_bot, test_transaction)

    # 3. Assert
    await session.refresh(test_transaction)
    assert test_transaction.status == 'succeeded'

    # Check that the key creation function was called with the correct parameters
    mock_create_key.assert_called_once_with(session, test_user, test_server, test_tariff.duration_days, 'ru')

    # Check that the user was notified with the key
    mock_bot.send_message.assert_called_once()
    call_args = mock_bot.send_message.call_args[1]
    assert 'vless://newkey' in call_args['text']
    assert '90' in call_args['text']
    assert 'Тест Сервер' in call_args['text']
