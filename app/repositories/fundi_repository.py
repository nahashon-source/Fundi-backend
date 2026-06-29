"""
Fundi repository -- all direct DB queries for FundiProfile.
Search/filter logic lives here (query building), not in the service,
since this is purely "how do I fetch rows", not a business rule.
"""
from typing import Optional, List

from sqlalchemy.orm import Session, joinedload

from app.models.fundi_profile import FundiProfile
from app.models.fundi_category import FundiCategory


class FundiRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, fundi_id: int) -> Optional[FundiProfile]:
        return (
            self.db.query(FundiProfile)
            .options(joinedload(FundiProfile.categories).joinedload(FundiCategory.category))
            .filter(FundiProfile.id == fundi_id)
            .first()
        )

    def get_by_user_id(self, user_id: int) -> Optional[FundiProfile]:
        return self.db.query(FundiProfile).filter(FundiProfile.user_id == user_id).first()

    def search(
        self,
        category_slug: Optional[str] = None,
        location: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[FundiProfile]:
        """
        Returns active (non-suspended) fundis only -- suspended fundis
        must never appear in public search results, regardless of filters.
        """
        query = (
            self.db.query(FundiProfile)
            .options(joinedload(FundiProfile.categories).joinedload(FundiCategory.category))
            .filter(FundiProfile.suspended.is_(False))
        )

        if location:
            query = query.filter(FundiProfile.location.ilike(f"%{location}%"))

        if category_slug:
            query = query.join(FundiCategory).join(FundiCategory.category).filter(
                FundiCategory.category.has(slug=category_slug)
            )

        return query.offset(skip).limit(limit).all()

    def update(self, fundi: FundiProfile, **fields) -> FundiProfile:
        for key, value in fields.items():
            if value is not None:
                setattr(fundi, key, value)
        self.db.commit()
        self.db.refresh(fundi)
        return fundi

    def set_suspended(self, fundi: FundiProfile, suspended: bool) -> FundiProfile:
        fundi.suspended = suspended
        self.db.commit()
        self.db.refresh(fundi)
        return fundi