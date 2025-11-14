from pydantic import BaseModel


class TopAssignee(BaseModel):
    assignee_id: int
    assignee_name: str
    issue_count: int


class LatencyReport(BaseModel):
    average_resolution_time_hours: float
    total_resolved_issues: int
