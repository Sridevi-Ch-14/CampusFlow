import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class ComplaintAssignment(Base):
    __tablename__ = "complaint_assignments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    complaint_id = Column(String(36), ForeignKey("complaints.id", ondelete="CASCADE"), nullable=False, index=True)
    staff_id = Column(String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    assigned_by_id = Column(String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    unassigned_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)

    complaint = relationship("Complaint", back_populates="assignments")
    staff = relationship("User", foreign_keys=[staff_id])
    assigned_by = relationship("User", foreign_keys=[assigned_by_id])
