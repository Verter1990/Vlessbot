# tests/integration/test_handlers.py

import pytest
from unittest.mock import AsyncMock, MagicMock

from aiogram.filters import CommandObject
from aiogram.types import Message, User as AiogramUser, Chat
from datetime import datetime

from core.handlers.user_handlers import command_start_handler
from core.database.models import User

@pytest.mark.asyncio
async def test_start_command_new_user(mocker):
    """Integration test for the /start command with a new user."""
    # 1. Setup Mocks
    session_mock = AsyncMock()

    # Correctly mock the chain for fetching the user
    execute_result_user = MagicMock()
    scalars_result_user = MagicMock()
    scalars_result_user.first.return_value = None  # Simulate user not found
    execute_result_user.scalars.return_value = scalars_result_user

    # Correctly mock the chain for fetching subscriptions
    execute_result_subs = MagicMock()
    scalars_result_subs = MagicMock()
    scalars_result_subs.all.return_value = []  # No subscriptions
    execute_result_subs.scalars.return_value = scalars_result_subs

    # Correctly mock the chain for fetching referrals
    execute_result_referrals = MagicMock()
    execute_result_referrals.scalar_one.return_value = 0 # No referrals

    # The handler calls session.execute three times: get_user, get_subscriptions, get_referrals
    session_mock.execute.side_effect = [execute_result_user, execute_result_subs, execute_result_referrals]

    # Mock the message object and its methods
    message_mock = AsyncMock(spec=Message)
    message_mock.from_user = AiogramUser(id=12345, is_bot=False, first_name="Test", language_code="en")
    message_mock.chat = Chat(id=12345, type="private")
    message_mock.date = datetime.now() # Add date
    message_mock.answer = AsyncMock(return_value=None) # Mock the answer method

    command = CommandObject(prefix="/", command="start", args=None)
    bot_mock = AsyncMock()

    # 2. Call the handler
    await command_start_handler(message=message_mock, command=command, session=session_mock, bot=bot_mock)

    # 3. Assertions
    # Assert that a new user was added to the session
    assert session_mock.add.call_count == 1
    added_user = session_mock.add.call_args[0][0]
    assert isinstance(added_user, User)
    assert added_user.telegram_id == 12345

    # Assert that commit and refresh were called
    assert session_mock.commit.call_count > 0
    assert session_mock.refresh.call_count == 1

    # Assert that the new user welcome message was sent
    assert message_mock.answer.call_count == 1
    sent_text = message_mock.answer.call_args[0][0]
    sent_reply_markup = message_mock.answer.call_args[1]['reply_markup']

    assert "What can this bot do?" in sent_text # Check for new user welcome message
    assert sent_reply_markup is not None
    assert sent_reply_markup.inline_keyboard[0][0].text == "Let's go!"
    assert sent_reply_markup.inline_keyboard[0][0].callback_data == "show_main_menu_after_welcome"
