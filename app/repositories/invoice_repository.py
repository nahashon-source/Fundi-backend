"""
Invoice repository -- direct DB access for Invoice rows.
"""
from typing import Optional, List

from sqlalchemy.orm import Session

from app.models.invoice import Invoice


class InvoiceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **fields) -> Invoice:
        invoice = Invoice(**fields)
        self.db.add(invoice)
        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    def get_by_id(self, invoice_id: int) -> Optional[Invoice]:
        return self.db.query(Invoice).filter(Invoice.id == invoice_id).first()

    def get_by_job_id(self, job_id: int) -> Optional[Invoice]:
        return self.db.query(Invoice).filter(Invoice.job_id == job_id).first()

    def list_for_customer(self, customer_id: int) -> List[Invoice]:
        return self.db.query(Invoice).filter(Invoice.customer_id == customer_id).all()

    def list_for_fundi(self, fundi_id: int) -> List[Invoice]:
        return self.db.query(Invoice).filter(Invoice.fundi_id == fundi_id).all()

    def list_all(self) -> List[Invoice]:
        return self.db.query(Invoice).all()

    def update_status(self, invoice: Invoice, status) -> Invoice:
        invoice.status = status
        self.db.commit()
        self.db.refresh(invoice)
        return invoice