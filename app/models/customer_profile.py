"""
CustomerProfile — extra profile data for users with role=customer.
Kept separate from User so the core auth table stays lean and
role-agnostic; profile fields only get added here, not on User.
"""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.session import Base


class CustomerProfile(Base):
    __tablename__ = "customer_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    full_name = Column(String, nullable=False)
    county = Column(String, nullable=True)
    avatar = Column(String, nullable=True)  # URL to avatar image

    user = relationship("User", back_populates="customer_profile")
    jobs = relationship("Job", back_populates="customer")