from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.models.complaint import PriorityEnum

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    default_priority: PriorityEnum = PriorityEnum.MEDIUM

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    default_priority: Optional[PriorityEnum] = None
    is_active: Optional[bool] = None

class CategoryResponse(CategoryBase):
    id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
