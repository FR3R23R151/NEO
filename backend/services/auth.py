"""
NEO Authentication Service

Replaces Supabase Auth with custom JWT-based authentication.
Provides user registration, login, session management, and authorization.
"""

import os
import hashlib
import secrets
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta, timezone
import jwt
import bcrypt
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request

from services.database import db_service
from utils.config import config

logger = logging.getLogger(__name__)

class AuthService:
    """
    NEO Authentication Service - JWT-based authentication system.
    Replaces Supabase Auth functionality.
    """
    
    def __init__(self):
        self.jwt_secret = config.get('JWT_SECRET', 'neo-jwt-secret-change-in-production')
        self.jwt_algorithm = 'HS256'
        self.access_token_expire_minutes = 60 * 24  # 24 hours
        self.refresh_token_expire_days = 30
        self.security = HTTPBearer()
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def generate_token(self, user_id: str, token_type: str = "access") -> str:
        """Generate JWT token."""
        now = datetime.now(timezone.utc)
        
        if token_type == "access":
            expire = now + timedelta(minutes=self.access_token_expire_minutes)
        else:  # refresh
            expire = now + timedelta(days=self.refresh_token_expire_days)
        
        payload = {
            "user_id": user_id,
            "type": token_type,
            "iat": now,
            "exp": expire
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    def generate_session_token(self) -> str:
        """Generate secure session token."""
        return secrets.token_urlsafe(32)
    
    def hash_session_token(self, token: str) -> str:
        """Hash session token for storage."""
        return hashlib.sha256(token.encode()).hexdigest()
    
    async def register_user(
        self,
        email: str,
        password: str,
        full_name: str = None,
        metadata: Dict = None
    ) -> Dict[str, Any]:
        """Register a new user."""
        try:
            # Check if user already exists
            existing_user = await db_service.get_user_by_email(email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User with this email already exists"
                )
            
            # Hash password
            password_hash = self.hash_password(password)
            
            # Create user
            user_id = await db_service.create_user(
                email=email,
                password_hash=password_hash,
                full_name=full_name,
                metadata=metadata
            )
            
            # Create personal account
            account_slug = email.split('@')[0] + '-' + secrets.token_hex(4)
            account_id = await db_service.create_account(
                name=f"{full_name or email}'s Account",
                slug=account_slug,
                personal_account=True,
                billing_email=email
            )
            
            # Add user to account as owner
            await db_service.add_user_to_account(account_id, user_id, "owner")
            
            # Generate tokens
            access_token = self.generate_token(user_id, "access")
            refresh_token = self.generate_token(user_id, "refresh")
            
            # Create session
            session_token = self.generate_session_token()
            session_hash = self.hash_session_token(session_token)
            expires_at = datetime.now(timezone.utc) + timedelta(days=self.refresh_token_expire_days)
            
            await db_service.create_session(
                user_id=user_id,
                token_hash=session_hash,
                expires_at=expires_at
            )
            
            logger.info(f"User registered: {email}")
            
            return {
                "user": {
                    "id": user_id,
                    "email": email,
                    "full_name": full_name
                },
                "access_token": access_token,
                "refresh_token": refresh_token,
                "session_token": session_token
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Registration failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration failed"
            )
    
    async def login_user(
        self,
        email: str,
        password: str,
        user_agent: str = None,
        ip_address: str = None
    ) -> Dict[str, Any]:
        """Login user with email and password."""
        try:
            # Get user by email
            user = await db_service.get_user_by_email(email)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            
            # Check if user is active
            if not user.get('is_active', True):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Account is disabled"
                )
            
            # Verify password
            if not self.verify_password(password, user['password_hash']):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            
            # Update last login
            await db_service.update_user_login(user['id'])
            
            # Generate tokens
            access_token = self.generate_token(user['id'], "access")
            refresh_token = self.generate_token(user['id'], "refresh")
            
            # Create session
            session_token = self.generate_session_token()
            session_hash = self.hash_session_token(session_token)
            expires_at = datetime.now(timezone.utc) + timedelta(days=self.refresh_token_expire_days)
            
            await db_service.create_session(
                user_id=user['id'],
                token_hash=session_hash,
                expires_at=expires_at,
                user_agent=user_agent,
                ip_address=ip_address
            )
            
            logger.info(f"User logged in: {email}")
            
            return {
                "user": {
                    "id": user['id'],
                    "email": user['email'],
                    "full_name": user['full_name']
                },
                "access_token": access_token,
                "refresh_token": refresh_token,
                "session_token": session_token
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Login failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Login failed"
            )
    
    async def logout_user(self, session_token: str):
        """Logout user by invalidating session."""
        try:
            session_hash = self.hash_session_token(session_token)
            await db_service.delete_session(session_hash)
            logger.info("User logged out")
        except Exception as e:
            logger.error(f"Logout failed: {e}")
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using refresh token."""
        try:
            # Verify refresh token
            payload = self.verify_token(refresh_token)
            
            if payload.get('type') != 'refresh':
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            user_id = payload['user_id']
            
            # Get user
            user = await db_service.get_user_by_id(user_id)
            if not user or not user.get('is_active', True):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found or inactive"
                )
            
            # Generate new access token
            access_token = self.generate_token(user_id, "access")
            
            return {
                "access_token": access_token,
                "user": {
                    "id": user['id'],
                    "email": user['email'],
                    "full_name": user['full_name']
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token refresh failed"
            )
    
    async def get_current_user(self, token: str) -> Dict[str, Any]:
        """Get current user from access token."""
        try:
            # Verify token
            payload = self.verify_token(token)
            
            if payload.get('type') != 'access':
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            user_id = payload['user_id']
            
            # Get user
            user = await db_service.get_user_by_id(user_id)
            if not user or not user.get('is_active', True):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found or inactive"
                )
            
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Get current user failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed"
            )
    
    async def get_current_user_from_request(self, request: Request) -> Dict[str, Any]:
        """Get current user from request (Bearer token)."""
        try:
            # Get authorization header
            authorization = request.headers.get("Authorization")
            if not authorization or not authorization.startswith("Bearer "):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Missing or invalid authorization header"
                )
            
            # Extract token
            token = authorization.split(" ")[1]
            
            # Get user
            return await self.get_current_user(token)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed"
            )
    
    async def check_account_access(self, user_id: str, account_id: str) -> bool:
        """Check if user has access to account."""
        try:
            user_accounts = await db_service.get_user_accounts(user_id)
            return any(account['id'] == account_id for account in user_accounts)
        except Exception as e:
            logger.error(f"Account access check failed: {e}")
            return False
    
    async def cleanup_expired_sessions(self):
        """Clean up expired sessions."""
        try:
            await db_service.cleanup_expired_sessions()
            logger.info("Expired sessions cleaned up")
        except Exception as e:
            logger.error(f"Session cleanup failed: {e}")

# Global auth service instance
auth_service = AuthService()