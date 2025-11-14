from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base


class IssueLabel(Base):
    __tablename__ = "issue_labels"
    __table_args__ = (
        UniqueConstraint('issue_id', 'label_id', name='uq_issue_label'),
    )

    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("issues.id"), nullable=False, index=True)
    label_id = Column(Integer, ForeignKey("labels.id"), nullable=False, index=True)

    # Relationships
    issue = relationship("Issue", back_populates="issue_labels")
    label = relationship("Label", back_populates="issue_labels")
