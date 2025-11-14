from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.models import Issue as IssueModel, User as UserModel, IssueStatus
from app.schemas import TopAssignee, LatencyReport


class ReportController:
    """Controller for report-related business logic"""

    @staticmethod
    def get_top_assignees(limit: int, db: Session) -> List[TopAssignee]:
        """Get top assignees by number of issues"""
        results = db.query(
            UserModel.id.label('assignee_id'),
            UserModel.username.label('assignee_name'),
            func.count(IssueModel.id).label('issue_count')
        ).join(
            IssueModel, UserModel.id == IssueModel.assignee_id
        ).group_by(
            UserModel.id, UserModel.username
        ).order_by(
            func.count(IssueModel.id).desc()
        ).limit(limit).all()

        return [
            TopAssignee(
                assignee_id=r.assignee_id,
                assignee_name=r.assignee_name,
                issue_count=r.issue_count
            )
            for r in results
        ]

    @staticmethod
    def get_average_resolution_time(db: Session) -> LatencyReport:
        """Get average resolution time for resolved issues"""
        resolved_issues = db.query(IssueModel).filter(
            IssueModel.status == IssueStatus.RESOLVED,
            IssueModel.resolved_at.isnot(None)
        ).all()

        if not resolved_issues:
            return LatencyReport(
                average_resolution_time_hours=0,
                total_resolved_issues=0
            )

        total_time = 0
        for issue in resolved_issues:
            time_diff = issue.resolved_at - issue.created_at
            total_time += time_diff.total_seconds()

        avg_time_hours = (total_time / len(resolved_issues)) / 3600

        return LatencyReport(
            average_resolution_time_hours=round(avg_time_hours, 2),
            total_resolved_issues=len(resolved_issues)
        )
