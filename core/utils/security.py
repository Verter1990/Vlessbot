from cryptography.fernet import Fernet
import hmac
import hashlib
import json
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

def verify_yookassa_signature(request_body: bytes, signature_header: str) -> bool:
    """
    Verifies the YooKassa webhook signature.
    :param request_body: The raw HTTP request body (bytes).
    :param signature_header: The value of the 'YooKassa-Signature' header.
    :return: True if the signature is valid, False otherwise.
    """
    secret_key = settings.YOOKASSA_SECRET_KEY.encode('utf-8')
    
    # Compute HMAC-SHA256 signature
    computed_signature = hmac.new(secret_key, request_body, hashlib.sha256).hexdigest()
    
    # Compare computed signature with the one from the header
    return hmac.compare_digest(computed_signature, signature_header)