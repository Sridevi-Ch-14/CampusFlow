from datetime import datetime
from sqlalchemy.orm import Session
from app.models.complaint import Complaint, ComplaintStatusEnum
from app.models.assignment import ComplaintAssignment
from app.models.status_history import ComplaintStatusHistory
from app.models.user import User, UserRole
from app.services.notification_service import create_notification
from app.core.exceptions import NotFoundException, BadRequestException, PermissionDeniedException

def assign_complaint_to_staff(
    db: Session,
    complaint_id: str,
    staff_id: str,
    assigned_by: User,
    notes: str = None
) -> Complaint:
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise NotFoundException("Complaint not found")

    staff = db.query(User).filter(User.id == staff_id, User.role == UserRole.STAFF, User.is_active == True).first()
    if not staff:
        raise BadRequestException("Selected user is not active maintenance staff")

    previous_status = complaint.status

    # Unassign active assignment if re-assigning
    active_assignment = db.query(ComplaintAssignment).filter(
        ComplaintAssignment.complaint_id == complaint_id,
        ComplaintAssignment.unassigned_at == None
    ).first()

    if active_assignment:
        active_assignment.unassigned_at = datetime.utcnow()

    # Create new assignment record
    new_assignment = ComplaintAssignment(
        complaint_id=complaint_id,
        staff_id=staff_id,
        assigned_by_id=assigned_by.id,
        notes=notes
    )
    db.add(new_assignment)

    # Update Complaint status & assigned staff
    complaint.assigned_staff_id = staff_id
    if complaint.status == ComplaintStatusEnum.OPEN or complaint.status == ComplaintStatusEnum.REOPENED:
        complaint.status = ComplaintStatusEnum.ASSIGNED

    complaint.updated_at = datetime.utcnow()

    # Log status history if status changed
    if complaint.status != previous_status:
        history = ComplaintStatusHistory(
            complaint_id=complaint.id,
            previous_status=previous_status,
            new_status=complaint.status,
            changed_by_id=assigned_by.id,
            comment=f"Assigned to staff: {staff.full_name}"
        )
        db.add(history)

    # Notify staff member
    create_notification(
        db,
        recipient_id=staff_id,
        title="New Complaint Assignment",
        message=f"You have been assigned complaint '{complaint.title}' ({complaint.complaint_number}).",
        notification_type="ASSIGNMENT",
        reference_id=complaint.id
    )

    db.commit()
    db.refresh(complaint)
    return complaint
