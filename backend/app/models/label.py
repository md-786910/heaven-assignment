from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Label(Base):
    __tablename__ = "labels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    color = Column(String(7), default="#808080")  # Hex color code
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    issue_labels = relationship("IssueLabel", back_populates="label", cascade="all, delete-orphan")
