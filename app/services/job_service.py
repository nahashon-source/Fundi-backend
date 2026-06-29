"""
Job business logic: who can create/view/edit a job, and the rules
around direct-request vs open-posting vs assignment acceptance.
"""
from typing import Optional, List

from sqlalchemy.orm import Session

from app.exceptions import NotFoundException, ForbiddenException, ValidationException
from app.models.job import Job, JobStatus
from app.models.user import User, UserRole
from app.repositories.fundi_repository import FundiRepository
from app.repositories.job_repository import JobRepository
from app.schemas.job import JobCreateRequest, JobUpdateRequest


class JobService:
    def __init__(self, db: Session):
        self.repo = JobRepository(db)
        self.fundi_repo = FundiRepository(db)

    def create_job(self, customer_profile_id: int, payload: JobCreateRequest) -> Job:
        if payload.fundi_id is not None:
            fundi = self.fundi_repo.get_by_id(payload.fundi_id)
            if fundi is None:
                raise NotFoundException("Requested fundi not found.")
            if fundi.suspended:
                raise ValidationException("Cannot request a suspended fundi.")

        job = self.repo.create(
            customer_id=customer_profile_id,
            category_id=payload.category_id,
            title=payload.title,
            description=payload.description,
            location=payload.location,
            budget=payload.budget,
            fundi_id=payload.fundi_id,
            status=JobStatus.PENDING,
        )

        # Direct request: immediately create the assignment so the fundi
        # sees it as "awaiting your response", not just sitting on the job.
        if payload.fundi_id is not None:
            self.repo.create_assignment(job_id=job.id, fundi_id=payload.fundi_id)

        return job

    def get_job(self, job_id: int) -> Job:
        job = self.repo.get_by_id(job_id)
        if job is None:
            raise NotFoundException("Job not found.")
        return job

    def list_jobs(self, current_user: User, customer_profile_id: Optional[int], fundi_profile_id: Optional[int]) -> List[Job]:
        """
        Scoping rule: customers see only their own jobs, fundis see only
        jobs assigned to them or open jobs, admins see everything.
        """
        if current_user.role == UserRole.ADMIN:
            return self.repo.list_all()
        if current_user.role == UserRole.CUSTOMER:
            return self.repo.list_for_customer(customer_profile_id)
        if current_user.role == UserRole.FUNDI:
            return self.repo.list_for_fundi(fundi_profile_id) + self.repo.list_open()
        return []

    def update_job(self, job_id: int, customer_profile_id: int, payload: JobUpdateRequest) -> Job:
        job = self.get_job(job_id)
        if job.customer_id != customer_profile_id:
            raise ForbiddenException("You can only edit your own jobs.")
        return self.repo.update(job, **payload.model_dump(exclude_unset=True))

    def delete_job(self, job_id: int, customer_profile_id: int) -> None:
        job = self.get_job(job_id)
        if job.customer_id != customer_profile_id:
            raise ForbiddenException("You can only delete your own jobs.")
        self.repo.delete(job)

    def assign_fundi(self, job_id: int, fundi_id: int, customer_profile_id: int) -> Job:
        """Customer picks a fundi for an open job (no prior direct request)."""
        job = self.get_job(job_id)
        if job.customer_id != customer_profile_id:
            raise ForbiddenException("You can only assign fundis to your own jobs.")
        if job.fundi_id is not None:
            raise ValidationException("This job is already assigned to a fundi.")

        fundi = self.fundi_repo.get_by_id(fundi_id)
        if fundi is None:
            raise NotFoundException("Fundi not found.")
        if fundi.suspended:
            raise ValidationException("Cannot assign a suspended fundi.")

        self.repo.create_assignment(job_id=job_id, fundi_id=fundi_id)
        return self.repo.update(job, fundi_id=fundi_id)

    def respond_to_assignment(self, job_id: int, fundi_profile_id: int, accepted: bool) -> Job:
        """Fundi accepts or declines a direct request or customer-initiated assignment."""
        assignment = self.repo.get_assignment(job_id, fundi_profile_id)
        if assignment is None:
            raise NotFoundException("Assignment not found.")

        assignment.accepted = accepted
        self.repo.db.commit()

        job = self.get_job(job_id)
        if accepted:
            return self.repo.update(job, status=JobStatus.IN_PROGRESS)
        else:
            # Declined: clear the fundi so the job becomes open again for others.
            return self.repo.update(job, fundi_id=None, status=JobStatus.PENDING)
        
    def mark_done_by_fundi(self, job_id: int, fundi_profile_id: int):
        """Fundi signals work is finished. Doesn't complete the job alone --
        waits on customer confirmation before status changes or an invoice is made."""
        job = self.get_job(job_id)
        if job.fundi_id != fundi_profile_id:
            raise ForbiddenException("You are not assigned to this job.")
        return self.repo.update(job, fundi_marked_done=True)

    def confirm_completion_by_customer(self, job_id: int, customer_profile_id: int):
        """
        Customer confirms the job is genuinely done. This is the single
        trigger point for: job -> completed, invoice generated, fundi's
        completed_jobs counter incremented.
        """
        job = self.get_job(job_id)
        if job.customer_id != customer_profile_id:
            raise ForbiddenException("You can only confirm your own jobs.")
        if not job.fundi_marked_done:
            raise ValidationException("Fundi has not marked this job as done yet.")

        job = self.repo.update(job, status=JobStatus.COMPLETED)

        # Increment the fundi's completed_jobs counter -- small but real
        # business effect of completion, used by FundiOut/profile display.
        from app.repositories.fundi_repository import FundiRepository
        fundi_repo = FundiRepository(self.repo.db)
        fundi = fundi_repo.get_by_id(job.fundi_id)
        fundi_repo.update(fundi, completed_jobs=fundi.completed_jobs + 1)

        from app.services.invoice_service import InvoiceService
        invoice = InvoiceService(self.repo.db).generate_for_job(job)
        return job, invoice
    
    def mark_done_by_fundi(self, job_id: int, fundi_profile_id: int):
        """Fundi signals work is finished. Doesn't complete the job alone --
        waits on customer confirmation before status changes or an invoice is made."""
        job = self.get_job(job_id)
        if job.fundi_id != fundi_profile_id:
            raise ForbiddenException("You are not assigned to this job.")
        return self.repo.update(job, fundi_marked_done=True)

    def confirm_completion_by_customer(self, job_id: int, customer_profile_id: int):
        """
        Customer confirms the job is genuinely done. This is the single
        trigger point for: job -> completed, invoice generated, fundi's
        completed_jobs counter incremented.
        """
        job = self.get_job(job_id)
        if job.customer_id != customer_profile_id:
            raise ForbiddenException("You can only confirm your own jobs.")
        if not job.fundi_marked_done:
            raise ValidationException("Fundi has not marked this job as done yet.")

        job = self.repo.update(job, status=JobStatus.COMPLETED)

        # Increment the fundi's completed_jobs counter -- small but real
        # business effect of completion, used by FundiOut/profile display.
        from app.repositories.fundi_repository import FundiRepository
        fundi_repo = FundiRepository(self.repo.db)
        fundi = fundi_repo.get_by_id(job.fundi_id)
        fundi_repo.update(fundi, completed_jobs=fundi.completed_jobs + 1)

        from app.services.invoice_service import InvoiceService
        invoice = InvoiceService(self.repo.db).generate_for_job(job)
        return job, invoice