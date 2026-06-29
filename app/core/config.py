"""
Application configuration, loaded from environment variables.

Uses pydantic-settings so every config value is type-checked at startup —
if DATABASE_URL or SECRET_KEY is missing, the app fails fast with a clear
error instead of crashing later mid-request.
"""
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- App ---
    app_name: str = "FundiHub API"
    environment: str = "development"
    debug: bool = True

    # --- Database ---
    database_url: str

    # --- JWT ---
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # --- CORS ---
    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    @property
    def cors_origins_list(self) -> List[str]:
        """Splits the comma-separated CORS_ORIGINS env var into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


# Single shared instance, imported everywhere config is needed.
settings = Settings()