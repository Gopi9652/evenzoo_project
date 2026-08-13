from cryptography.fernet import Fernet
from app.config import settings

# Fernet requires a 32-byte URL-safe base64-encoded key.
# Generate once with: Fernet.generate_key() and store it in your .env — never regenerate
# in production once messages exist, or all previously encrypted messages become unreadable.
_cipher = Fernet(settings.MESSAGE_ENCRYPTION_KEY.encode())


def encrypt_message(plaintext: str) -> str:
    if not plaintext:
        return plaintext
    return _cipher.encrypt(plaintext.encode()).decode()


def decrypt_message(ciphertext: str) -> str:
    if not ciphertext:
        return ciphertext
    try:
        return _cipher.decrypt(ciphertext.encode()).decode()
    except Exception:
        # If decryption fails (e.g. legacy plaintext message from before encryption
        # was added), return it as-is rather than crashing the whole conversation view
        return ciphertext