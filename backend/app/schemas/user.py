"""User schemas."""

from datetime import datetime

from pydantic import BaseModel


class LoginRequest(BaseModel):
    """Schema for login request."""
    username: str
    password: str


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    username: str
    password: str
    role: str = "user"


class UserRead(BaseModel):
    """Schema for reading user data."""
    id: int
    username: str
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"