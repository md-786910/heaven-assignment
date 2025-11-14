from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UserInfo(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class TimelineEvent(BaseModel):
    id: int
    field_name: str
    old_value: str | None
    new_value: str | None
    changed_by_id: int
    changed_at: datetime
    changed_by: Optional[UserInfo] = None

    class Config:
        from_attributes = True
