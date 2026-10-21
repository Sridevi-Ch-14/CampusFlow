from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.sla_config import SLAConfig
from app.models.user import User, UserRole
from app.services.auth_service import require_roles
from app.services.sla_service import check_and_update_sla_breaches

router = APIRouter(prefix="/sla", tags=["SLA Management"])

@router.get("/configs")
def list_sla_configs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.SUPER_ADMIN]))
):
    return db.query(SLAConfig).all()

@router.post("/trigger-check")
def trigger_sla_breach_check(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.SUPER_ADMIN]))
):
    breached_count = check_and_update_sla_breaches(db)
    return {"message": "SLA check completed", "newly_breached_count": breached_count}
