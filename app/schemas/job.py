"""
Schemas for job posting, listing, and assignment.
"""
from typing import Optional, List

from pydantic import BaseModel, Field

from app.models.job import JobStatus


class JobCreateRequest(BaseModel):
    category_id: int
    title: str
    description: str
    location: str
    budget: float = Field(gt=0)
    fundi_id: Optional[int] = None  # direct request if provided, open posting if None


class JobUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    budget: Optional[float] = Field(default=None, gt=0)
    status: Optional[JobStatus] = None


class JobOut(BaseModel):
    id: int
    customer_id: int
    category_id: int
    title: str
    description: str
    location: str
    budget: float
    status: JobStatus

    class Config:
        from_attributes = True


class JobAssignRequest(BaseModel):
    fundi_id: int


class JobAssignmentOut(BaseModel):
    id: int
    job_id: int
    fundi_id: int
    accepted: Optional[bool]

    class Config:
        from_attributes = True


class AssignmentDecisionRequest(BaseModel):
    accepted: bool
    
class MarkDoneResponse(BaseModel):
    id: int
    fundi_marked_done: bool

    class Config:
        from_attributes = True