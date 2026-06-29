"""
Review — a customer's rating/comment on a completed job.
One review per job (enforced via unique job_id), matching the
frontend's RatingStars usage on fundi profiles.
"""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.session import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customer_profiles.id"), nullable=False)
    fundi_id = Column(Integer, ForeignKey("fundi_profiles.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5, validated in the Pydantic schema layer
    comment = Column(String, nullable=True)

    job = relationship("Job", back_populates="review")
    customer = relationship("CustomerProfile")
    fundi = relationship("FundiProfile", back_populates="reviews")