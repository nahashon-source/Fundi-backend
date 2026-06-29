"""
User model — the root identity for every person on the platform.
Role determines which profile table (CustomerProfile / FundiProfile)
applies, and which permissions the JWT-based auth system grants.
"""
import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship

from app.db.session import Base


class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    FUNDI = "fundi"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.CUSTOMER)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # One-to-one: a user is EITHER a customer OR a fundi (enforced at the service layer, not the DB)
    customer_profile = relationship("CustomerProfile", back_populates="user", uselist=False)
    fundi_profile = relationship("FundiProfile", back_populates="user", uselist=False)
    notifications = relationship("Notification", back_populates="user")