from pydantic import BaseModel, Field
from datetime import datetime


class LabelBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    color: str = Field(default="#808080", pattern=r"^#[0-9A-Fa-f]{6}$")


class LabelCreate(LabelBase):
    pass


class Label(LabelBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class LabelInDB(Label):
    pass
