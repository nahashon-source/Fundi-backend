"""
Fundi business logic. Thin for now -- mostly delegates to the repository --
but this is where rules like "a suspended fundi can't update their profile"
or "only verified fundis appear in search" would go as they're added.
"""
from typing import Optional, List

from sqlalchemy.orm import Session

from app.exceptions import NotFoundException, ForbiddenException
from app.models.fundi_profile import FundiProfile
from app.repositories.fundi_repository import FundiRepository
from app.schemas.fundi import FundiUpdateRequest


class FundiService:
    def __init__(self, db: Session):
        self.repo = FundiRepository(db)

    def list_fundis(
        self, category_slug: Optional[str], location: Optional[str], skip: int, limit: int
    ) -> List[FundiProfile]:
        return self.repo.search(category_slug=category_slug, location=location, skip=skip, limit=limit)

    def get_fundi(self, fundi_id: int) -> FundiProfile:
        fundi = self.repo.get_by_id(fundi_id)
        if fundi is None:
            raise NotFoundException("Fundi not found.")
        return fundi

    def update_own_profile(self, user_id: int, payload: FundiUpdateRequest) -> FundiProfile:
        fundi = self.repo.get_by_user_id(user_id)
        if fundi is None:
            raise NotFoundException("Fundi profile not found for this user.")
        if fundi.suspended:
            raise ForbiddenException("Suspended fundis cannot update their profile.")
        return self.repo.update(fundi, **payload.model_dump(exclude_unset=True))

    def set_suspended(self, fundi_id: int, suspended: bool) -> FundiProfile:
        """Admin-only action -- permission check happens at the route level via require_admin."""
        fundi = self.repo.get_by_id(fundi_id)
        if fundi is None:
            raise NotFoundException("Fundi not found.")
        return self.repo.set_suspended(fundi, suspended)