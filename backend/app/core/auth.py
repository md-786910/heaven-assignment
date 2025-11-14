from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.models.user import User as UserModel
from app.schemas.auth import TokenData

# HTTP Bearer token
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_password_hash(password: str) -> str:
    """Hash a password"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> TokenData:
    """Decode and verify a JWT token"""
    try:
        print(f"DEBUG: Attempting to decode token...")
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        print(f"DEBUG: Token payload: {payload}")
        user_id_str: str = payload.get("sub")
        username: str = payload.get("username")
        print(f"DEBUG: Extracted user_id_str={user_id_str}, username={username}")

        if user_id_str is None:
            print("DEBUG: user_id_str is None, raising 401")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Convert string user_id back to integer
        user_id = int(user_id_str)
        print(f"DEBUG: Converted user_id to int: {user_id}")

        return TokenData(user_id=user_id, username=username)
    except JWTError as e:
        print(f"DEBUG: JWTError occurred: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ValueError as e:
        print(f"DEBUG: ValueError converting user_id: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> UserModel:
    """Get the current authenticated user"""
    try:
        token = credentials.credentials
        print(f"DEBUG: Received token: {token[:20]}...")  # Print first 20 chars
        token_data = decode_access_token(token)
        print(f"DEBUG: Token decoded successfully, user_id: {token_data.user_id}")

        user = db.query(UserModel).filter(UserModel.id == token_data.user_id).first()

        if user is None:
            print(f"DEBUG: User not found for user_id: {token_data.user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            print(f"DEBUG: User {user.id} is inactive")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )

        print(f"DEBUG: Authentication successful for user: {user.username}")
        return user
    except Exception as e:
        print(f"DEBUG: Authentication failed with error: {str(e)}")
        raise


def get_current_active_user(
    current_user: UserModel = Depends(get_current_user)
) -> UserModel:
    """Get the current active user (alias for consistency)"""
    return current_user
