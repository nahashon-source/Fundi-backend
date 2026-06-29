"""
Reusable FastAPI dependencies for authentication and role-based access.
Routes declare who's allowed to call them just by listing these in
their signature -- no manual role checks scattered through route bodies.
"""
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import get_db
from app.exceptions import UnauthorizedException, ForbiddenException
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Decodes the bearer token and loads the corresponding User row."""
    try:
        payload = decode_token(token)
    except JWTError:
        raise UnauthorizedException("Invalid or expired token.")

    if payload.get("type") != "access":
        raise UnauthorizedException("Invalid token type -- use an access token.")

    user_id = payload.get("sub")
    user = UserRepository(db).get_by_id(int(user_id))
    if user is None or not user.is_active:
        raise UnauthorizedException("User not found or inactive.")

    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.ADMIN:
        raise ForbiddenException("Admin access required.")
    return user


def require_customer(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.CUSTOMER:
        raise ForbiddenException("Customer access required.")
    return user


def require_fundi(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.FUNDI:
        raise ForbiddenException("Fundi access required.")
    return user