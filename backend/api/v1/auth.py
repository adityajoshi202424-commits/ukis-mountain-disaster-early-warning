"""
Authentication API Router

Endpoints:
- POST /api/v1/auth/login (User login, returns JWT token)
- POST /api/v1/auth/register (User registration)
- GET /api/v1/auth/me (Current user profile & RBAC permissions)
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from fastapi import APIRouter, HTTPException, Depends

from backend.services.auth import (
    auth_service,
    create_access_token,
    get_current_user,
    require_role,
)

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str = Field(..., example="admin")
    password: str = Field(..., example="AdminSecure2024!")


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    organization: str = "General Public"


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str
    role: str
    organization: str


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest):
    """Authenticates user and returns JWT token."""
    user = auth_service.authenticate_user(payload.username, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token(user.user_id, user.username, user.role)
    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user_id=user.user_id,
        username=user.username,
        role=user.role,
        organization=user.organization,
    )


@router.post("/register", response_model=AuthResponse)
async def register(payload: RegisterRequest):
    """Registers a new user account."""
    user = auth_service.register_user(
        username=payload.username,
        email=payload.email,
        password=payload.password,
        role="PUBLIC",
        org=payload.organization,
    )
    token = create_access_token(user.user_id, user.username, user.role)
    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user_id=user.user_id,
        username=user.username,
        role=user.role,
        organization=user.organization,
    )


@router.get("/me")
async def get_my_profile(current_user: Optional[dict] = Depends(get_current_user)):
    """Returns profile for currently authenticated user."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication token missing or invalid")
    return {
        "user_id": current_user.get("sub"),
        "username": current_user.get("username"),
        "role": current_user.get("role"),
        "is_authenticated": True,
    }
