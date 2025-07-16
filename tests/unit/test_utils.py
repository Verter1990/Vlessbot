import pytest
import string

from core.handlers.user_handlers import generate_unique_code
from core import constants

def test_generate_unique_code_length():
    """Tests that the generated code has the correct length."""
    code = generate_unique_code()
    assert len(code) == constants.GIFT_CODE_LENGTH

def test_generate_unique_code_charset():
    """Tests that the generated code contains only allowed characters."""
    allowed_chars = set(string.ascii_letters + string.digits)
    code = generate_unique_code()
    assert set(code).issubset(allowed_chars)

def test_generate_unique_code_uniqueness():
    """Tests that multiple generated codes are unique."""
    codes = {generate_unique_code() for _ in range(100)}
    assert len(codes) == 100
