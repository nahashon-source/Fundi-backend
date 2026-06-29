"""
Schemas for category CRUD (admin) and fundi category self-assignment.
"""
from typing import Optional, List

from pydantic import BaseModel


class CategoryOut(BaseModel):
    id: int
    name: str
    slug: str
    icon: Optional[str]

    class Config:
        from_attributes = True


class CategoryCreateRequest(BaseModel):
    name: str
    slug: str
    icon: Optional[str] = None


class FundiCategoryAssignRequest(BaseModel):
    """A fundi sets their full list of offered categories in one call --
    simpler for the frontend than separate add/remove endpoints, and
    matches how a 'select your services' UI naturally submits."""
    category_ids: List[int]