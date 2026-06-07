"""FastAPI dependencies: database session, current user, admin check."""

from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.core.security import decode_access_token
from app.models import User

security_scheme = HTTPBearer(auto_error=True)
web_security_scheme = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide an async database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def _get_user_from_token(db: AsyncSession, token: str) -> User:
    """Helper: decode JWT token and return user or raise 401."""
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get the current authenticated user from JWT token (API usage, requires Bearer header)."""
    return await _get_user_from_token(db, credentials.credentials)


async def get_current_user_for_web(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(web_security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get the current authenticated user from JWT token.

    Supports two methods:
    1. Authorization: Bearer <token> header (for HTMX/fetch requests)
    2. jwt_token cookie (for direct browser navigation)
    """
    token: str | None = None

    # 1. Try Authorization header first
    if credentials is not None:
        token = credentials.credentials

    # 2. Fall back to cookie
    if token is None:
        token = request.cookies.get("jwt_token")

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    return await _get_user_from_token(db, token)


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Check if the current user has admin role."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user
