"""
Schemas for invoice endpoints. Invoice creation is never exposed
directly to the API -- it only happens as a side effect of job
completion confirmation, inside JobService.
"""
from pydantic import BaseModel

from app.models.invoice import InvoiceStatus


class InvoiceOut(BaseModel):
    id: int
    job_id: int
    customer_id: int
    fundi_id: int
    amount: float
    commission_rate: float
    commission_amount: float
    fundi_earnings: float
    status: InvoiceStatus
    invoice_number: str

    class Config:
        from_attributes = True


class InvoiceStatusUpdateRequest(BaseModel):
    status: InvoiceStatus