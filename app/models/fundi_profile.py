"""
FundiProfile — extra profile data for users with role=fundi.
`verified` and `suspended` are the two flags the admin dashboard
already manages in the frontend (suspend/reactivate action).
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.db.session import Base


class FundiProfile(Base):
    __tablename__ = "fundi_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    business_name = Column(String, nullable=True)
    bio = Column(String, nullable=True)
    experience_years = Column(Integer, nullable=True)
    hourly_rate = Column(Float, nullable=False, default=0)
    location = Column(String, nullable=True)
    verified = Column(Boolean, default=False, nullable=False)
    suspended = Column(Boolean, default=False, nullable=False)
    rating = Column(Float, default=0.0, nullable=False)
    completed_jobs = Column(Integer, default=0, nullable=False)

    user = relationship("User", back_populates="fundi_profile")
    categories = relationship("FundiCategory", back_populates="fundi")
    assignments = relationship("JobAssignment", back_populates="fundi")
    invoices = relationship("Invoice", back_populates="fundi")
    reviews = relationship("Review", back_populates="fundi")

    @property
    def category_list(self):
        """Returns the actual Category objects this fundi offers,
        unwrapping the FundiCategory join rows."""
        return [fc.category for fc in self.categories]