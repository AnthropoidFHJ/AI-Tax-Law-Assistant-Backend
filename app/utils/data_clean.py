from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os, base64
from typing import Tuple
from app.config.config import settings

_DEF_ASSOCIATED_DATA = b"AITaxLawBDv1"


def _derive_key() -> bytes:
    if settings.ENCRYPTION_KEY:
        raw = base64.urlsafe_b64decode(settings.ENCRYPTION_KEY.encode())
        if len(raw) == 32:
            return raw
    return os.urandom(32)


def encrypt_bytes(data: bytes) -> Tuple[bytes, bytes]:
    key = _derive_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, data, _DEF_ASSOCIATED_DATA)
    return nonce, ct


def decrypt_bytes(nonce: bytes, ct: bytes) -> bytes:
    key = _derive_key()
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ct, _DEF_ASSOCIATED_DATA)


def sanitize_number(value: str) -> float:
    try:
        return float(value.replace(",", "").strip())
    except Exception:
        return 0.0
