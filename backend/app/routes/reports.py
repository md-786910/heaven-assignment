from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas import TopAssignee, LatencyReport
from app.controllers import ReportController

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/top-assignees", response_model=List[TopAssignee])
def get_top_assignees(limit: int = 10, db: Session = Depends(get_db)):
    """Get top assignees by number of issues"""
    return ReportController.get_top_assignees(limit, db)


@router.get("/latency", response_model=LatencyReport)
def get_average_resolution_time(db: Session = Depends(get_db)):
    """Get average resolution time for resolved issues"""
    return ReportController.get_average_resolution_time(db)
