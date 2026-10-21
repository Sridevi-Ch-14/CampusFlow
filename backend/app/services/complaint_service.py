import math
from datetime import datetime
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, desc, asc, func

from app.models.complaint import Complaint, ComplaintStatusEnum, PriorityEnum
from app.models.status_history import ComplaintStatusHistory
from app.models.assignment import ComplaintAssignment
from app.models.category import Category
from app.models.location import Room, Floor, Building
from app.models.user import User, UserRole
from app.schemas.complaint import ComplaintCreate, ComplaintUpdateStatus
from app.services.sla_service import calculate_sla_deadline
from app.services.notification_service import create_notification
from app.core.exceptions import (
    NotFoundException,
    PermissionDeniedException,
    BadRequestException,
    InvalidStateTransitionException
)

ALLOWED_TRANSITIONS = {
    ComplaintStatusEnum.OPEN: [ComplaintStatusEnum.ASSIGNED, ComplaintStatusEnum.REJECTED],
    ComplaintStatusEnum.ASSIGNED: [ComplaintStatusEnum.IN_PROGRESS, ComplaintStatusEnum.ASSIGNED, ComplaintStatusEnum.REJECTED],
    ComplaintStatusEnum.IN_PROGRESS: [ComplaintStatusEnum.RESOLVED, ComplaintStatusEnum.ASSIGNED],
    ComplaintStatusEnum.RESOLVED: [ComplaintStatusEnum.CLOSED, ComplaintStatusEnum.REOPENED],
    ComplaintStatusEnum.REOPENED: [ComplaintStatusEnum.ASSIGNED, ComplaintStatusEnum.IN_PROGRESS],
    ComplaintStatusEnum.REJECTED: [],
    ComplaintStatusEnum.CLOSED: []
}

def generate_complaint_number(db: Session) -> str:
    count = db.query(Complaint).count()
    return f"CF-{10000 + count + 1}"

def create_complaint(db: Session, complaint_in: ComplaintCreate, creator: User) -> Complaint:
    category = db.query(Category).filter(Category.id == complaint_in.category_id, Category.is_active == True).first()
    if not category:
        raise BadRequestException("Invalid or inactive category")

    room = db.query(Room).filter(Room.id == complaint_in.location_id).first()
    if not room:
        raise BadRequestException("Invalid location selected")

    priority = complaint_in.priority or PriorityEnum(category.default_priority)
    sla_deadline = calculate_sla_deadline(db, priority)
    complaint_num = generate_complaint_number(db)

    complaint = Complaint(
        complaint_number=complaint_num,
        title=complaint_in.title,
        description=complaint_in.description,
        category_id=complaint_in.category_id,
        location_id=complaint_in.location_id,
        specific_location_details=complaint_in.specific_location_details,
        priority=priority,
        status=ComplaintStatusEnum.OPEN,
        creator_id=creator.id,
        sla_deadline=sla_deadline,
        is_sla_breached=False
    )
    db.add(complaint)
    db.flush()

    # Log initial status history
    history = ComplaintStatusHistory(
        complaint_id=complaint.id,
        previous_status=None,
        new_status=ComplaintStatusEnum.OPEN,
        changed_by_id=creator.id,
        comment="Complaint submitted"
    )
    db.add(history)
    db.commit()
    db.refresh(complaint)
    return complaint

def get_complaint_by_id(db: Session, complaint_id: str, current_user: User) -> Complaint:
    complaint = db.query(Complaint).options(
        joinedload(Complaint.category),
        joinedload(Complaint.location).joinedload(Room.floor).joinedload(Floor.building),
        joinedload(Complaint.creator),
        joinedload(Complaint.assigned_staff),
        joinedload(Complaint.status_history).joinedload(ComplaintStatusHistory.changed_by),
        joinedload(Complaint.assignments).joinedload(ComplaintAssignment.staff),
        joinedload(Complaint.assignments).joinedload(ComplaintAssignment.assigned_by),
        joinedload(Complaint.comments),
        joinedload(Complaint.attachments),
        joinedload(Complaint.rating)
    ).filter(Complaint.id == complaint_id).first()

    if not complaint:
        raise NotFoundException("Complaint not found")

    # Object-Level Authorization
    if current_user.role == UserRole.STUDENT and complaint.creator_id != current_user.id:
        raise PermissionDeniedException("You are not authorized to view this complaint")

    if current_user.role == UserRole.STAFF and complaint.assigned_staff_id != current_user.id:
        # Staff can view if unassigned open complaints or assigned to them
        pass

    return complaint

