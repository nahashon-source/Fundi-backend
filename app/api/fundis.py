"""
Fundi routes. Public listing/profile endpoints have no auth requirement
(matches the current open FundiListing/FundiProfile pages). Profile
editing requires the fundi to be logged in as themselves; suspending
requires admin.
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user, require_admin, require_fundi
from app.models.user import User
from app.schemas.fundi import FundiOut, FundiUpdateRequest, FundiSuspendRequest
from app.services.fundi_service import FundiService

router = APIRouter()


@router.get("")
def list_fundis(
    category: Optional[str] = Query(default=None, description="Category slug to filter by"),
    location: Optional[str] = Query(default=None, description="Location substring to filter by"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    fundis = FundiService(db).list_fundis(category, location, skip, limit)
    data = [FundiOut.model_validate(f).model_dump() for f in fundis]
    return {"success": True, "message": "Fundis fetched.", "data": data}


@router.get("/{fundi_id}")
def get_fundi(fundi_id: int, db: Session = Depends(get_db)) -> dict:
    fundi = FundiService(db).get_fundi(fundi_id)
    data = FundiOut.model_validate(fundi).model_dump()
    return {"success": True, "message": "Fundi fetched.", "data": data}


@router.patch("/profile")
def update_own_profile(
    payload: FundiUpdateRequest,
    current_user: User = Depends(require_fundi),
    db: Session = Depends(get_db),
) -> dict:
    fundi = FundiService(db).update_own_profile(current_user.id, payload)
    data = FundiOut.model_validate(fundi).model_dump()
    return {"success": True, "message": "Profile updated.", "data": data}


@router.patch("/{fundi_id}/suspend")
def suspend_fundi(
    fundi_id: int,
    payload: FundiSuspendRequest,
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict:
    fundi = FundiService(db).set_suspended(fundi_id, payload.suspended)
    data = FundiOut.model_validate(fundi).model_dump()
    action = "suspended" if payload.suspended else "reactivated"
    return {"success": True, "message": f"Fundi {action}.", "data": data}