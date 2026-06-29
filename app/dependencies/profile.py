"""
Resolves the current user's profile row (CustomerProfile or FundiProfile)
so route handlers don't each have to query for it separately.
"""
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import require_customer, require_fundi
from app.exceptions import NotFoundException
from app.models.customer_profile import CustomerProfile
from app.models.fundi_profile import FundiProfile
from app.models.user import User


def get_current_customer_profile(
    user: User = Depends(require_customer),
    db: Session = Depends(get_db),
) -> CustomerProfile:
    profile = db.query(CustomerProfile).filter(CustomerProfile.user_id == user.id).first()
    if profile is None:
        raise NotFoundException("Customer profile not found.")
    return profile


def get_current_fundi_profile(
    user: User = Depends(require_fundi),
    db: Session = Depends(get_db),
) -> FundiProfile:
    profile = db.query(FundiProfile).filter(FundiProfile.user_id == user.id).first()
    if profile is None:
        raise NotFoundException("Fundi profile not found.")
    return profile