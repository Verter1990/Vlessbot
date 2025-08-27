import pytest
import pytest
from aiogram.types import Message, User as AiogramUser, Chat
from datetime import datetime
from sqlalchemy import select
from core.database.models import User
from core.handlers.user_handlers import command_start_handler
from aiogram.filters import CommandObject
