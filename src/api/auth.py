"""Authentication and authorization."""

from typing import Optional
from datetime import datetime, timezone, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from loguru import logger

from ..utils.config import get_settings
from ..database.queries import UserQueries
from ..database.models import User

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.

    Args:
        data: Token payload data
        expires_delta: Token expiration time

    Returns:
        Encoded JWT token

    Example:
        >>> token = create_access_token({"sub": "user@example.com"})
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire})

    try:
        encoded_jwt = jwt.encode(
            to_encode,
            settings.secret_key,
            algorithm=settings.jwt_algorithm,
        )
        return encoded_jwt
    except Exception as e:
        logger.error(f"Token creation error: {e}")
        raise


def verify_token(token: str) -> dict:
    """
    Verify JWT token and extract payload.

    Args:
        token: JWT token string

    Returns:
        Token payload

    Raises:
        HTTPException: If token is invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except JWTError as e:
        logger.warning(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """
    Get current authenticated user from token.

    Args:
        credentials: HTTP Bearer credentials

    Returns:
        Current user

    Raises:
        HTTPException: If authentication fails

    Example:
        >>> @app.get("/protected")
        >>> async def protected(user: User = Depends(get_current_user)):
        >>>     return {"user": user.email}
    """
    token = credentials.credentials
    payload = verify_token(token)

    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    # Get user from database
    user_queries = UserQueries()
    user = user_queries.get_user_by_email(email)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user (status must be 'active').

    Args:
        current_user: Current authenticated user

    Returns:
        Active user

    Raises:
        HTTPException: If user is not active
    """
    if current_user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account",
        )

    return current_user


def require_plan(required_plan: str):
    """
    Decorator to require specific subscription plan.

    Args:
        required_plan: Required plan level

    Returns:
        Dependency function

    Example:
        >>> @app.get("/premium")
        >>> async def premium_feature(user: User = Depends(require_plan("premium"))):
        >>>     return {"message": "Premium content"}
    """

    async def plan_checker(user: User = Depends(get_current_active_user)) -> User:
        plan_hierarchy = {
            "basic": 1,
            "pro": 2,
            "premium": 3,
            "bot": 4,
            "enterprise": 5,
        }

        user_level = plan_hierarchy.get(user.plan, 0)
        required_level = plan_hierarchy.get(required_plan, 999)

        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This feature requires {required_plan} plan or higher",
            )

        return user

    return plan_checker
