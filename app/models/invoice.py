"""
Invoice — generated once a job is completed. Commission calculation
(commission_rate -> commission_amount -> fundi_earnings) happens in the
service layer, never recalculated ad-hoc in the frontend or here in the model.
"""
import enum

from sqlalchemy import Column, Integer, Float, String, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.db.session import Base


class InvoiceStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customer_profiles.id"), nullable=False)
    fundi_id = Column(Integer, ForeignKey("fundi_profiles.id"), nullable=False)
    amount = Column(Float, nullable=False)
    commission_rate = Column(Float, nullable=False)  # percent, e.g. 25.0 — snapshot at invoice time
    commission_amount = Column(Float, nullable=False)
    fundi_earnings = Column(Float, nullable=False)
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.PENDING, nullable=False)
    invoice_number = Column(String, unique=True, nullable=False)

    job = relationship("Job", back_populates="invoice")
    customer = relationship("CustomerProfile")
    fundi = relationship("FundiProfile", back_populates="invoices")