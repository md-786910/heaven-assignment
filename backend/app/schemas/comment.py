from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class CommentBase(BaseModel):
    body: str = Field(..., min_length=1)


class CommentCreate(CommentBase):
    author_id: int


class UserInfo(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class Comment(CommentBase):
    id: int
    author_id: int
    issue_id: int
    created_at: datetime
    updated_at: datetime
    author: Optional[UserInfo] = None

    class Config:
        from_attributes = True


class CommentInDB(Comment):
    pass
