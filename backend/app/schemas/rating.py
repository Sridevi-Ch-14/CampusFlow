from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.user import UserResponse

class RatingCreate(BaseModel):
    score: int = Field(ge=1, le=5)
    feedback: Optional[str] = None

class RatingResponse(BaseModel):
    id: str
    complaint_id: str
    score: int
    feedback: Optional[str] = None
    student: UserResponse
    created_at: datetime

    class Config:
        from_attributes = True
