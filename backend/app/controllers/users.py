from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List
from app.models import User as UserModel
from app.schemas import UserCreate, User


class UserController:
    """Controller for user-related business logic"""

    @staticmethod
    def create_user(user: UserCreate, db: Session) -> UserModel:
        """Create a new user"""
        # Check if username or email already exists
        existing = db.query(UserModel).filter(
            (UserModel.username == user.username) | (UserModel.email == user.email)
        ).first()

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Username or email already exists"
            )

        db_user = UserModel(**user.model_dump())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def get_users(skip: int, limit: int, db: Session) -> List[UserModel]:
        """Get list of users with pagination"""
        return db.query(UserModel).offset(skip).limit(limit).all()

    @staticmethod
    def get_user_by_id(user_id: int, db: Session) -> UserModel:
        """Get a specific user by ID"""
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    @staticmethod
    def validate_user_exists(user_id: int, db: Session) -> UserModel:
        """Validate that a user exists and return it"""
        return UserController.get_user_by_id(user_id, db)
