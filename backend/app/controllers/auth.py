from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User as UserModel
from app.schemas.auth import (
    UserLogin,
    UserRegister,
    LoginResponse,
    UserResponse,
    PasswordResetRequest,
    PasswordResetResponse,
    PasswordResetConfirm,
)
from app.core.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
)
import random
import string


class AuthController:
    @staticmethod
    def register_user(user_data: UserRegister, db: Session) -> LoginResponse:
        """Register a new user"""
        # Check if username already exists
        existing_user = db.query(UserModel).filter(
            UserModel.username == user_data.username
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )

        # Check if email already exists
        existing_email = db.query(UserModel).filter(
            UserModel.email == user_data.email
        ).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create new user
        hashed_password = get_password_hash(user_data.password)
        db_user = UserModel(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            is_active=True,
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        # Create access token
        access_token = create_access_token(
            data={"sub": str(db_user.id), "username": db_user.username}
        )

        user_response = UserResponse(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            full_name=db_user.full_name,
            is_active=db_user.is_active,
        )

        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_response,
        )

    @staticmethod
    def login_user(credentials: UserLogin, db: Session) -> LoginResponse:
        """Authenticate user and return token"""
        # Find user by email
        user = db.query(UserModel).filter(
            UserModel.email == credentials.email
        ).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verify password
        if not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )

        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username}
        )

        user_response = UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
        )

        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_response,
        )

    @staticmethod
    def generate_reset_code() -> str:
        """Generate a random reset code"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=9))

    @staticmethod
    def request_password_reset(
        request: PasswordResetRequest, db: Session
    ) -> PasswordResetResponse:
        """Generate password reset code"""
        # Find user by email
        user = db.query(UserModel).filter(
            UserModel.email == request.email
        ).first()

        if not user:
            # For security, don't reveal if email exists
            # But still generate a fake code
            fake_code = AuthController.generate_reset_code()
            return PasswordResetResponse(
                reset_code=fake_code,
                message="If the email exists, a reset code has been generated."
            )

        # Generate reset code
        reset_code = AuthController.generate_reset_code()
        reset_code_expires = datetime.now(timezone.utc) + timedelta(hours=1)

        # Save reset code to user
        user.reset_code = reset_code
        user.reset_code_expires = reset_code_expires
        db.commit()

        return PasswordResetResponse(
            reset_code=reset_code,
            message="Reset code generated successfully. Code expires in 1 hour."
        )

    @staticmethod
    def reset_password(
        reset_data: PasswordResetConfirm, db: Session
    ) -> dict:
        """Reset user password with code"""
        # Find user by email
        user = db.query(UserModel).filter(
            UserModel.email == reset_data.email
        ).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Verify reset code
        if not user.reset_code or user.reset_code != reset_data.reset_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset code"
            )

        # Check if code is expired
        # Handle both timezone-aware (PostgreSQL) and naive (SQLite) datetimes
        now = datetime.now(timezone.utc)
        expires = user.reset_code_expires
        if expires:
            # If expires is naive (SQLite), make now naive for comparison
            if expires.tzinfo is None:
                now = now.replace(tzinfo=None)
            if expires < now:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Reset code has expired"
                )

        # Reset password
        user.hashed_password = get_password_hash(reset_data.new_password)
        user.reset_code = None
        user.reset_code_expires = None
        db.commit()

        return {"success": True, "message": "Password reset successfully"}

    @staticmethod
    def get_current_user_info(user: UserModel) -> UserResponse:
        """Get current user information"""
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
        )
