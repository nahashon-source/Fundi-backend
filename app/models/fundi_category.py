"""
FundiCategory — many-to-many join table between fundis and categories.
A fundi can offer multiple services (e.g. both Plumbing and Electrical).
"""
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.db.session import Base


class FundiCategory(Base):
    __tablename__ = "fundi_categories"

    fundi_id = Column(Integer, ForeignKey("fundi_profiles.id"), primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id"), primary_key=True)

    fundi = relationship("FundiProfile", back_populates="categories")
    category = relationship("Category", back_populates="fundis")