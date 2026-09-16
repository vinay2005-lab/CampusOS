"""Security utilities for authentication, authorization, and encryption.

Handles JWT tokens, password hashing, role-based access control, and CSRF protection.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Password hashing context
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Adjust for performance/security trade-off
)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    scopes={
        "read": "Read access",
        "write": "Write access",
        "admin": "Admin access"
    }
)


class TokenData(BaseModel):
    """JWT token payload data."""
    user_id: int
    email: str
    role: str
    student_id: Optional[str] = None
    exp: Optional[datetime] = None


class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


def hash_password(password: str) -> str:
    """Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        str: Hashed password

    Raises:
        ValueError: If password hashing fails
    """
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"Password hashing failed: {e}")
        raise ValueError("Password hashing failed")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to verify against

    Returns:
        bool: True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    user_id: int,
    email: str,
    role: str,
    student_id: Optional[str] = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token.

    Args:
        user_id: User ID
        email: User email
        role: User role (STUDENT, FACULTY, ADMIN, SUPER_ADMIN)
        student_id: Optional student ID
        expires_delta: Custom expiration time

    Returns:
        str: Encoded JWT token
    """
    if expires_delta is None:
        expires_delta = timedelta(
            minutes=settings.access_token_expire_minutes
        )

    expire = datetime.utcnow() + expires_delta
    to_encode = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "student_id": student_id,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    }

    try:
        encoded_jwt = jwt.encode(
            to_encode,
            settings.secret_key,
            algorithm=settings.algorithm
        )
        return encoded_jwt
    except Exception as e:
        logger.error(f"Token creation failed: {e}")
        raise ValueError("Token creation failed")


def create_refresh_token(
    user_id: int,
    email: str,
    role: str,
    student_id: Optional[str] = None
) -> str:
    """Create a JWT refresh token.

    Args:
        user_id: User ID
        email: User email
        role: User role
        student_id: Optional student ID

    Returns:
        str: Encoded refresh token
    """
    expire = datetime.utcnow() + timedelta(
        days=settings.refresh_token_expire_days
    )
    to_encode = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "student_id": student_id,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    }

    try:
        encoded_jwt = jwt.encode(
            to_encode,
            settings.secret_key,
            algorithm=settings.algorithm
        )
        return encoded_jwt
    except Exception as e:
        logger.error(f"Refresh token creation failed: {e}")
        raise ValueError("Refresh token creation failed")


def verify_token(token: str) -> TokenData:
    """Verify and decode a JWT token.

    Args:
        token: JWT token to verify

    Returns:
        TokenData: Decoded token data

    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        user_id: int = payload.get("user_id")
        email: str = payload.get("email")
        role: str = payload.get("role")
        student_id: Optional[str] = payload.get("student_id")

        if user_id is None or email is None:
            raise credentials_exception

        token_data = TokenData(
            user_id=user_id,
            email=email,
            role=role,
            student_id=student_id,
            exp=datetime.fromtimestamp(payload.get("exp"))
        )
    except JWTError as e:
        logger.warning(f"Token verification failed: {e}")
        raise credentials_exception

    return token_data


def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """Dependency to get current authenticated user.

    Args:
        token: JWT token from request header

    Returns:
        TokenData: Current user data

    Raises:
        HTTPException: If authentication fails
    """
    return verify_token(token)


def require_role(required_roles: list[str]):
    """Dependency to require specific roles.

    Args:
        required_roles: List of allowed roles

    Returns:
        Callable: Dependency function
    """
    async def role_checker(current_user: TokenData = Depends(get_current_user)):
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires one of: {', '.join(required_roles)}"
            )
        return current_user

    return role_checker


def generate_student_id(admission_year: int, branch_code: str, serial: int) -> str:
    """Generate unique student ID.

    Format: YY-BRANCH-SERIAL (e.g., 24-CSE-001)

    Args:
        admission_year: Year of admission (e.g., 2024)
        branch_code: Branch code (e.g., CSE, ECE, MECH)
        serial: Serial number

    Returns:
        str: Generated student ID
    """
    year = str(admission_year)[-2:]
    return f"{year}-{branch_code}-{serial:04d}"
