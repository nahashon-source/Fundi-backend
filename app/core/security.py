"""
Password hashing and JWT token creation/verification.
Centralized here so no other file ever touches bcrypt or jose directly —
keeps the crypto surface area small and auditable.
"""
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hashes a plaintext password for storage. Never store raw passwords."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Checks a plaintext password against a stored hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Creates a short-lived JWT access token carrying the given claims (e.g. user id, role)."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(data: dict) -> str:
    """Creates a longer-lived JWT refresh token, used only to mint new access tokens."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> dict:
    """
    Decodes and validates a JWT. Raises jose.JWTError on expiry or tampering —
    callers (dependencies) are responsible for converting that into an HTTP 401.
    """
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])