# core/utils/security.py

from cryptography.fernet import Fernet
from core.config import settings

# Initialize Fernet suite with the key from settings
fernet = Fernet(settings.ENCRYPTION_KEY.encode())

def encrypt_password(password: str) -> str:
    """Encrypts a password using Fernet encryption."""
    if not password:
        return ""
    return fernet.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password: str) -> str:
    """Decrypts a password using Fernet encryption."""
    if not encrypted_password:
        return ""
    return fernet.decrypt(encrypted_password.encode()).decode()
