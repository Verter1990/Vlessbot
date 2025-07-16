import pytest
from aiogram.types import Message, User as AiogramUser
from sqlalchemy import select
from core.database.models import User
from core.handlers.user_handlers import command_start_handler
from aiogram.filters import CommandObject

@pytest.mark.asyncio
async def test_new_user_registration(session):
    """Test that a new user is registered in the database on /start command."""
    user_id = 123456789
    username = "testuser"
    
    # Mock a Message object
    message = Message(message_id=1, date=None, chat=None, from_user=AiogramUser(id=user_id, is_bot=False, first_name="Test", username=username))
    message.answer = lambda text, reply_markup=None: None # Mock the answer method

    # Mock a CommandObject
    command = CommandObject(prefix="/", command="start", args=None)

    # Call the handler
    await command_start_handler(message, command, session, None) # Pass None for bot as it's not used in this path

    # Verify user is in DB
    db_user = (await session.execute(select(User).where(User.telegram_id == user_id))).scalars().first()
    assert db_user is not None
    assert db_user.telegram_id == user_id
    assert db_user.username == username
    assert db_user.language_code == "en" # Default language from AiogramUser mock

@pytest.mark.asyncio
async def test_existing_user_start_command(session):
    """Test that an existing user is not re-registered on /start command."""
    user_id = 987654321
    username = "existinguser"

    # Pre-add user to DB
    existing_user = User(telegram_id=user_id, username=username, language_code="ru")
    session.add(existing_user)
    await session.commit()

    # Mock a Message object
    message = Message(message_id=1, date=None, chat=None, from_user=AiogramUser(id=user_id, is_bot=False, first_name="Existing", username=username))
    message.answer = lambda text, reply_markup=None: None # Mock the answer method

    # Mock a CommandObject
    command = CommandObject(prefix="/", command="start", args=None)

    # Call the handler
    await command_start_handler(message, command, session, None) # Pass None for bot

    # Verify user is still only one in DB
    users_count = (await session.execute(select(User).where(User.telegram_id == user_id))).scalar_one()
    assert users_count == 1

    db_user = (await session.execute(select(User).where(User.telegram_id == user_id))).scalars().first()
    assert db_user.language_code == "ru" # Ensure original language is preserved
