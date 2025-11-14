from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_user
from app.controllers.auth import AuthController
from app.schemas.auth import (
    UserLogin,
    UserRegister,
    LoginResponse,
    UserResponse,
    PasswordResetRequest,
    PasswordResetResponse,
    PasswordResetConfirm,
)
from app.models.user import User as UserModel

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    return AuthController.register_user(user_data, db)


@router.post("/login", response_model=LoginResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return access token"""
    return AuthController.login_user(credentials, db)


@router.post("/forgot-password", response_model=PasswordResetResponse)
def forgot_password(
    request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """Request password reset code"""
    return AuthController.request_password_reset(request, db)


@router.post("/reset-password")
def reset_password(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """Reset password with code"""
    return AuthController.reset_password(reset_data, db)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: UserModel = Depends(get_current_user)):
    """Get current user information"""
    return AuthController.get_current_user_info(current_user)


@router.post("/logout")
def logout():
    """Logout user (client should remove token)"""
    return {"success": True, "message": "Logged out successfully"}
