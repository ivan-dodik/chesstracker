# SPDX-FileCopyrightText: 2026 Ivan Dodik
# SPDX-License-Identifier: AGPL-3.0-only

"""Security utilities: password hashing and JWT tokens."""

from datetime import UTC, datetime, timedelta

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings


def hash_password(password: str) -> str:
    """Hash a plain-text password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a bcrypt hash."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


def _decode_jwt_sync(token: str) -> dict | None:
    """Synchronous JWT decode (runs in thread pool)."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        return None


async def decode_access_token(token: str) -> dict | None:
    """Decode and validate a JWT access token. Returns the payload or None.

    Uses ``asyncio.to_thread`` to avoid blocking the event loop with
    synchronous cryptography operations from ``python-jose``.
    """
    import asyncio

    return await asyncio.to_thread(_decode_jwt_sync, token)
