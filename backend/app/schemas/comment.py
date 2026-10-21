from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.schemas.user import UserResponse

class CommentCreate(BaseModel):
    content: str
    is_internal: bool = False

class CommentResponse(BaseModel):
    id: str
    complaint_id: str
    author: UserResponse
    content: str
    is_internal: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
