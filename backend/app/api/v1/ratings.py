from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.rating import Rating
from app.models.complaint import ComplaintStatusEnum
from app.schemas.rating import RatingCreate, RatingResponse
from app.services.auth_service import get_current_user
from app.services.complaint_service import get_complaint_by_id
from app.core.exceptions import BadRequestException, PermissionDeniedException

router = APIRouter(prefix="/complaints", tags=["Ratings"])

@router.post("/{complaint_id}/rating", response_model=RatingResponse, status_code=status.HTTP_201_CREATED)
def rate_service_resolution(
    complaint_id: str,
    rating_in: RatingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    complaint = get_complaint_by_id(db, complaint_id, current_user)

    if current_user.id != complaint.creator_id:
        raise PermissionDeniedException("Only the student who submitted the complaint can rate the service")

    if complaint.status not in [ComplaintStatusEnum.RESOLVED, ComplaintStatusEnum.CLOSED]:
        raise BadRequestException("Can only rate complaints that are resolved or closed")

    existing_rating = db.query(Rating).filter(Rating.complaint_id == complaint_id).first()
    if existing_rating:
        raise BadRequestException("Service for this complaint has already been rated")

    rating = Rating(
        complaint_id=complaint.id,
        student_id=current_user.id,
        score=rating_in.score,
        feedback=rating_in.feedback
    )
    db.add(rating)
    db.commit()
    db.refresh(rating)
    return rating
