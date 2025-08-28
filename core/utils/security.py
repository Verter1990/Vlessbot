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
    :param signature_header: The value of the 'Signature' or 'Yoo-Money-Signature' header.
    :return: True if the signature is valid, False otherwise.
    """
    # THIS IS THE TEST TO SEE IF NEW CODE IS DEPLOYED
    logger.critical("--- EXECUTING LATEST CODE v3 (verify_yookassa_signature) ---")
    
    try:
        # The header can be in two formats:
        # 1. "ts=1543515454,v1=long_signature_string" (key-value)
        # 2. "v1 <ts> <signature>" (space-separated, observed in user's logs)

        logger.info(f"Attempting to verify signature with header: {signature_header}")

        # Let's try to parse the key-value format first
        if '=' in signature_header:
            logger.info("Parsing as key-value format (ts=...,v1=...).")
            header_parts = {part.split('=')[0]: part.split('=')[1] for part in signature_header.split(',')}
            ts = header_parts.get('ts')
            received_signature = header_parts.get('v1')
        # Otherwise, parse the space-separated format
        else:
            logger.info("Parsing as space-separated format (v1 ...).")
            parts = signature_header.split(' ')
            # Based on logs: "v1 <ts> <some_number> <signature>" - let's assume ts is the second part.
            if parts[0] != 'v1' or len(parts) < 3:
                logger.warning(f"Unsupported signature format: {signature_header}")
                return False
            ts = parts[1]
            received_signature = parts[-1] # The signature is the last part

        if not ts or not received_signature:
            logger.warning(f"Could not parse timestamp or signature from header: {signature_header}")
            return False

        logger.info(f"Parsed ts: {ts}, Parsed signature: {received_signature}")
        secret_key = settings.YOOKASSA_SECRET_KEY.encode('utf-8')

        # The signature is based on the concatenation of the timestamp and the raw request body
        payload_to_sign = f"{ts}.".encode('utf-8') + request_body

        # Compute HMAC-SHA256 signature
        computed_signature = hmac.new(secret_key, payload_to_sign, hashlib.sha256).hexdigest()
        logger.info(f"Computed signature: {computed_signature}")

        # Compare computed signature with the one from the header
        is_valid = hmac.compare_digest(computed_signature, received_signature)
        logger.info(f"Signature validation result: {is_valid}")
        return is_valid
    except Exception as e:
        logger.error(f"An unexpected error occurred during signature verification: {e}", exc_info=True)
        return False
