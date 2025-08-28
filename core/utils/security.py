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
        logger.info("--- YooKassa Signature Verification ---")
        logger.info(f"Received Signature Header: {signature_header}")
        
        # The header is a string like: "ts=1543515454,v1=long_signature_string"
        header_parts = {part.split('='): part.split('=')[1] for part in signature_header.split(',')}
        ts = header_parts.get('ts')
        received_signature = header_parts.get('v1')

        if not ts or not received_signature:
            logger.error("Timestamp (ts) or signature (v1) not found in header.")
            return False

        logger.info(f"Parsed Timestamp (ts): {ts}")
        logger.info(f"Parsed Received Signature (v1): {received_signature}")

        secret_key = settings.YOOKASSA_SECRET_KEY.encode('utf-8')

        # The signature is based on the concatenation of the timestamp and the raw request body
        payload_to_sign = f"{ts}.".encode('utf-8') + request_body
        
        # Log the body and payload for debugging. Be careful with sensitive data in production.
        logger.info(f"Request Body (decoded for logging): {request_body.decode('utf-8', errors='ignore')}")
        logger.info(f"Payload for Signing (decoded for logging): {payload_to_sign.decode('utf-8', errors='ignore')}")

        # Compute HMAC-SHA256 signature
        computed_signature = hmac.new(secret_key, payload_to_sign, hashlib.sha256).hexdigest()
        logger.info(f"Computed Signature: {computed_signature}")

        # Compare computed signature with the one from the header
        is_valid = hmac.compare_digest(computed_signature, received_signature)
        logger.info(f"Signature is valid: {is_valid}")
        logger.info("--- End of Verification ---")
        return is_valid
    except (ValueError, KeyError, IndexError, UnicodeDecodeError) as e:
        logger.error(f"Error during signature parsing: {e}")
        # In case of parsing errors
        return False