def update_complaint_status(
    db: Session,
    complaint_id: str,
    status_update: ComplaintUpdateStatus,
    current_user: User
) -> Complaint:
    complaint = get_complaint_by_id(db, complaint_id, current_user)
    current_status = complaint.status
    target_status = status_update.target_status

    if target_status not in ALLOWED_TRANSITIONS.get(current_status, []):
        raise InvalidStateTransitionException(current_status.value, target_status.value)

    # Role specific transition authorization rules
    if current_user.role == UserRole.STUDENT:
        if current_status == ComplaintStatusEnum.RESOLVED and target_status in [ComplaintStatusEnum.CLOSED, ComplaintStatusEnum.REOPENED]:
            pass
        else:
            raise PermissionDeniedException("Students can only mark resolved complaints as CLOSED or REOPENED")

    if current_user.role == UserRole.STAFF:
        if complaint.assigned_staff_id != current_user.id:
            raise PermissionDeniedException("Staff can only update complaints assigned to them")

    # Update Complaint fields
    complaint.status = target_status
    complaint.updated_at = datetime.utcnow()

    if status_update.resolution_notes:
        complaint.resolution_notes = status_update.resolution_notes

    if target_status == ComplaintStatusEnum.RESOLVED:
        complaint.resolved_at = datetime.utcnow()
    elif target_status == ComplaintStatusEnum.CLOSED:
        complaint.closed_at = datetime.utcnow()

    # Log status history
    history = ComplaintStatusHistory(
        complaint_id=complaint.id,
        previous_status=current_status,
        new_status=target_status,
        changed_by_id=current_user.id,
        comment=status_update.comment or status_update.resolution_notes
    )
    db.add(history)

    # In-App Notifications
    if target_status == ComplaintStatusEnum.RESOLVED:
        create_notification(
            db,
            recipient_id=complaint.creator_id,
            title="Complaint Resolved",
            message=f"Your complaint '{complaint.title}' ({complaint.complaint_number}) has been marked as resolved.",
            notification_type="STATUS_CHANGE",
            reference_id=complaint.id
        )
    elif target_status == ComplaintStatusEnum.REOPENED:
        if complaint.assigned_staff_id:
            create_notification(
                db,
                recipient_id=complaint.assigned_staff_id,
                title="Complaint Reopened",
                message=f"Complaint '{complaint.title}' ({complaint.complaint_number}) has been reopened by the student.",
                notification_type="STATUS_CHANGE",
                reference_id=complaint.id
            )

    db.commit()
    db.refresh(complaint)
    return complaint

def filter_complaints(
    db: Session,
    current_user: User,
    status: Optional[ComplaintStatusEnum] = None,
    priority: Optional[PriorityEnum] = None,
    category_id: Optional[str] = None,
    location_id: Optional[str] = None,
    building_id: Optional[str] = None,
    assigned_staff_id: Optional[str] = None,
    creator_id: Optional[str] = None,
    is_sla_breached: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    sort: str = "created_at_desc"
) -> Tuple[List[Complaint], int, int]:
    query = db.query(Complaint).options(
        joinedload(Complaint.category),
        joinedload(Complaint.location).joinedload(Room.floor).joinedload(Floor.building),
        joinedload(Complaint.creator),
        joinedload(Complaint.assigned_staff)
    )

    # Role enforcement
    if current_user.role == UserRole.STUDENT:
        query = query.filter(Complaint.creator_id == current_user.id)
    elif current_user.role == UserRole.STAFF:
        if assigned_staff_id:
            query = query.filter(Complaint.assigned_staff_id == assigned_staff_id)
        else:
            query = query.filter(or_(Complaint.assigned_staff_id == current_user.id, Complaint.status == ComplaintStatusEnum.OPEN))

    # Filters
    if status:
        query = query.filter(Complaint.status == status)
    if priority:
        query = query.filter(Complaint.priority == priority)
    if category_id:
        query = query.filter(Complaint.category_id == category_id)
    if location_id:
        query = query.filter(Complaint.location_id == location_id)
    if building_id:
        query = query.join(Room).join(Floor).join(Building).filter(Building.id == building_id)
    if assigned_staff_id and current_user.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        query = query.filter(Complaint.assigned_staff_id == assigned_staff_id)
    if creator_id and current_user.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        query = query.filter(Complaint.creator_id == creator_id)
    if is_sla_breached is not None:
        query = query.filter(Complaint.is_sla_breached == is_sla_breached)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Complaint.title.like(search_term),
                Complaint.description.like(search_term),
                Complaint.complaint_number.like(search_term)
            )
        )

    # Sorting
    if sort == "created_at_asc":
        query = query.order_by(asc(Complaint.created_at))
    elif sort == "priority_desc":
        query = query.order_by(desc(Complaint.priority))
    elif sort == "sla_deadline_asc":
        query = query.order_by(asc(Complaint.sla_deadline))
    else:
        query = query.order_by(desc(Complaint.created_at))

    total = query.count()
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    return items, total, total_pages
