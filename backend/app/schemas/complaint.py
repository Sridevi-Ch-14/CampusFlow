from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.complaint import PriorityEnum, ComplaintStatusEnum
from app.schemas.user import UserResponse
from app.schemas.category import CategoryResponse
from app.schemas.location import RoomDetailResponse
from app.schemas.comment import CommentResponse
from app.schemas.attachment import AttachmentResponse
from app.schemas.rating import RatingResponse

class ComplaintCreate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    description: str
    category_id: str
    location_id: str
    specific_location_details: Optional[str] = None
    priority: Optional[PriorityEnum] = None

class ComplaintUpdateStatus(BaseModel):
    target_status: ComplaintStatusEnum
    resolution_notes: Optional[str] = None
    comment: Optional[str] = None

class ComplaintAssign(BaseModel):
    staff_id: str
    notes: Optional[str] = None

class ComplaintChangePriority(BaseModel):
    priority: PriorityEnum

class StatusHistoryResponse(BaseModel):
    id: str
    previous_status: Optional[ComplaintStatusEnum] = None
    new_status: ComplaintStatusEnum
    changed_by: Optional[UserResponse] = None
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class AssignmentHistoryResponse(BaseModel):
    id: str
    staff: UserResponse
    assigned_by: Optional[UserResponse] = None
    assigned_at: datetime
    unassigned_at: Optional[datetime] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True

class ComplaintResponse(BaseModel):
    id: str
    complaint_number: str
    title: str
    description: str
    category: CategoryResponse
    location: RoomDetailResponse
    specific_location_details: Optional[str] = None
    priority: PriorityEnum
    status: ComplaintStatusEnum
    creator: UserResponse
    assigned_staff: Optional[UserResponse] = None
    sla_deadline: datetime
    is_sla_breached: bool
    resolution_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    
    status_history: List[StatusHistoryResponse] = []
    assignments: List[AssignmentHistoryResponse] = []
    comments: List[CommentResponse] = []
    attachments: List[AttachmentResponse] = []
    rating: Optional[RatingResponse] = None

    class Config:
        from_attributes = True

class ComplaintListItemResponse(BaseModel):
    id: str
    complaint_number: str
    title: str
    category: CategoryResponse
    location: RoomDetailResponse
    priority: PriorityEnum
    status: ComplaintStatusEnum
    creator: UserResponse
    assigned_staff: Optional[UserResponse] = None
    sla_deadline: datetime
    is_sla_breached: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ComplaintListResponse(BaseModel):
    items: List[ComplaintListItemResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
