from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.complaint import ComplaintStatusEnum, PriorityEnum
from app.schemas.complaint import (
    ComplaintCreate,
    ComplaintResponse,
    ComplaintListResponse,
    ComplaintUpdateStatus,
    ComplaintAssign,
    ComplaintChangePriority
)
from app.services.auth_service import get_current_user, require_roles
from app.services.complaint_service import (
    create_complaint,
    get_complaint_by_id,
    update_complaint_status,
    filter_complaints
)
from app.services.assignment_service import assign_complaint_to_staff
from app.services.sla_service import calculate_sla_deadline
from app.models.status_history import ComplaintStatusHistory

router = APIRouter(prefix="/complaints", tags=["Complaints"])

@router.post("", response_model=ComplaintResponse, status_code=status.HTTP_201_CREATED)
def create_new_complaint(
    complaint_in: ComplaintCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    complaint = create_complaint(db, complaint_in, current_user)
    return get_complaint_by_id(db, complaint.id, current_user)

@router.get("", response_model=ComplaintListResponse)
def list_complaints(
    status: Optional[ComplaintStatusEnum] = None,
    priority: Optional[PriorityEnum] = None,
    category_id: Optional[str] = None,
    location_id: Optional[str] = None,
    building_id: Optional[str] = None,
    assigned_staff_id: Optional[str] = None,
    creator_id: Optional[str] = None,
    is_sla_breached: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    sort: str = Query(default="created_at_desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    items, total, total_pages = filter_complaints(
        db=db,
        current_user=current_user,
        status=status,
        priority=priority,
        category_id=category_id,
        location_id=location_id,
        building_id=building_id,
        assigned_staff_id=assigned_staff_id,
        creator_id=creator_id,
        is_sla_breached=is_sla_breached,
        search=search,
        page=page,
        page_size=page_size,
        sort=sort
    )
    return ComplaintListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.get("/{complaint_id}", response_model=ComplaintResponse)
def get_complaint(
    complaint_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_complaint_by_id(db, complaint_id, current_user)

@router.patch("/{complaint_id}/status", response_model=ComplaintResponse)
def change_complaint_status(
    complaint_id: str,
    status_update: ComplaintUpdateStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    update_complaint_status(db, complaint_id, status_update, current_user)
    return get_complaint_by_id(db, complaint_id, current_user)

@router.post("/{complaint_id}/assign", response_model=ComplaintResponse)
def assign_staff(
    complaint_id: str,
    assign_in: ComplaintAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.SUPER_ADMIN]))
):
    assign_complaint_to_staff(db, complaint_id, assign_in.staff_id, current_user, assign_in.notes)
    return get_complaint_by_id(db, complaint_id, current_user)

@router.patch("/{complaint_id}/priority", response_model=ComplaintResponse)
def change_complaint_priority(
    complaint_id: str,
    priority_in: ComplaintChangePriority,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.SUPER_ADMIN]))
):
    complaint = get_complaint_by_id(db, complaint_id, current_user)
    old_priority = complaint.priority
    complaint.priority = priority_in.priority
    complaint.sla_deadline = calculate_sla_deadline(db, priority_in.priority, complaint.created_at)

    history = ComplaintStatusHistory(
        complaint_id=complaint.id,
        previous_status=complaint.status,
        new_status=complaint.status,
        changed_by_id=current_user.id,
        comment=f"Priority updated from {old_priority.value} to {priority_in.priority.value}"
    )
    db.add(history)
    db.commit()
    return get_complaint_by_id(db, complaint_id, current_user)
