from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile
from typing import List, Dict, Any
from datetime import datetime
import csv
import io

from app.models import (
    Issue as IssueModel,
    IssueStatus,
    Comment as CommentModel,
    Label as LabelModel,
    IssueLabel,
    User as UserModel,
    IssueHistory
)
from app.schemas import (
    IssueCreate,
    IssueUpdate,
    IssueBulkStatusUpdate,
    CSVImportResult,
    CSVImportRow
)


class IssueController:
    """Controller for issue-related business logic"""

    @staticmethod
    def create_issue(issue: IssueCreate, db: Session) -> IssueModel:
        """Create a new issue"""
        # Validate creator exists
        creator = db.query(UserModel).filter(UserModel.id == issue.creator_id).first()
        if not creator:
            raise HTTPException(status_code=404, detail="Creator not found")

        # Validate assignee if provided
        if issue.assignee_id:
            assignee = db.query(UserModel).filter(
                UserModel.id == issue.assignee_id
            ).first()
            if not assignee:
                raise HTTPException(status_code=404, detail="Assignee not found")

        db_issue = IssueModel(**issue.model_dump())
        db.add(db_issue)
        db.commit()
        db.refresh(db_issue)

        # Create history entry
        IssueController._create_history_entry(
            db=db,
            issue_id=db_issue.id,
            changed_by_id=issue.creator_id,
            field_name="created",
            old_value=None,
            new_value="Issue created"
        )

        return db_issue

    @staticmethod
    def get_issues(
        status: IssueStatus | None,
        assignee_id: int | None,
        creator_id: int | None,
        skip: int,
        limit: int,
        db: Session
    ) -> List[IssueModel]:
        """Get list of issues with filtering and pagination"""
        query = db.query(IssueModel)

        if status:
            query = query.filter(IssueModel.status == status)
        if assignee_id:
            query = query.filter(IssueModel.assignee_id == assignee_id)
        if creator_id:
            query = query.filter(IssueModel.creator_id == creator_id)

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_issue_by_id(issue_id: int, db: Session) -> Dict[str, Any]:
        """Get issue with comments and labels"""
        issue = db.query(IssueModel).filter(IssueModel.id == issue_id).first()
        if not issue:
            raise HTTPException(status_code=404, detail="Issue not found")

        # Get comments
        comments = db.query(CommentModel).filter(
            CommentModel.issue_id == issue_id
        ).all()

        # Get labels
        labels = db.query(LabelModel).join(IssueLabel).filter(
            IssueLabel.issue_id == issue_id
        ).all()

        return {
            **issue.__dict__,
            "comments": comments,
            "labels": labels
        }

    @staticmethod
    def update_issue(
        issue_id: int,
        issue_update: IssueUpdate,
        current_user_id: int,
        db: Session
    ) -> IssueModel:
        """Update issue with optimistic concurrency control"""
        db_issue = db.query(IssueModel).filter(IssueModel.id == issue_id).first()
        if not db_issue:
            raise HTTPException(status_code=404, detail="Issue not found")

        # Optimistic concurrency check
        if db_issue.version != issue_update.version:
            raise HTTPException(
                status_code=409,
                detail=f"Version mismatch. Expected {db_issue.version}, "
                       f"got {issue_update.version}"
            )

        # Track changes for history
        changes = []
        update_data = issue_update.model_dump(exclude_unset=True, exclude={"version"})

        for field, new_value in update_data.items():
            old_value = getattr(db_issue, field)
            if old_value != new_value:
                changes.append({
                    "field_name": field,
                    "old_value": str(old_value) if old_value is not None else None,
                    "new_value": str(new_value) if new_value is not None else None
                })
                setattr(db_issue, field, new_value)

        # Update resolved_at if status changed to resolved
        if "status" in update_data and update_data["status"] == IssueStatus.RESOLVED:
            if db_issue.resolved_at is None:
                db_issue.resolved_at = datetime.now()

        # Increment version
        db_issue.version += 1

        db.commit()
        db.refresh(db_issue)

        # Create history entries
        for change in changes:
            IssueController._create_history_entry(
                db=db,
                issue_id=issue_id,
                changed_by_id=current_user_id,
                **change
            )

        return db_issue

    @staticmethod
    def bulk_status_update(
        bulk_update: IssueBulkStatusUpdate,
        current_user_id: int,
        db: Session
    ) -> Dict[str, str]:
        """Transactional bulk status update with rollback on error"""
        try:
            # Start transaction
            issues = db.query(IssueModel).filter(
                IssueModel.id.in_(bulk_update.issue_ids)
            ).all()

            if len(issues) != len(bulk_update.issue_ids):
                raise HTTPException(
                    status_code=404,
                    detail="One or more issues not found"
                )

            # Update all issues
            for issue in issues:
                old_status = issue.status
                issue.status = bulk_update.status
                issue.version += 1

                # Update resolved_at if needed
                if (bulk_update.status == IssueStatus.RESOLVED and
                        issue.resolved_at is None):
                    issue.resolved_at = datetime.now()

                # Create history entry
                IssueController._create_history_entry(
                    db=db,
                    issue_id=issue.id,
                    changed_by_id=current_user_id,
                    field_name="status",
                    old_value=old_status.value,
                    new_value=bulk_update.status.value
                )

            db.commit()
            return {"message": f"Successfully updated {len(issues)} issues"}

        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    async def import_issues_from_csv(
        file: UploadFile,
        db: Session
    ) -> CSVImportResult:
        """Import issues from CSV file with validation"""
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV")

        content = await file.read()
        csv_file = io.StringIO(content.decode('utf-8'))
        reader = csv.DictReader(csv_file)

        results = []
        successful = 0
        failed = 0

        for row_num, row in enumerate(reader, start=2):
            result = IssueController._process_csv_row(row, row_num, db)
            results.append(result)

            if result.success:
                successful += 1
            else:
                failed += 1

        db.commit()

        return CSVImportResult(
            total_rows=len(results),
            successful=successful,
            failed=failed,
            results=results
        )

    @staticmethod
    def get_issue_timeline(issue_id: int, db: Session) -> List[IssueHistory]:
        """Get issue history timeline"""
        issue = db.query(IssueModel).filter(IssueModel.id == issue_id).first()
        if not issue:
            raise HTTPException(status_code=404, detail="Issue not found")

        timeline = db.query(IssueHistory).filter(
            IssueHistory.issue_id == issue_id
        ).order_by(IssueHistory.changed_at.desc()).all()

        return timeline

    @staticmethod
    def _create_history_entry(
        db: Session,
        issue_id: int,
        changed_by_id: int,
        field_name: str,
        old_value: str | None,
        new_value: str | None
    ) -> None:
        """Helper method to create history entry"""
        history = IssueHistory(
            issue_id=issue_id,
            changed_by_id=changed_by_id,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value
        )
        db.add(history)
        db.commit()

    @staticmethod
    def _process_csv_row(
        row: Dict[str, str],
        row_num: int,
        db: Session
    ) -> CSVImportRow:
        """Process a single CSV row"""
        errors = []
        issue_id = None

        try:
            # Validate required fields
            if not row.get('title'):
                errors.append("Title is required")
            if not row.get('creator_id'):
                errors.append("Creator ID is required")

            if errors:
                return CSVImportRow(
                    row_number=row_num,
                    success=False,
                    errors=errors
                )

            # Validate creator exists
            creator_id = int(row['creator_id'])
            creator = db.query(UserModel).filter(UserModel.id == creator_id).first()
            if not creator:
                return CSVImportRow(
                    row_number=row_num,
                    success=False,
                    errors=[f"Creator with ID {creator_id} not found"]
                )

            # Validate assignee if provided
            assignee_id = row.get('assignee_id')
            if assignee_id:
                assignee_id = int(assignee_id)
                assignee = db.query(UserModel).filter(
                    UserModel.id == assignee_id
                ).first()
                if not assignee:
                    return CSVImportRow(
                        row_number=row_num,
                        success=False,
                        errors=[f"Assignee with ID {assignee_id} not found"]
                    )
            else:
                assignee_id = None

            # Create issue
            issue = IssueModel(
                title=row['title'],
                description=row.get('description', ''),
                status=IssueStatus(row.get('status', 'open')),
                priority=row.get('priority', 'medium'),
                creator_id=creator_id,
                assignee_id=assignee_id
            )
            db.add(issue)
            db.flush()  # Get the issue ID without committing

            issue_id = issue.id
            return CSVImportRow(
                row_number=row_num,
                success=True,
                issue_id=issue_id
            )

        except Exception as e:
            return CSVImportRow(
                row_number=row_num,
                success=False,
                errors=[str(e)]
            )

    @staticmethod
    def delete_issue(issue_id: int, current_user_id: int, db: Session) -> dict:
        """Delete an issue (only by creator)"""
        db_issue = db.query(IssueModel).filter(IssueModel.id == issue_id).first()

        if not db_issue:
            raise HTTPException(status_code=404, detail="Issue not found")

        # Check ownership - only creator can delete
        if db_issue.creator_id != current_user_id:
            raise HTTPException(
                status_code=403,
                detail="You can only delete issues created by you"
            )

        # Delete associated records first (cascade)
        db.query(CommentModel).filter(CommentModel.issue_id == issue_id).delete()
        db.query(IssueLabel).filter(IssueLabel.issue_id == issue_id).delete()
        db.query(IssueHistory).filter(IssueHistory.issue_id == issue_id).delete()

        # Delete the issue
        db.delete(db_issue)
        db.commit()

        return {"success": True, "message": "Issue deleted successfully"}
