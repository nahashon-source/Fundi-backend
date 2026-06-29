"""
Category business logic: uniqueness rules for admin-created categories,
and validation that a fundi can't assign themselves to a category
that doesn't exist.
"""
from typing import List

from sqlalchemy.orm import Session

from app.exceptions import ConflictException, NotFoundException
from app.models.category import Category
from app.repositories.category_repository import CategoryRepository
from app.repositories.fundi_repository import FundiRepository
from app.schemas.category import CategoryCreateRequest


class CategoryService:
    def __init__(self, db: Session):
        self.repo = CategoryRepository(db)
        self.fundi_repo = FundiRepository(db)

    def list_categories(self) -> List[Category]:
        return self.repo.list_all()

    def create_category(self, payload: CategoryCreateRequest) -> Category:
        if self.repo.get_by_slug(payload.slug):
            raise ConflictException(f"A category with slug '{payload.slug}' already exists.")
        return self.repo.create(payload.name, payload.slug, payload.icon)

    def assign_fundi_categories(self, user_id: int, category_ids: List[int]) -> None:
        fundi = self.fundi_repo.get_by_user_id(user_id)
        if fundi is None:
            raise NotFoundException("Fundi profile not found for this user.")

        for cat_id in category_ids:
            if self.repo.get_by_id(cat_id) is None:
                raise NotFoundException(f"Category with id {cat_id} does not exist.")

        self.repo.set_fundi_categories(fundi.id, category_ids)