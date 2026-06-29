"""
Reads/writes PlatformSetting key-value rows. Commission rate lives here
so invoice generation always uses the current admin-configured rate,
not a hardcoded constant.
"""
from typing import Optional

from sqlalchemy.orm import Session

from app.models.platform_setting import PlatformSetting

DEFAULT_COMMISSION_RATE = 25.0


class PlatformSettingsService:
    def __init__(self, db: Session):
        self.db = db

    def get_commission_rate(self) -> float:
        setting = self.db.query(PlatformSetting).filter(PlatformSetting.key == "commission_rate").first()
        if setting is None:
            return DEFAULT_COMMISSION_RATE
        return float(setting.value)

    def set_setting(self, key: str, value: str) -> PlatformSetting:
        setting = self.db.query(PlatformSetting).filter(PlatformSetting.key == key).first()
        if setting is None:
            setting = PlatformSetting(key=key, value=value)
            self.db.add(setting)
        else:
            setting.value = value
        self.db.commit()
        self.db.refresh(setting)
        return setting