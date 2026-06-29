"""
Job repository -- direct DB access for Job and JobAssignment.
"""
from typing import Optional, List

from sqlalchemy.orm import Session

from app.models.job import Job, JobStatus
from app.models.job_assignment import JobAssignment


class JobRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **fields) -> Job:
        job = Job(**fields)
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get_by_id(self, job_id: int) -> Optional[Job]:
        return self.db.query(Job).filter(Job.id == job_id).first()

    def list_for_customer(self, customer_id: int) -> List[Job]:
        return self.db.query(Job).filter(Job.customer_id == customer_id).all()

    def list_for_fundi(self, fundi_id: int) -> List[Job]:
        """Jobs directly assigned to this fundi -- via Job.fundi_id (direct request)
        or via an existing JobAssignment row (came through open-posting + assign)."""
        direct = self.db.query(Job).filter(Job.fundi_id == fundi_id)
        via_assignment = (
            self.db.query(Job)
            .join(JobAssignment)
            .filter(JobAssignment.fundi_id == fundi_id)
        )
        return direct.union(via_assignment).all()

    def list_open(self) -> List[Job]:
        """Open jobs with no fundi attached yet -- what fundis browse to apply for."""
        return self.db.query(Job).filter(Job.fundi_id.is_(None), Job.status == JobStatus.PENDING).all()

    def list_all(self) -> List[Job]:
        """Admin-only: every job regardless of status or assignment."""
        return self.db.query(Job).all()

    def update(self, job: Job, **fields) -> Job:
        for key, value in fields.items():
            if value is not None:
                setattr(job, key, value)
        self.db.commit()
        self.db.refresh(job)
        return job

    def delete(self, job: Job) -> None:
        self.db.delete(job)
        self.db.commit()

    def create_assignment(self, job_id: int, fundi_id: int) -> JobAssignment:
        assignment = JobAssignment(job_id=job_id, fundi_id=fundi_id, accepted=None)
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)
        return assignment

    def get_assignment(self, job_id: int, fundi_id: int) -> Optional[JobAssignment]:
        return (
            self.db.query(JobAssignment)
            .filter(JobAssignment.job_id == job_id, JobAssignment.fundi_id == fundi_id)
            .first()
        )