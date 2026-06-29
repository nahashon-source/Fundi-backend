"""
User repository -- the only place that runs SQLAlchemy queries against
the User table. Services call this; this never contains business logic.
"""
from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def create(self, email: str, phone: Optional[str], password_hash: str, role) -> User:
        user = User(email=email, phone=phone, password_hash=password_hash, role=role)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user