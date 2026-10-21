import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
from app.core.database import Base

class SLAConfig(Base):
    __tablename__ = "sla_configs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    priority = Column(String(20), nullable=False, unique=True, index=True)  # LOW, MEDIUM, HIGH, CRITICAL
    resolution_time_hours = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
