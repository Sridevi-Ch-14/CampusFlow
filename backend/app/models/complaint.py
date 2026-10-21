import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Enum, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class PriorityEnum(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ComplaintStatusEnum(str, enum.Enum):
    OPEN = "OPEN"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    REJECTED = "REJECTED"
    REOPENED = "REOPENED"

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    complaint_number = Column(String(50), unique=True, nullable=False, index=True)  # e.g., CF-10001
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    
    category_id = Column(String(36), ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False, index=True)
    location_id = Column(String(36), ForeignKey("rooms.id", ondelete="RESTRICT"), nullable=False, index=True)
    specific_location_details = Column(String(255), nullable=True)
    
    priority = Column(Enum(PriorityEnum), nullable=False, default=PriorityEnum.MEDIUM, index=True)
    status = Column(Enum(ComplaintStatusEnum), nullable=False, default=ComplaintStatusEnum.OPEN, index=True)
    
    creator_id = Column(String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    assigned_staff_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    sla_deadline = Column(DateTime, nullable=False, index=True)
    is_sla_breached = Column(Boolean, default=False, nullable=False, index=True)
    
    resolution_notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)

    # Relationships
    category = relationship("Category", back_populates="complaints")
    location = relationship("Room", back_populates="complaints")
    creator = relationship("User", foreign_keys=[creator_id], back_populates="created_complaints")
    assigned_staff = relationship("User", foreign_keys=[assigned_staff_id], back_populates="assigned_complaints")
    
    status_history = relationship("ComplaintStatusHistory", back_populates="complaint", cascade="all, delete-orphan", order_by="ComplaintStatusHistory.created_at.asc()")
    assignments = relationship("ComplaintAssignment", back_populates="complaint", cascade="all, delete-orphan", order_by="ComplaintAssignment.assigned_at.desc()")
    comments = relationship("ComplaintComment", back_populates="complaint", cascade="all, delete-orphan", order_by="ComplaintComment.created_at.asc()")
    attachments = relationship("ComplaintAttachment", back_populates="complaint", cascade="all, delete-orphan")
    rating = relationship("Rating", back_populates="complaint", uselist=False, cascade="all, delete-orphan")
