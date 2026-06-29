"""
Invoice business logic: commission calculation happens here, once,
at generation time. commission_rate is snapshotted onto the invoice
so it never changes retroactively if the admin updates the platform
rate later.
"""
import uuid
from typing import List

from sqlalchemy.orm import Session

from app.exceptions import NotFoundException, ForbiddenException
from app.models.invoice import Invoice
from app.models.user import User, UserRole
from app.repositories.invoice_repository import InvoiceRepository
from app.services.platform_settings_service import PlatformSettingsService


class InvoiceService:
    def __init__(self, db: Session):
        self.repo = InvoiceRepository(db)
        self.settings_service = PlatformSettingsService(db)

    def generate_for_job(self, job) -> Invoice:
        """Called once, from JobService, the moment a job is confirmed complete."""
        existing = self.repo.get_by_job_id(job.id)
        if existing is not None:
            return existing  # idempotent -- never double-invoice the same job

        commission_rate = self.settings_service.get_commission_rate()
        commission_amount = round(job.budget * (commission_rate / 100), 2)
        fundi_earnings = round(job.budget - commission_amount, 2)
        invoice_number = f"INV-{uuid.uuid4().hex[:8].upper()}"

        return self.repo.create(
            job_id=job.id,
            customer_id=job.customer_id,
            fundi_id=job.fundi_id,
            amount=job.budget,
            commission_rate=commission_rate,
            commission_amount=commission_amount,
            fundi_earnings=fundi_earnings,
            invoice_number=invoice_number,
        )

    def get_invoice(self, invoice_id: int) -> Invoice:
        invoice = self.repo.get_by_id(invoice_id)
        if invoice is None:
            raise NotFoundException("Invoice not found.")
        return invoice

    def list_invoices(self, current_user: User, customer_profile_id, fundi_profile_id) -> List[Invoice]:
        if current_user.role == UserRole.ADMIN:
            return self.repo.list_all()
        if current_user.role == UserRole.CUSTOMER:
            return self.repo.list_for_customer(customer_profile_id)
        if current_user.role == UserRole.FUNDI:
            return self.repo.list_for_fundi(fundi_profile_id)
        return []

    def mark_paid(self, invoice_id: int) -> Invoice:
        from app.models.invoice import InvoiceStatus
        invoice = self.get_invoice(invoice_id)
        return self.repo.update_status(invoice, InvoiceStatus.PAID)