import os
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.storage import storage_service
from app.models.user import User
from app.models.attachment import ComplaintAttachment
from app.schemas.attachment import AttachmentResponse
from app.services.auth_service import get_current_user
from app.services.complaint_service import get_complaint_by_id
from app.core.exceptions import BadRequestException, NotFoundException

router = APIRouter(tags=["Attachments"])

ALLOWED_MIME_TYPES = [
    "image/jpeg", "image/png", "image/webp", "image/gif",
    "application/pdf", "text/plain",
    "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
]
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

@router.post("/complaints/{complaint_id}/attachments", response_model=AttachmentResponse, status_code=status.HTTP_201_CREATED)
def upload_attachment(
    complaint_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    complaint = get_complaint_by_id(db, complaint_id, current_user)

    if file.content_type not in ALLOWED_MIME_TYPES:
        raise BadRequestException(f"Invalid file type '{file.content_type}'. Allowed types: images, PDF, DOCX, TXT.")

    storage_key, filename, file_size = storage_service.save_file(file)

    if file_size > MAX_FILE_SIZE:
        storage_service.delete_file(storage_key)
        raise BadRequestException("File size exceeds maximum limit of 10 MB")

    attachment = ComplaintAttachment(
        complaint_id=complaint.id,
        uploader_id=current_user.id,
        original_filename=filename,
        storage_key=storage_key,
        mime_type=file.content_type or "application/octet-stream",
        file_size=file_size
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)

    attachment_url = f"/api/v1/attachments/{storage_key}"
    return AttachmentResponse(
        id=attachment.id,
        complaint_id=attachment.complaint_id,
        original_filename=attachment.original_filename,
        mime_type=attachment.mime_type,
        file_size=attachment.file_size,
        storage_key=attachment.storage_key,
        uploader=attachment.uploader,
        created_at=attachment.created_at,
        url=attachment_url
    )

@router.get("/attachments/{storage_key}")
def download_attachment(
    storage_key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    attachment = db.query(ComplaintAttachment).filter(ComplaintAttachment.storage_key == storage_key).first()
    if not attachment:
        raise NotFoundException("Attachment file not found")

    # Authorize access based on complaint ownership / role
    get_complaint_by_id(db, attachment.complaint_id, current_user)

    file_path = storage_service.get_file_path(storage_key)
    if not os.path.exists(file_path):
        raise NotFoundException("Attachment file not found on disk")

    filename = attachment.original_filename if attachment else storage_key
    media_type = attachment.mime_type if attachment else "application/octet-stream"

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type=media_type
    )
