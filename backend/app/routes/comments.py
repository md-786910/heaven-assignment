from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User as UserModel
from app.schemas import Comment, CommentCreate
from app.controllers import CommentController

router = APIRouter(tags=["comments"])


@router.post("/issues/{issue_id}/comments", response_model=Comment, status_code=201)
def add_comment(
    issue_id: int,
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Add a comment to an issue (requires authentication)"""
    # Override author_id with current user
    comment.author_id = current_user.id
    return CommentController.create_comment(issue_id, comment, db)
