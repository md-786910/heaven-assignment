from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models import Comment as CommentModel, Issue as IssueModel, User as UserModel
from app.schemas import CommentCreate


class CommentController:
    """Controller for comment-related business logic"""

    @staticmethod
    def create_comment(
        issue_id: int,
        comment: CommentCreate,
        db: Session
    ) -> CommentModel:
        """Add a comment to an issue"""
        # Validate issue exists
        issue = db.query(IssueModel).filter(IssueModel.id == issue_id).first()
        if not issue:
            raise HTTPException(status_code=404, detail="Issue not found")

        # Validate author exists
        author = db.query(UserModel).filter(UserModel.id == comment.author_id).first()
        if not author:
            raise HTTPException(status_code=404, detail="Author not found")

        # Validate body is not empty
        if not comment.body.strip():
            raise HTTPException(
                status_code=400,
                detail="Comment body cannot be empty"
            )

        db_comment = CommentModel(
            **comment.model_dump(),
            issue_id=issue_id
        )
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)

        return db_comment
