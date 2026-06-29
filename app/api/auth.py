"""
Auth routes. Thin by design -- each route only validates the request
shape (via Pydantic), delegates to AuthService, and wraps the result
in the standard {success, message, data} envelope.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserOut
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> dict:
    tokens = AuthService(db).register(payload)
    return {"success": True, "message": "Account created successfully.", "data": tokens.model_dump()}


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> dict:
    tokens = AuthService(db).login(payload)
    return {"success": True, "message": "Login successful.", "data": tokens.model_dump()}


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)) -> dict:
    user_out = UserOut.model_validate(current_user)
    return {"success": True, "message": "Current user fetched.", "data": user_out.model_dump()}