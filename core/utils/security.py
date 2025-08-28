from cryptography.fernet import Fernet
import hmac
import hashlib
import json
from core.config import settings
from loguru import logger

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

def verify_yookassa_signature(request_body: bytes, signature_header: str) -> bool:
    """
    Verifies the YooKassa webhook signature.
    :param request_body: The raw HTTP request body (bytes).
    :param signature_header: The value of the 'Signature' header.
    :return: True if the signature is valid, False otherwise.
    """
    try:
        # The header is a string like: "ts=1543515454,v1=long_signature_string"
        header_parts = {part.split('='): part.split('=')[1] for part in signature_header.split(',')}
        ts = header_parts.get('ts')
        received_signature = header_parts.get('v1')

        if not ts or not received_signature:
            return False

        secret_key = settings.YOOKASSA_SECRET_KEY.encode('utf-8')

        # The signature is based on the concatenation of the timestamp and the raw request body
        payload_to_sign = f"{ts}.".encode('utf-8') + request_body

        # Compute HMAC-SHA256 signature
        computed_signature = hmac.new(secret_key, payload_to_sign, hashlib.sha256).hexdigest()

        # Compare computed signature with the one from the header
        return hmac.compare_digest(computed_signature, received_signature)
    except (ValueError, KeyError, IndexError, UnicodeDecodeError):
        # In case of parsing errors
        return False
