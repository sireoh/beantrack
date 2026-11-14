"""Session-token hashing and at-rest encryption of Discord OAuth tokens."""

import hashlib
import secrets

from cryptography.fernet import Fernet


def new_session_token() -> str:
    """A fresh, unguessable session token. Only the client ever sees this raw value."""
    return secrets.token_urlsafe(32)


def hash_session_token(token: str) -> str:
    """SHA-256 hex digest of a session token; this is what the `sessions` table stores.

    A fast hash is fine here (unlike passwords): the token has 256 bits of entropy,
    so it cannot be brute-forced from the hash.
    """
    return hashlib.sha256(token.encode()).hexdigest()


class TokenCipher:
    """Symmetric encryption (Fernet: AES-128-CBC + HMAC-SHA256) for secrets stored in the DB."""

    def __init__(self, key: str) -> None:
        self._fernet = Fernet(key.encode())

    def encrypt(self, plaintext: str) -> str:
        return self._fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        return self._fernet.decrypt(ciphertext.encode()).decode()
