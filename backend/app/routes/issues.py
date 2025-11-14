from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User as UserModel
from app.schemas import (
    Issue, IssueCreate, IssueUpdate, IssueWithDetails,
    IssueBulkStatusUpdate, CSVImportResult,
    TimelineEvent
)
from app.models import IssueStatus
from app.controllers import IssueController

router = APIRouter(prefix="/issues", tags=["issues"])


@router.post("/", response_model=Issue, status_code=201)
def create_issue(
    issue: IssueCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Create a new issue (requires authentication)"""
    return IssueController.create_issue(issue, db)


@router.get("/", response_model=List[Issue])
def list_issues(
    status: IssueStatus | None = None,
    assignee_id: int | None = None,
    creator_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List issues with optional filtering and pagination"""
    return IssueController.get_issues(status, assignee_id, creator_id, skip, limit, db)


@router.get("/{issue_id}", response_model=IssueWithDetails)
def get_issue(issue_id: int, db: Session = Depends(get_db)):
    """Get issue with comments and labels"""
    return IssueController.get_issue_by_id(issue_id, db)


@router.patch("/{issue_id}", response_model=Issue)
def update_issue(
    issue_id: int,
    issue_update: IssueUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Update issue with optimistic concurrency control (requires authentication)"""
    return IssueController.update_issue(issue_id, issue_update, current_user.id, db)


@router.post("/bulk-status", status_code=200)
def bulk_status_update(
    bulk_update: IssueBulkStatusUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Transactional bulk status update with rollback on error (requires authentication)"""
    return IssueController.bulk_status_update(bulk_update, current_user.id, db)


@router.post("/import", response_model=CSVImportResult)
async def import_issues(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Import issues from CSV file with validation (requires authentication)"""
    return await IssueController.import_issues_from_csv(file, db)


@router.get("/{issue_id}/timeline", response_model=List[TimelineEvent])
def get_issue_timeline(issue_id: int, db: Session = Depends(get_db)):
    """Get issue history timeline (Bonus feature)"""
    return IssueController.get_issue_timeline(issue_id, db)


@router.delete("/{issue_id}")
def delete_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Delete an issue (only by creator) (requires authentication)"""
    return IssueController.delete_issue(issue_id, current_user.id, db)
