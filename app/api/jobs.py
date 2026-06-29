"""
Job routes. Listing is scoped by role inside the service. Creation
requires a customer. Assignment response requires a fundi.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user, require_customer, require_fundi
from app.dependencies.profile import get_current_customer_profile, get_current_fundi_profile
from app.models.customer_profile import CustomerProfile
from app.models.fundi_profile import FundiProfile
from app.models.user import User
from app.schemas.job import (
    JobCreateRequest, JobUpdateRequest, JobOut, JobAssignRequest, AssignmentDecisionRequest,
)
from app.services.job_service import JobService

router = APIRouter()


@router.post("")
def create_job(
    payload: JobCreateRequest,
    customer: CustomerProfile = Depends(get_current_customer_profile),
    db: Session = Depends(get_db),
) -> dict:
    job = JobService(db).create_job(customer.id, payload)
    return {"success": True, "message": "Job posted.", "data": JobOut.model_validate(job).model_dump()}


@router.get("")
def list_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    # Resolve the relevant profile id for scoping, without forcing a specific role dependency
    # (this endpoint is shared across customer/fundi/admin, each scoped differently).
    customer_profile_id = None
    fundi_profile_id = None

    if current_user.role.value == "customer":
        from app.models.customer_profile import CustomerProfile as CP
        profile = db.query(CP).filter(CP.user_id == current_user.id).first()
        customer_profile_id = profile.id if profile else None
    elif current_user.role.value == "fundi":
        from app.models.fundi_profile import FundiProfile as FP
        profile = db.query(FP).filter(FP.user_id == current_user.id).first()
        fundi_profile_id = profile.id if profile else None

    jobs = JobService(db).list_jobs(current_user, customer_profile_id, fundi_profile_id)
    data = [JobOut.model_validate(j).model_dump() for j in jobs]
    return {"success": True, "message": "Jobs fetched.", "data": data}


@router.get("/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db)) -> dict:
    job = JobService(db).get_job(job_id)
    return {"success": True, "message": "Job fetched.", "data": JobOut.model_validate(job).model_dump()}


@router.patch("/{job_id}")
def update_job(
    job_id: int,
    payload: JobUpdateRequest,
    customer: CustomerProfile = Depends(get_current_customer_profile),
    db: Session = Depends(get_db),
) -> dict:
    job = JobService(db).update_job(job_id, customer.id, payload)
    return {"success": True, "message": "Job updated.", "data": JobOut.model_validate(job).model_dump()}


@router.delete("/{job_id}")
def delete_job(
    job_id: int,
    customer: CustomerProfile = Depends(get_current_customer_profile),
    db: Session = Depends(get_db),
) -> dict:
    JobService(db).delete_job(job_id, customer.id)
    return {"success": True, "message": "Job deleted.", "data": None}


@router.post("/{job_id}/assign")
def assign_fundi(
    job_id: int,
    payload: JobAssignRequest,
    customer: CustomerProfile = Depends(get_current_customer_profile),
    db: Session = Depends(get_db),
) -> dict:
    job = JobService(db).assign_fundi(job_id, payload.fundi_id, customer.id)
    return {"success": True, "message": "Fundi assigned.", "data": JobOut.model_validate(job).model_dump()}


@router.post("/{job_id}/respond")
def respond_to_assignment(
    job_id: int,
    payload: AssignmentDecisionRequest,
    fundi: FundiProfile = Depends(get_current_fundi_profile),
    db: Session = Depends(get_db),
) -> dict:
    job = JobService(db).respond_to_assignment(job_id, fundi.id, payload.accepted)
    action = "accepted" if payload.accepted else "declined"
    return {"success": True, "message": f"Job {action}.", "data": JobOut.model_validate(job).model_dump()}

@router.post("/{job_id}/mark-done")
def mark_done(
    job_id: int,
    fundi: FundiProfile = Depends(get_current_fundi_profile),
    db: Session = Depends(get_db),
) -> dict:
    job = JobService(db).mark_done_by_fundi(job_id, fundi.id)
    return {"success": True, "message": "Marked as done. Awaiting customer confirmation.", "data": JobOut.model_validate(job).model_dump()}


@router.post("/{job_id}/confirm-completion")
def confirm_completion(
    job_id: int,
    customer: CustomerProfile = Depends(get_current_customer_profile),
    db: Session = Depends(get_db),
) -> dict:
    job, invoice = JobService(db).confirm_completion_by_customer(job_id, customer.id)
    from app.schemas.invoice import InvoiceOut
    return {
        "success": True,
        "message": "Job completed and invoice generated.",
        "data": {"job": JobOut.model_validate(job).model_dump(), "invoice": InvoiceOut.model_validate(invoice).model_dump()},
    }