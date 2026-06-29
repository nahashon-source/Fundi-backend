"""
Pydantic schemas for fundi-related endpoints.
FundiOut never exposes user.password_hash or other internal fields --
it's built explicitly from FundiProfile + the linked User's public fields.
"""
from typing import Optional, List

from pydantic import BaseModel, Field


class CategoryOut(BaseModel):
    id: int
    name: str
    slug: str
    icon: Optional[str]

    class Config:
        from_attributes = True


class FundiOut(BaseModel):
    id: int
    user_id: int
    business_name: Optional[str]
    bio: Optional[str]
    experience_years: Optional[int]
    hourly_rate: float
    location: Optional[str]
    verified: bool
    suspended: bool
    rating: float
    completed_jobs: int
    categories: List[CategoryOut] = Field(default=[], validation_alias="category_list")

    class Config:
        from_attributes = True
        populate_by_name = True

class FundiUpdateRequest(BaseModel):
    """Fields a fundi can edit on their own profile."""
    business_name: Optional[str] = None
    bio: Optional[str] = None
    experience_years: Optional[int] = Field(default=None, ge=0)
    hourly_rate: Optional[float] = Field(default=None, ge=0)
    location: Optional[str] = None


class FundiSuspendRequest(BaseModel):
    suspended: bool