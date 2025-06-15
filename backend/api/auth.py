"""
NEO Authentication API

Provides authentication endpoints for user registration, login, and session management.
Replaces Supabase Auth API.
"""

from fastapi import APIRouter, HTTPException, status, Request, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any

from services.auth import auth_service
from services.database import db_service

router = APIRouter(prefix="/auth", tags=["authentication"])

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class AuthResponse(BaseModel):
    user: Dict[str, Any]
    access_token: str
    refresh_token: str
    session_token: str

class UserResponse(BaseModel):
    user: Dict[str, Any]

@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """Register a new user."""
    return await auth_service.register_user(
        email=request.email,
        password=request.password,
        full_name=request.full_name
    )

@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, http_request: Request):
    """Login user with email and password."""
    user_agent = http_request.headers.get("User-Agent")
    ip_address = http_request.client.host if http_request.client else None
    
    return await auth_service.login_user(
        email=request.email,
        password=request.password,
        user_agent=user_agent,
        ip_address=ip_address
    )

@router.post("/logout")
async def logout(request: Request):
    """Logout user."""
    # Get session token from header or cookie
    session_token = request.headers.get("X-Session-Token")
    if not session_token:
        # Try to get from cookie
        session_token = request.cookies.get("session_token")
    
    if session_token:
        await auth_service.logout_user(session_token)
    
    return {"message": "Logged out successfully"}

@router.post("/refresh", response_model=Dict[str, Any])
async def refresh_token(request: RefreshTokenRequest):
    """Refresh access token."""
    return await auth_service.refresh_token(request.refresh_token)

@router.get("/me", response_model=UserResponse)
async def get_current_user(request: Request):
    """Get current user information."""
    user = await auth_service.get_current_user_from_request(request)
    return {"user": user}

@router.get("/accounts")
async def get_user_accounts(request: Request):
    """Get user accounts."""
    user = await auth_service.get_current_user_from_request(request)
    accounts = await db_service.get_user_accounts(user['id'])
    return {"accounts": accounts}

@router.post("/verify-email")
async def verify_email(email: EmailStr):
    """Verify email address (placeholder for email verification)."""
    # TODO: Implement email verification logic
    return {"message": "Email verification sent"}

@router.post("/reset-password")
async def reset_password(email: EmailStr):
    """Reset password (placeholder for password reset)."""
    # TODO: Implement password reset logic
    return {"message": "Password reset email sent"}

@router.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    request: Request
):
    """Change user password."""
    user = await auth_service.get_current_user_from_request(request)
    
    # Verify current password
    user_data = await db_service.get_user_by_id(user['id'])
    if not auth_service.verify_password(current_password, user_data['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    new_password_hash = auth_service.hash_password(new_password)
    await db_service.update(
        "users",
        {"password_hash": new_password_hash},
        {"id": user['id']}
    )
    
    return {"message": "Password changed successfully"}