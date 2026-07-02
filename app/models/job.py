"""
Job — a customer's service request. This is the central entity that
JobAssignment, Invoice, and Review all hang off of.
"""
import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship

from app.db.session import Base


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customer_profiles.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    location = Column(String, nullable=False)
    budget = Column(Float, nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    fundi_id = Column(Integer, ForeignKey("fundi_profiles.id"), nullable=True)
    fundi_marked_done = Column(Boolean, default=False, nullable=False)

    customer = relationship("CustomerProfile", back_populates="jobs")
    category = relationship("Category", back_populates="jobs")
    assignments = relationship("JobAssignment", back_populates="job")
    invoice = relationship("Invoice", back_populates="job", uselist=False)
    review = relationship("Review", back_populates="job", uselist=False)