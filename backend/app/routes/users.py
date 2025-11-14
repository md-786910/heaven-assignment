from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas import UserCreate
from app.schemas.user import User
from app.controllers import UserController

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=User, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    return UserController.create_user(user, db)


@router.get("/", response_model=List[User])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all users"""
    return UserController.get_users(skip, limit, db)


@router.get("/{user_id}", response_model=User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user"""
    return UserController.get_user_by_id(user_id, db)
