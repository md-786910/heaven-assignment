from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas import Label, LabelCreate
from app.controllers import LabelController

router = APIRouter(prefix="/labels", tags=["labels"])


@router.post("/", response_model=Label, status_code=201)
def create_label(label: LabelCreate, db: Session = Depends(get_db)):
    """Create a new label"""
    return LabelController.create_label(label, db)


@router.get("/", response_model=List[Label])
def list_labels(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all labels"""
    return LabelController.get_labels(skip, limit, db)


@router.put("/issues/{issue_id}/labels", response_model=List[Label])
def replace_issue_labels(issue_id: int, label_ids: List[int] = Query(...), db: Session = Depends(get_db)):
    """Replace all labels for an issue atomically"""
    return LabelController.replace_issue_labels(issue_id, label_ids, db)
