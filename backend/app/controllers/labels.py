from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List

from app.models import Label as LabelModel, Issue as IssueModel, IssueLabel
from app.schemas import LabelCreate


class LabelController:
    """Controller for label-related business logic"""

    @staticmethod
    def create_label(label: LabelCreate, db: Session) -> LabelModel:
        """Create a new label"""
        # Check if label already exists
        existing = db.query(LabelModel).filter(LabelModel.name == label.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Label already exists")

        db_label = LabelModel(**label.model_dump())
        db.add(db_label)
        db.commit()
        db.refresh(db_label)
        return db_label

    @staticmethod
    def get_labels(skip: int, limit: int, db: Session) -> List[LabelModel]:
        """Get list of labels"""
        return db.query(LabelModel).offset(skip).limit(limit).all()

    @staticmethod
    def replace_issue_labels(
        issue_id: int,
        label_ids: List[int],
        db: Session
    ) -> List[LabelModel]:
        """Replace all labels for an issue atomically"""
        # Validate issue exists
        issue = db.query(IssueModel).filter(IssueModel.id == issue_id).first()
        if not issue:
            raise HTTPException(status_code=404, detail="Issue not found")

        # Validate all labels exist
        labels = db.query(LabelModel).filter(LabelModel.id.in_(label_ids)).all()
        if len(labels) != len(label_ids):
            raise HTTPException(
                status_code=404,
                detail="One or more labels not found"
            )

        try:
            # Remove all existing labels
            db.query(IssueLabel).filter(IssueLabel.issue_id == issue_id).delete()

            # Add new labels
            for label_id in label_ids:
                issue_label = IssueLabel(issue_id=issue_id, label_id=label_id)
                db.add(issue_label)

            db.commit()

            # Return updated labels
            updated_labels = db.query(LabelModel).filter(
                LabelModel.id.in_(label_ids)
            ).all()
            return updated_labels

        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))
