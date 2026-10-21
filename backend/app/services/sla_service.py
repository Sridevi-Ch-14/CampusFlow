from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.sla_config import SLAConfig
from app.models.complaint import Complaint, PriorityEnum, ComplaintStatusEnum

DEFAULT_SLA_HOURS = {
    PriorityEnum.LOW: 72,
    PriorityEnum.MEDIUM: 48,
    PriorityEnum.HIGH: 24,
    PriorityEnum.CRITICAL: 4
}

def calculate_sla_deadline(db: Session, priority: PriorityEnum, start_time: datetime = None) -> datetime:
    if start_time is None:
        start_time = datetime.utcnow()
        
    config = db.query(SLAConfig).filter(SLAConfig.priority == priority.value).first()
    hours = config.resolution_time_hours if config else DEFAULT_SLA_HOURS.get(priority, 48)
    return start_time + timedelta(hours=hours)

def check_and_update_sla_breaches(db: Session) -> int:
    """
    Finds open complaints past their SLA deadline and flags them as sla_breached.
    Returns the count of newly breached complaints.
    """
    now = datetime.utcnow()
    unresolved_statuses = [ComplaintStatusEnum.OPEN, ComplaintStatusEnum.ASSIGNED, ComplaintStatusEnum.IN_PROGRESS, ComplaintStatusEnum.REOPENED]
    
    breached_complaints = db.query(Complaint).filter(
        Complaint.status.in_(unresolved_statuses),
        Complaint.sla_deadline < now,
        Complaint.is_sla_breached == False
    ).all()

    count = 0
    for complaint in breached_complaints:
        complaint.is_sla_breached = True
        count += 1
        
    if count > 0:
        db.commit()
        
    return count
