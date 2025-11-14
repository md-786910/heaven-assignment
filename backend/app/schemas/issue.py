from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from app.models.issue import IssueStatus, IssuePriority


class IssueBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: IssueStatus = IssueStatus.OPEN
    priority: IssuePriority = IssuePriority.MEDIUM
    assignee_id: Optional[int] = None


class IssueCreate(IssueBase):
    creator_id: int


class IssueUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[IssueStatus] = None
    priority: Optional[IssuePriority] = None
    assignee_id: Optional[int] = None
    version: int  # Required for optimistic concurrency control


class Issue(IssueBase):
    id: int
    creator_id: int
    version: int
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class IssueInDB(Issue):
    pass


class LabelSchema(BaseModel):
    id: int
    name: str
    color: str

    class Config:
        from_attributes = True


class UserInfo(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class CommentSchema(BaseModel):
    id: int
    body: str
    author_id: int
    created_at: datetime
    author: Optional['UserInfo'] = None

    class Config:
        from_attributes = True


class IssueWithDetails(Issue):
    comments: List[CommentSchema] = []
    labels: List[LabelSchema] = []

    class Config:
        from_attributes = True


class IssueBulkStatusUpdate(BaseModel):
    issue_ids: List[int]
    status: IssueStatus


class IssueFilter(BaseModel):
    status: Optional[IssueStatus] = None
    priority: Optional[IssuePriority] = None
    assignee_id: Optional[int] = None
    creator_id: Optional[int] = None
    skip: int = 0
    limit: int = 100
