import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from aiogram import Bot
from datetime import datetime, timedelta

from core.services.scheduler_jobs import check_expiring_subscriptions, deactivate_expired_users
from core.database.models import Subscription, User, Server
from core.services.xui_client import XUIClientError, XUIClient

@pytest.fixture
def mock_session():
    mock_execute_result = AsyncMock()
    mock_execute_result.scalars.return_value.all.return_value = [] # Default empty list
    mock_session = AsyncMock()
    mock_session.execute.return_value = mock_execute_result
    return mock_session

@pytest.fixture
def mock_bot():
    return AsyncMock(spec=Bot)

@pytest.fixture
def mock_xui_client():
    return AsyncMock(spec=XUIClient)

@pytest.fixture(autouse=True)
def mock_get_client(mock_xui_client):
    with patch('core.services.scheduler_jobs.get_client', return_value=mock_xui_client) as mock_gc:
        yield mock_gc

@pytest.fixture
def mock_logger():
    with patch('core.services.scheduler_jobs.logger') as mock_log:
        yield mock_log

@pytest.mark.asyncio
class TestSchedulerJobs:

    async def test_check_expiring_subscriptions_no_expiring(self, mock_session, mock_bot, mock_logger):
        mock_session.execute.return_value.scalars.return_value.all.return_value = []
        await check_expiring_subscriptions(mock_bot, mock_session)
        mock_bot.send_message.assert_not_called()
        mock_logger.info.assert_any_call("Scheduler job: Checking for expiring subscriptions...")
        mock_logger.info.assert_any_call("Found 0 subscriptions expiring soon.")

    async def test_check_expiring_subscriptions_with_expiring(self, mock_session, mock_bot, mock_logger):
        user = AsyncMock(spec=User, telegram_id=123, username="testuser")
        server = AsyncMock(spec=Server, name="TestServer")
        sub = AsyncMock(spec=Subscription, user_id=123, server_id=456, expires_at=datetime.utcnow() + timedelta(days=2, hours=23, minutes=59))
        
        mock_session.execute.return_value.scalars.return_value.all.return_value = [sub]
        mock_session.get.side_effect = [user, server]

        await check_expiring_subscriptions(mock_bot, mock_session)

        mock_bot.send_message.assert_called_once_with(
            chat_id=user.telegram_id,
            text=f"Здравствуйте, {user.username or 'пользователь'}!\n\n"
                 f"Ваша подписка на сервер \"{server.name}\" истекает через 3 дня.\n\n"
                 f"Чтобы продлить ее и не потерять доступ, пожалуйста, оплатите подписку."
        )
        mock_logger.info.assert_any_call("Found 1 subscriptions expiring soon.")
        mock_logger.info.assert_any_call(f"Sent renewal reminder to user {user.telegram_id} for server {server.name}")

    async def test_check_expiring_subscriptions_send_message_error(self, mock_session, mock_bot, mock_logger):
        user = AsyncMock(spec=User, telegram_id=123, username="testuser")
        server = AsyncMock(spec=Server, name="TestServer")
        sub = AsyncMock(spec=Subscription, user_id=123, server_id=456, expires_at=datetime.utcnow() + timedelta(days=2, hours=23, minutes=59))
        
        mock_session.execute.return_value.scalars.return_value.all.return_value = [sub]
        mock_session.get.side_effect = [user, server]
        mock_bot.send_message.side_effect = Exception("Telegram API error")

        await check_expiring_subscriptions(mock_bot, mock_session)

        mock_logger.error.assert_called_once_with(f"Failed to send renewal reminder to {user.telegram_id}: Telegram API error")

    async def test_deactivate_expired_users_no_expired(self, mock_session, mock_xui_client, mock_logger):
        mock_session.execute.return_value.scalars.return_value.all.return_value = []
        await deactivate_expired_users(mock_session)
        mock_xui_client.delete_user.assert_not_called()
        mock_session.commit.assert_called_once()
        mock_logger.info.assert_any_call("Scheduler job: Deactivating expired users...")
        mock_logger.info.assert_any_call("Found 0 expired subscriptions to deactivate.")

    async def test_deactivate_expired_users_with_expired(self, mock_session, mock_xui_client, mock_logger):
        user = AsyncMock(spec=User, telegram_id=123)
        server = AsyncMock(spec=Server, name="TestServer")
        sub = AsyncMock(spec=Subscription, user_id=123, server_id=456, xui_user_uuid="test_uuid", is_active=True, expires_at=datetime.utcnow() - timedelta(days=1))
        
        mock_session.execute.return_value.scalars.return_value.all.return_value = [sub]
        mock_session.get.side_effect = [user, server]
        mock_xui_client.delete_user.return_value = {"success": True}

        await deactivate_expired_users(mock_session)

        mock_xui_client.delete_user.assert_called_once_with(server.inbound_id, sub.xui_user_uuid)
        assert sub.is_active is False
        mock_session.commit.assert_called_once()
        mock_logger.info.assert_any_call(f"Successfully deactivated user {user.telegram_id} from server {server.name}")

    async def test_deactivate_expired_users_xui_client_not_found_error(self, mock_session, mock_xui_client, mock_logger):
        user = AsyncMock(spec=User, telegram_id=123)
        server = AsyncMock(spec=Server, name="TestServer")
        sub = AsyncMock(spec=Subscription, user_id=123, server_id=456, xui_user_uuid="test_uuid", is_active=True, expires_at=datetime.utcnow() - timedelta(days=1))
        
        mock_session.execute.return_value.scalars.return_value.all.return_value = [sub]
        mock_session.get.side_effect = [user, server]
        mock_xui_client.delete_user.side_effect = XUIClientError("Client not found in X-UI")

        await deactivate_expired_users(mock_session)

        mock_xui_client.delete_user.assert_called_once_with(server.inbound_id, sub.xui_user_uuid)
        assert sub.is_active is False
        mock_session.commit.assert_called_once()
        mock_logger.warning.assert_called_once_with(f"Client {sub.xui_user_uuid} was already deleted in X-UI. Marking as inactive in DB.")

    async def test_deactivate_expired_users_other_xui_client_error(self, mock_session, mock_xui_client, mock_logger):
        user = AsyncMock(spec=User, telegram_id=123)
        server = AsyncMock(spec=Server, name="TestServer")
        sub = AsyncMock(spec=Subscription, user_id=123, server_id=456, xui_user_uuid="test_uuid", is_active=True, expires_at=datetime.utcnow() - timedelta(days=1))
        
        mock_session.execute.return_value.scalars.return_value.all.return_value = [sub]
        mock_session.get.side_effect = [user, server]
        mock_xui_client.delete_user.side_effect = XUIClientError("Some other XUI error")

        await deactivate_expired_users(mock_session)

        mock_xui_client.delete_user.assert_called_once_with(server.inbound_id, sub.xui_user_uuid)
        assert sub.is_active is True # Should not be deactivated if it's another XUI error
        mock_session.commit.assert_called_once()
        mock_logger.error.assert_called_once_with(f"XUI error deactivating {user.telegram_id} from server {server.name}: Some other XUI error")

    async def test_deactivate_expired_users_unexpected_error(self, mock_session, mock_xui_client, mock_logger):
        user = AsyncMock(spec=User, telegram_id=123)
        server = AsyncMock(spec=Server, name="TestServer")
        sub = AsyncMock(spec=Subscription, user_id=123, server_id=456, xui_user_uuid="test_uuid", is_active=True, expires_at=datetime.utcnow() - timedelta(days=1))
        
        mock_session.execute.return_value.scalars.return_value.all.return_value = [sub]
        mock_session.get.side_effect = [user, server]
        mock_xui_client.delete_user.side_effect = Exception("Unexpected error")

        await deactivate_expired_users(mock_session)

        mock_xui_client.delete_user.assert_called_once_with(server.inbound_id, sub.xui_user_uuid)
        assert sub.is_active is True # Should not be deactivated if it's an unexpected error
        mock_session.commit.assert_called_once()
        mock_logger.error.assert_called_once_with(f"Unexpected error deactivating {user.telegram_id} from server {server.name}: Unexpected error")