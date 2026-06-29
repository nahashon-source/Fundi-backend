"""
Category repository -- direct DB access for Category and the
FundiCategory join table.
"""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.fundi_category import FundiCategory


class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_all(self) -> List[Category]:
        return self.db.query(Category).all()

    def get_by_id(self, category_id: int) -> Optional[Category]:
        return self.db.query(Category).filter(Category.id == category_id).first()

    def get_by_slug(self, slug: str) -> Optional[Category]:
        return self.db.query(Category).filter(Category.slug == slug).first()

    def create(self, name: str, slug: str, icon: Optional[str]) -> Category:
        category = Category(name=name, slug=slug, icon=icon)
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def count_fundis_in_category(self, category_id: int) -> int:
        return self.db.query(FundiCategory).filter(FundiCategory.category_id == category_id).count()

    def set_fundi_categories(self, fundi_id: int, category_ids: List[int]) -> None:
        """Replaces a fundi's full category list -- delete existing links, insert the new set."""
        self.db.query(FundiCategory).filter(FundiCategory.fundi_id == fundi_id).delete()
        for cat_id in category_ids:
            self.db.add(FundiCategory(fundi_id=fundi_id, category_id=cat_id))
        self.db.commit()