from datetime import datetime
from pydantic import BaseModel
from app.schemas.user import UserResponse

class AttachmentResponse(BaseModel):
    id: str
    complaint_id: str
    original_filename: str
    mime_type: str
    file_size: int
    storage_key: str
    uploader: UserResponse
    created_at: datetime
    url: str

    class Config:
        from_attributes = True
