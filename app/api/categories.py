"""
Category routes. Listing is public (matches the frontend's open
category filter chips). Creating categories is admin-only. Fundis
assign themselves to existing categories via their own endpoint.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import require_admin, require_fundi
from app.models.user import User
from app.schemas.category import CategoryOut, CategoryCreateRequest, FundiCategoryAssignRequest
from app.services.category_service import CategoryService

router = APIRouter()


@router.get("")
def list_categories(db: Session = Depends(get_db)) -> dict:
    categories = CategoryService(db).list_categories()
    data = [CategoryOut.model_validate(c).model_dump() for c in categories]
    return {"success": True, "message": "Categories fetched.", "data": data}


@router.post("")
def create_category(
    payload: CategoryCreateRequest,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    category = CategoryService(db).create_category(payload)
    data = CategoryOut.model_validate(category).model_dump()
    return {"success": True, "message": "Category created.", "data": data}


@router.put("/fundi/categories")
def assign_fundi_categories(
    payload: FundiCategoryAssignRequest,
    current_user: User = Depends(require_fundi),
    db: Session = Depends(get_db),
) -> dict:
    CategoryService(db).assign_fundi_categories(current_user.id, payload.category_ids)
    return {"success": True, "message": "Categories updated.", "data": None}