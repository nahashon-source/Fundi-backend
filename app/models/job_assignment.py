"""
JobAssignment — links a fundi to a job they've been offered/accepted.
Separated from Job itself so a job's assignment history is trackable
(e.g. if a fundi declines, another can be assigned without losing the record).
"""
from datetime import datetime

from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.session import Base


class JobAssignment(Base):
    __tablename__ = "job_assignments"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    fundi_id = Column(Integer, ForeignKey("fundi_profiles.id"), nullable=False)
    accepted = Column(Boolean, nullable=True)  # null = pending response, True/False once decided
    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    job = relationship("Job", back_populates="assignments")
    fundi = relationship("FundiProfile", back_populates="assignments")