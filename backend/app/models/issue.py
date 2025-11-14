from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base


class IssueStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class IssuePriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    status = Column(Enum(IssueStatus), default=IssueStatus.OPEN, nullable=False, index=True)
    priority = Column(Enum(IssuePriority), default=IssuePriority.MEDIUM, nullable=False)
    version = Column(Integer, default=1, nullable=False)  # For optimistic concurrency control

    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True, index=True)

    # Relationships
    creator = relationship("User", foreign_keys=[creator_id], back_populates="created_issues")
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="assigned_issues")
    comments = relationship("Comment", back_populates="issue", cascade="all, delete-orphan")
    issue_labels = relationship("IssueLabel", back_populates="issue", cascade="all, delete-orphan")
    history = relationship("IssueHistory", back_populates="issue", cascade="all, delete-orphan")
