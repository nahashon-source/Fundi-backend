"""
PlatformSetting — simple key-value store for admin-configurable
platform settings (site name, commission rate, maintenance mode, etc).
Matches the Settings tab already built in AdminDashboard.tsx.
"""
from sqlalchemy import Column, Integer, String

from app.db.session import Base


class PlatformSetting(Base):
    __tablename__ = "platform_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False, index=True)
    value = Column(String, nullable=False)  # stored as string; parsed to bool/float/int in the service layer