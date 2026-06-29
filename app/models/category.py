"""
Category — service categories (Plumbing, Electrical, Painting, etc.)
Matches the `categories` array already used in mock.ts on the frontend.
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.session import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False, index=True)
    icon = Column(String, nullable=True)  # icon name, matches frontend's iconMap keys

    fundis = relationship("FundiCategory", back_populates="category")
    jobs = relationship("Job", back_populates="category")