from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.models.complaint import Complaint, ComplaintStatusEnum, PriorityEnum
from app.models.category import Category
from app.models.location import Room, Floor, Building
from app.models.user import User, UserRole
from app.schemas.analytics import (
    AnalyticsKPIResponse,
    AnalyticsDashboardResponse,
    CategoryDistributionItem,
    LocationDistributionItem,
    PriorityDistributionItem,
    StaffWorkloadItem
)

def get_analytics_dashboard(db: Session) -> AnalyticsDashboardResponse:
    total_complaints = db.query(Complaint).count()
    open_complaints = db.query(Complaint).filter(Complaint.status == ComplaintStatusEnum.OPEN).count()
    assigned_complaints = db.query(Complaint).filter(Complaint.status == ComplaintStatusEnum.ASSIGNED).count()
    in_progress_complaints = db.query(Complaint).filter(Complaint.status == ComplaintStatusEnum.IN_PROGRESS).count()
    resolved_complaints = db.query(Complaint).filter(Complaint.status == ComplaintStatusEnum.RESOLVED).count()
    closed_complaints = db.query(Complaint).filter(Complaint.status == ComplaintStatusEnum.CLOSED).count()
    rejected_complaints = db.query(Complaint).filter(Complaint.status == ComplaintStatusEnum.REJECTED).count()
    sla_breached_complaints = db.query(Complaint).filter(Complaint.is_sla_breached == True).count()

    resolved_items = db.query(Complaint).filter(Complaint.resolved_at != None).all()
    if resolved_items:
        total_hours = sum((c.resolved_at - c.created_at).total_seconds() / 3600.0 for c in resolved_items)
        avg_resolution_time = round(total_hours / len(resolved_items), 2)
    else:
        avg_resolution_time = 0.0

    completed_total = resolved_complaints + closed_complaints
    resolution_rate = round((completed_total / total_complaints * 100.0), 2) if total_complaints > 0 else 0.0

    kpi = AnalyticsKPIResponse(
        total_complaints=total_complaints,
        open_complaints=open_complaints,
        assigned_complaints=assigned_complaints,
        in_progress_complaints=in_progress_complaints,
        resolved_complaints=resolved_complaints,
        closed_complaints=closed_complaints,
        rejected_complaints=rejected_complaints,
        sla_breached_complaints=sla_breached_complaints,
        avg_resolution_time_hours=avg_resolution_time,
        resolution_rate_percent=resolution_rate
    )

    # Category distribution
    cat_query = db.query(Category.name, func.count(Complaint.id)).join(
        Complaint, Category.id == Complaint.category_id, isouter=True
    ).group_by(Category.id, Category.name).all()
    by_category = [CategoryDistributionItem(category_name=name, count=count) for name, count in cat_query]

    # Location (Building) distribution
    loc_query = db.query(Building.name, func.count(Complaint.id)).join(
        Floor, Building.id == Floor.building_id
    ).join(
        Room, Floor.id == Room.floor_id
    ).join(
        Complaint, Room.id == Complaint.location_id
    ).group_by(Building.id, Building.name).all()
    by_location = [LocationDistributionItem(building_name=name, count=count) for name, count in loc_query]

    # Priority distribution
    prio_query = db.query(Complaint.priority, func.count(Complaint.id)).group_by(Complaint.priority).all()
    by_priority = [PriorityDistributionItem(priority=p.value if hasattr(p, 'value') else str(p), count=count) for p, count in prio_query]

    # Staff Workload
    staff_members = db.query(User).filter(User.role == UserRole.STAFF, User.is_active == True).all()
    staff_workload = []
    for staff in staff_members:
        assigned_c = db.query(Complaint).filter(Complaint.assigned_staff_id == staff.id, Complaint.status == ComplaintStatusEnum.ASSIGNED).count()
        in_prog_c = db.query(Complaint).filter(Complaint.assigned_staff_id == staff.id, Complaint.status == ComplaintStatusEnum.IN_PROGRESS).count()
        res_c = db.query(Complaint).filter(Complaint.assigned_staff_id == staff.id, Complaint.status.in_([ComplaintStatusEnum.RESOLVED, ComplaintStatusEnum.CLOSED])).count()
        staff_workload.append(
            StaffWorkloadItem(
                staff_id=staff.id,
                staff_name=staff.full_name,
                assigned_count=assigned_c,
                in_progress_count=in_prog_c,
                resolved_count=res_c
            )
        )

    return AnalyticsDashboardResponse(
        kpi=kpi,
        by_category=by_category,
        by_location=by_location,
        by_priority=by_priority,
        staff_workload=staff_workload
    )
