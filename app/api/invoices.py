"""
Invoice routes. Listing is scoped by role. Marking paid is admin-only
for now -- real payment integration (M-Pesa, Stripe, etc.) would
trigger this automatically later, but that's a separate module.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user, require_admin
from app.models.user import User
from app.schemas.invoice import InvoiceOut
from app.services.invoice_service import InvoiceService

router = APIRouter()


@router.get("")
def list_invoices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    customer_profile_id = None
    fundi_profile_id = None

    if current_user.role.value == "customer":
        from app.models.customer_profile import CustomerProfile
        profile = db.query(CustomerProfile).filter(CustomerProfile.user_id == current_user.id).first()
        customer_profile_id = profile.id if profile else None
    elif current_user.role.value == "fundi":
        from app.models.fundi_profile import FundiProfile
        profile = db.query(FundiProfile).filter(FundiProfile.user_id == current_user.id).first()
        fundi_profile_id = profile.id if profile else None

    invoices = InvoiceService(db).list_invoices(current_user, customer_profile_id, fundi_profile_id)
    data = [InvoiceOut.model_validate(i).model_dump() for i in invoices]
    return {"success": True, "message": "Invoices fetched.", "data": data}


@router.get("/{invoice_id}")
def get_invoice(invoice_id: int, db: Session = Depends(get_db)) -> dict:
    invoice = InvoiceService(db).get_invoice(invoice_id)
    return {"success": True, "message": "Invoice fetched.", "data": InvoiceOut.model_validate(invoice).model_dump()}


@router.patch("/{invoice_id}/mark-paid")
def mark_paid(
    invoice_id: int,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    invoice = InvoiceService(db).mark_paid(invoice_id)
    return {"success": True, "message": "Invoice marked as paid.", "data": InvoiceOut.model_validate(invoice).model_dump()}