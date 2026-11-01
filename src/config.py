import os

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_ENV: str = "dev"
    ECOMMERCE_API_BASE_URL: str = ""

    model_config = SettingsConfigDict(
        env_file=f".env.{os.getenv('APP_ENV', 'dev')}",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached Settings singleton.

    The @lru_cache ensures Settings() is only instantiated once per process,
    regardless of how many routes or modules call get_settings().
    Use FastAPI's Depends(get_settings) to inject it into routes.
    """
    return Settings()