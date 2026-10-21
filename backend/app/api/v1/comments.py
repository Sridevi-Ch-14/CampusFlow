from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.comment import ComplaintComment
from app.schemas.comment import CommentCreate, CommentResponse
from app.services.auth_service import get_current_user
from app.services.complaint_service import get_complaint_by_id
from app.services.notification_service import create_notification

router = APIRouter(prefix="/complaints", tags=["Comments"])

@router.post("/{complaint_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def add_comment(
    complaint_id: str,
    comment_in: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    complaint = get_complaint_by_id(db, complaint_id, current_user)

    comment = ComplaintComment(
        complaint_id=complaint.id,
        author_id=current_user.id,
        content=comment_in.content,
        is_internal=comment_in.is_internal
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    # Trigger notifications
    if current_user.id != complaint.creator_id:
        create_notification(
            db,
            recipient_id=complaint.creator_id,
            title="New Comment on Complaint",
            message=f"{current_user.full_name} commented on '{complaint.title}' ({complaint.complaint_number}).",
            notification_type="COMMENT",
            reference_id=complaint.id
        )
    elif complaint.assigned_staff_id and current_user.id != complaint.assigned_staff_id:
        create_notification(
            db,
            recipient_id=complaint.assigned_staff_id,
            title="Student Commented",
            message=f"Student {current_user.full_name} commented on '{complaint.title}' ({complaint.complaint_number}).",
            notification_type="COMMENT",
            reference_id=complaint.id
        )

    return comment
